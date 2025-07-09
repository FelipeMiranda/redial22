import os
import signal
import typing

import urwid
from redial22.config import Config
from redial22.hostinfo import HostInfo
from redial22.tree.node import Node
from redial22.ui.dialog import AddHostDialog, MessageDialog, AddFolderDialog, RemoveHostDialog, CopySSHKeyDialog, RemoveFolderDialog
from redial22.ui.footer import init_footer
from redial22.ui.tree import UIParentNode, UITreeWidget, UITreeNode, UITreeListBox, State
from redial22.ui.palette import palette
from redial22.utils import package_available, get_public_ssh_keys
from redial22.uistate import save_ui_state, restore_ui_state
from functools import partial


class RedialApplication:

    def __init__(self, root_folder=None):
        self.sessions = Config().load_from_file()
        if root_folder is not None:
            self.root = root_folder
        else:
            self.root = self.sessions

        top_node = UIParentNode(self.root, key_handler=self.on_key_press)
        self.walker = urwid.TreeWalker(top_node)
        self.listbox = UITreeListBox(self.walker)

        restore_ui_state(self.listbox, self.sessions)

        self.header_text = urwid.Text("redial22")
        urwid.connect_signal(self.walker, "modified", lambda: on_focus_change(self.listbox))
        footer = init_footer(self.listbox)

        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(self.header_text, 'head'),
            footer=footer)

        # Set screen to 256 color mode
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)
        self.loop = urwid.MainLoop(self.view, palette, screen)

        # instance attributes
        self.command = None
        self.command_return_key = None  # type: int | None
        self.log = None
        self.search_string = ""
        self.in_search_mode = False

    def reset_search(self):
        self.search_string = ""
        self.in_search_mode = False
        self.header_text.set_text("redial22")

    def search_and_focus(self, search_string):
        # Traverse all nodes and focus the first match
        def traverse(node, parent_path=None):
            if parent_path is None:
                parent_path = []
            results = []
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    results.extend(traverse(child, parent_path + [node]))
            results.append((node, parent_path))
            return results
        all_nodes = traverse(self.sessions)
        search_lower = search_string.lower()
        for node, parent_path in all_nodes:
            name = getattr(node, 'name', '') or ''
            nodetype = getattr(node, 'nodetype', '') or ''
            ip = getattr(getattr(node, 'hostinfo', None), 'ip', '') or ''
            if search_lower in name.lower() or search_lower in ip.lower():
                # Expand all parent folders by iterating through visible widgets
                for parent in parent_path:
                    if hasattr(parent, 'nodetype') and parent.nodetype == 'folder':
                        widget = None
                        if hasattr(parent, 'get_widget'):
                            widget = parent.get_widget()
                        if widget is not None and hasattr(widget, 'expanded'):
                            widget.expanded = True
                            widget.update_expanded_icon()
                self.listbox.set_focus_to_node(node)
                break

    def run(self):
        if self.command_return_key == 0 and self.log is not None:
            MessageDialog("Info", self.log, self.close_dialog).show(self.loop)
            self.log = None
        self.loop.run()

    def on_key_press(self, key: str, w: UITreeWidget):
        # Enter search mode with '/'
        if not self.in_search_mode and key == '/':
            self.in_search_mode = True
            self.search_string = ""
            self.header_text.set_text("Search: ")
            return

        # Handle search mode
        if self.in_search_mode:
            if key == 'esc' or key == 'enter':
                self.reset_search()
                return
            elif key == 'backspace':
                self.search_string = self.search_string[:-1]
            elif len(key) == 1 and (key.isprintable()):
                self.search_string += key
            # Update header and focus
            self.header_text.set_text(f"Search: {self.search_string}")
            self.search_and_focus(self.search_string)
            return

        # Handle reserved command keys (only when not in search mode)
        if key in ['q', 'Q', 'ctrl d']:
            self.command = EXIT_REDIAL
            raise urwid.ExitMainLoop()

        this_node = w.get_node().get_value()
        folder_node = this_node if (w.get_node().get_parent() is None or this_node.nodetype == "folder") \
            else w.get_node().get_parent().get_value()

        parent_node = None if w.get_node().get_parent() is None else w.get_node().get_parent().get_value()

        if key == "enter":
            if isinstance(w.get_node(), UITreeNode):
                self.command = w.get_node().get_value().hostinfo.get_ssh_command()
                raise urwid.ExitMainLoop()

        elif key == "f3" and w.is_leaf:
            if (len(get_public_ssh_keys())) == 0:
                MessageDialog("Error",
                              "There is no public SSH Key (.pub) in ~/.ssh folder. You can use ssh-keygen to "
                              "generate SSH key pairs",
                              self.close_dialog).show(
                    self.loop)
            else:
                self.log = "SSH key is copied successfully"
                CopySSHKeyDialog(this_node, self.close_dialog_and_run, self.change_log).show(self.loop)

        elif key == "f5" and w.is_leaf:
            if package_available(package_name="mc"):
                self.command = this_node.hostinfo.get_mc_command()
                raise urwid.ExitMainLoop()
            else:
                MessageDialog("Error", "Please install mc (Midnight Commander) package"
                                       " to use this feature", self.close_dialog).show(self.loop)

        elif key == "f6":
            AddFolderDialog(folder_node, Node("", "folder"), self.save_and_focus).show(self.loop)

        elif key == "f7":
            AddHostDialog(folder_node, Node("", "session", HostInfo("")), self.save_and_focus).show(self.loop)

        elif key == "f8":
            if parent_node is None:
                MessageDialog("Error", "Root folder cannot be removed", self.close_dialog).show(self.loop)
            else:
                parent_node_typed = typing.cast(Node, parent_node)
                if this_node.nodetype == "folder":
                    RemoveFolderDialog(parent_node_typed, this_node, self.save_and_focus).show(self.loop)
                else:
                    RemoveHostDialog(parent_node_typed, this_node, self.save_and_focus).show(self.loop)

        elif key == "f9" and w.is_leaf:
            AddHostDialog(parent_node, this_node, self.save_and_focus).show(self.loop)

        elif key in ["meta down", "ctrl down"]:
            if parent_node is None: return
            i = parent_node.children.index(this_node)
            if i == len(parent_node.children) - 1: return  # at bottom
            parent_node.children[i], parent_node.children[i + 1] = parent_node.children[i + 1], parent_node.children[i]

            self.save_and_focus(this_node)

        elif key in ["meta up", "ctrl up"]:
            if parent_node is None: return
            i = parent_node.children.index(this_node)
            if i == 0: return  # at top
            parent_node.children[i], parent_node.children[i - 1] = parent_node.children[i - 1], parent_node.children[i]

            self.save_and_focus(this_node)
        else:
            return key

    def save_and_focus(self, focus: Node):
        save_ui_state(self.listbox)
        Config().save_to_file(self.sessions)
        self.walker.set_focus(UIParentNode(self.sessions, key_handler=self.on_key_press))
        self.listbox.set_focus_to_node(focus)
        restore_ui_state(self.listbox, self.sessions)
        self.loop.widget = self.view

    def close_dialog(self):
        self.loop.widget = self.view

    def close_dialog_and_run(self, command=None):
        if command is not None:
            self.command = command
            self.loop.widget = self.view
            raise urwid.ExitMainLoop()
        else:
            self.loop.widget = self.view

    def change_log(self, log):
        self.log = log


EXIT_REDIAL = "__EXIT__"


def on_focus_change(listbox):
    State.focused = listbox.get_focus()[0]


def run():
    app = RedialApplication()

    signal.signal(signal.SIGINT, partial(sigint_handler, app))

    while True:
        app.run()

        if app.command:
            if app.command == EXIT_REDIAL:
                break
            else:
                rk = os.system(app.command)
                if rk == 33280 or rk == 0:
                    app.command_return_key = rk
                else:
                    app.command_return_key = rk
                    break

    save_ui_state(app.listbox)


def sigint_handler(app, signum, frame):
    app.command = EXIT_REDIAL
    raise urwid.ExitMainLoop()


if __name__ == "__main__":
    run()
