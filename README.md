# redial22 improved

[![Build Status](https://img.shields.io/pypi/pyversions/redial22.svg)](https://pypi.org/project/redial22/)
[![License](https://img.shields.io/github/license/FelipeMiranda/redial22)](LICENSE)
[![Version](https://img.shields.io/pypi/v/redial22)](https://pypi.org/project/redial22/)

redial22 improved is a simple shell application that manages your SSH sessions on Unix terminal.
This application is a fork of the original [redail](https://github.com/taypo/redial) developed by:
Author: Bahadır Yağan

![redial22](https://github.com/FelipeMiranda/redial22/blob/master/doc/redial.png?raw=true)

## What's New

### 1.1.0 (07-09-2025)
- Basic support for adding ssh keys to connections
- Dynamic, Local and Remote port forwarding settings (only one of each can be defined for now)
- UI state is restored at startup. Redial22 now remembers last selected connection and folder expanded/collapsed states
- Support to use ProxyJump (Bastion servers)
- Now you can remove a folder
- Run on Docker container (updated with Debian Bookworm)

## Installation

### Requirements
- Python 3 or later to run redial22.
- [mc (Midnight Commander)](https://midnight-commander.org/) to use `F5 (Browse)` feature.

#### Installing mc (Midnight Commander)

**Ubuntu/Debian:**
```bash
sudo apt-get install mc
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install mc
# or for newer versions:
sudo dnf install mc
```

**macOS:**
```bash
brew install mc
```

**Arch Linux:**
```bash
sudo pacman -S mc
```

### Stable Version

#### Installing via pip

We recommend installing redial22 via pip:

```bash
pip3 install redial22
``` 

### Latest Version

#### Installing from Git

You can install the latest version from Git:

```bash
pip3 install git+https://github.com/FelipeMiranda/redial22.git
```

### Docker

[Dockerfile](Dockerfile) is provided. 

#### Build Dockerfile:

```bash
docker build -t redial22 .
```

#### Run redial22 in Docker Container

```bash
docker run -it --rm redial22:latest redial22
```

## Features
- [x] Manage your connections in folders/groups
- [x] Open a file manager to your remote host (Midnight Commander should be installed)
- [x] Edit/Move/Delete connection
- [x] Copy SSH Key to remote host
- [x] ProxyJump (Bastion server)
- [x] Type-to-search for connections and folders (see below)

### Type-to-Search (Incremental Search)

Press `/` to enter search mode, then start typing the name or IP of a connection or folder. The first visible match will be selected automatically. Press `ESC` or `Enter` to exit search mode.

**Note:** The search only works for folders and connections that are currently visible (i.e., inside expanded folders). If a folder is collapsed, its contents will not be found by search until you expand it.

### Connect to SSH Session (ENTER)

Press `ENTER` to connect a SSH session.

![connect_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/connect.gif)

### Add Folder (F6)

Press `F6` or click `F6 New Folder` to add a folder. There must be at least
one connection under the folder. 

![add_folder_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/add_folder.gif)

### Add Connection (F7)

Press `F7` or click `F7 New Conn.` to add a ssh connection. 

![add_conn_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/add_connection.gif)

### Browse over mc (F5)

Press `F5` or click `F5 Browse` to open mc (Midnight Commander) session. 

**Note:** This feature requires `mc` (Midnight Commander) to be installed on your system. If you don't have it installed, you'll see an error message. See the installation instructions above.

![mc_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/mc.gif)

### Remove Connection (F8)

Press `F8` or click `F8 Remove` to remove a session/folder. 

![remove_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/remove.gif)

### Edit Connection (F9)

Press `F9` or click `F9 Edit` to edit a session. 

![edit_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/edit.gif)


### Move sessions and folders

Press `CTRL` and `up/down` keys to move session or folder. **For macOS users:** Use `ALT` and `up/down` keys.

![move_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/move.gif)

## Notes

Configuration file is stored in `~/.config/redial22/sessions`. File format
is same as the [SSH config](https://man.openbsd.org/ssh_config) file. Configuration file can be included in
SSH config file with the following way (Make sure that `~/.ssh/config` file exists): 

```bash
sed -i -e '1iInclude ~/.config/redial22/sessions' ~/.ssh/config
```

## Platforms

- Linux
- macOS

Windows is currently not supported.

## License

redial22 is licensed under the [GNU General Public License v3.0](LICENSE).
