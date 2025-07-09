import sys
import os


def main():
    try:
        from .redial import run, RedialApplication
        if len(sys.argv) > 1:
            # Command-line argument provided: try to connect directly
            connection_name = sys.argv[1]
            app = RedialApplication()
            # Traverse all nodes to find an exact match (case-sensitive)
            def traverse(node):
                results = []
                if hasattr(node, 'children') and node.children:
                    for child in node.children:
                        results.extend(traverse(child))
                results.append(node)
                return results
            all_nodes = traverse(app.sessions)
            match = None
            for node in all_nodes:
                if getattr(node, 'nodetype', None) == 'session' and getattr(node, 'name', None) == connection_name:
                    match = node
                    break
            if match:
                ssh_cmd = match.hostinfo.get_ssh_command()
                sys.exit(os.system(ssh_cmd))
            else:
                print(f"Connection '{connection_name}' not found.")
                sys.exit(1)
        else:
            sys.exit(run())
    except KeyboardInterrupt:
        from . import ExitStatus
        sys.exit(ExitStatus.ERROR_CTRL_C)


if __name__ == '__main__':
    main()