import sys
import os


def main():
    try:
        from .redial import run, RedialApplication
        if len(sys.argv) > 1:
            # Command-line argument provided: try to connect directly or show folder
            arg = sys.argv[1]
            app = RedialApplication()
            # Traverse all nodes to find a connection or folder
            def traverse(node):
                results = []
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        results.extend(traverse(child))
                results.append(node)
                return results
            all_nodes = traverse(app.sessions)
            match = None
            folder_match = None
            for node in all_nodes:
                if getattr(node, 'nodetype', None) == 'session' and getattr(node, 'name', None) == arg:
                    match = node
                    break
            if not match:
                # Try case-insensitive folder match
                for node in all_nodes:
                    if getattr(node, 'nodetype', None) == 'folder' and getattr(node, 'name', '').lower() == arg.lower():
                        folder_match = node
                        break
            if match:
                ssh_cmd = match.hostinfo.get_ssh_command()
                sys.exit(os.system(ssh_cmd))
            elif folder_match:
                # Show only the folder and its subtree in the UI
                app = RedialApplication(root_folder=folder_match)
                sys.exit(app.run())
            else:
                print(f"Connection or folder '{arg}' not found.")
                sys.exit(1)
        else:
            sys.exit(run())
    except KeyboardInterrupt:
        from . import ExitStatus
        sys.exit(ExitStatus.ERROR_CTRL_C)


if __name__ == '__main__':
    main()