# TerminalView

[![Build Status](https://travis-ci.org/Wramberg/TerminalView.svg?branch=master)](https://travis-ci.org/Wramberg/TerminalView)

A Linux/macOS plugin for Sublime Text 3 that allows for terminals inside editor views. The plugin uses a pseudo-terminal to start the underlying shell which means it supports

* Interactive applications
* Auto-completion
* Terminal shortcuts (`ctrl`+`c`, etc.)
* Password prompts
* etc.

**Note that you may have to insert some keybindings in your user keymap for everything to work - see the keybindings section for details.**

![example.gif](https://raw.githubusercontent.com/Wramberg/TerminalView/master/example.gif "TerminalView Demonstration")

## Dependencies
To run this plugin you need

* Linux-based OS
* Sublime Text 3 (build 3092 or newer)
* bash (this is not required but recommended, see "Changing shell" below for details)

## Installation
To install from https://packagecontrol.io/

1. Open the command palette (`ctrl`+`shift`+`p` by default) and find "Package Control: Install Package"
2. Search for TerminalView and hit `enter` to install.

To install manually from github run

```
git clone https://github.com/Wramberg/TerminalView.git $HOME/.config/sublime-text-3/Packages/TerminalView
```

## Usage
Simply bring up your command pallete (`ctrl`+`shift`+`p` by default) and search for "Terminal View". This opens a terminal using 'bash -l' as shell. By default there is no keybinding for opening a terminal view but you can bind a key in your keymap to the *terminal_view_open* command:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open" },
```

which does the same.

## Keybindings
The following keys are forwarded to the shell by default:

* All single characters and numbers
* All signs (create an issue if some are missing)
* Arrow keys
* `home`, `end`, `delete`, `insert`, `pageup`, `pagedown`
* `escape`, `tab`, `space`, `backspace`, `enter`
* Any `ctrl`+`<char>` combination except `ctrl`+`k` (see below if you want this to go to the shell instead of ST3)
* Any `alt`+`<char>` combination
* Any `ctrl`+`<arrow key>` combination

Note that `ctrl`+`<sign>` combinations are not forwarded as they depend on keyboard layout. The default keymap is available in the menu: *Preferences->Package Settings->TerminalView*. Copy and adjust any missing keybindings into your user keymap.

**If some of the keybindings are not working they are probably shadowed by keybindings in your user keymap.** To fix this find the missing keybindings in the default keymap and copy them into your user keymap. For example, if you have bound `alt`+`f` in your user keymap you need to insert the following in your user keymap:

```
{"keys": ["alt+f"], "command": "terminal_view_keypress", "args": {"key": "f", "alt": true}, "context": [{"key": "setting.terminal_view"}]},
```

Similarly, if you want to override some of the default TerminalView keybindings like e.g. `ctrl`+`w` move the following into your user keymap

```
{ "keys": ["ctrl+w"], "command": "close" },
```

Lastly TerminalView also includes a few utility keybindings:

Shortcut | Command | Description
--- | --- | ---
`ctrl` + `shift` + `c` | terminal_view_copy | Copy the selection/line in the terminal into the clipboard
`ctrl` + `shift` + `v` | terminal_view_paste | Paste the contents of the clipboard into the terminal
`alt` + `mouse wheel up` / `mouse wheel down` | terminal_view_scroll | Scroll back/forward in terminal history
`shift` + `pageup` / `pagedown` | terminal_view_scroll | Scroll back/forward in terminal history
`ctrl` + `shift` + `t` / `n` | new_file | Open a new file
`ctrl` + `shift` + `w` / `q` | close | Close the terminal view
`ctrl` + `shift` + `up` / `down` / `left` / `right` | move | Move the ST3 cursor (not the terminal cursor)
`ctrl` + `shift` + `home` / `end` | move_to | Move the ST3 cursor to beginning/end of line

Note that standard ST3 keybindings for selection are **not** shadowed which mean you can use `shift` + `keys` for selection in the terminal in case you prefer to use the keyboard. These keybindings do not move the actual terminal cursor however so whenever the terminal is updated the cursor will snap back to its point of origin.

## Changing shell
If you want to use another shell it is highly recommended to do this through bash with the -c command line argument. You can control the shell command through the *cmd* argument to the *terminal_view_open* command. In addition, you can also alter the title of the terminal view to reflect which shell is running.

If you e.g. want to run an IPython shell when hitting `ctrl`+`alt`+`t`, add the following to your keymap file:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open", "args": {"cmd": "/bin/bash -l -c /usr/bin/ipython", "title": "Terminal (IPython)"}},
```

If you really want to avoid using bash you can also run your shell directly:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open", "args": {"cmd": "/usr/bin/ipython", "title": "Terminal (IPython)"}},
```

but this is **very experimental**. Some future development regarding this is planned, but at the moment only bash is tested.

When you are done you can close the terminal by closing the view (`ctrl`+`shift`+`q` or `ctrl`+`shift`+`w` as default) or exiting the shell (by e.g. hitting `ctrl`+`d`).

## Settings
The settings are available in the menu: *Preferences->Package Settings->TerminalView*. The settings include options for adjusting colors, scrollback history and similar. Simply copy the settings you want to change into your user settings which are also available in the menu.

## Color scheme
The color scheme is used for both dynamic coloring (colors set by the shell) and static coloring (colors set by syntax highlighting). Both options can be controlled in the settings. The color scheme itself can be tweaked by copying the default color scheme into the user color scheme file. Both of these files are available in the menu: *Preferences->Package Settings->TerminalView*.

## Syntax highlighting
The plugin supports user provided syntax highlighting for static coloring. To use this feature create a *\<name\>.sublime-syntax* file in your *Packages/User* folder. The *packages* folder can accessed through the menu: *Preferences->Browse Packages*. The content of the file depends entirely on your needs - see https://www.sublimetext.com/docs/3/syntax.html for details. As an example consider the following which highlights the prompt in bash.

```
%YAML 1.2
---
name: TerminalViewBash
hidden: true
file_extensions:
  - terminal_view
scope: text.terminal_view
contexts:
  main:
    - match: '\w+@[A-z,\-_]+(?=:)'
      scope: terminalview.black_green
    - match: '([A-z,\-_/~0-9.]+\$)'
      scope: terminalview.black_blue
```

The matching could be improved upon but it will do for the purpose of this example. Note that the scope names are chosen so they match with scopes that are already defined in the color scheme. To change the color scheme see the "color scheme" section above. In this example the syntax file was saved as *bash.sublime-syntax* under the *Packages/User* folder. To use it when opening a bash terminal pass it to the *terminal_view_open* command with the *syntax* argument:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open", "args": {"cmd": "/bin/bash -l", "title": "Bash Terminal", "syntax": "bash.sublime-syntax"}},
```

Note that no syntax-files are provided with the plugin at the moment so all users must create their own.

## Future development
Development is performed ad-hoc and current plans include:

* Using ST3 scrolling instead of pyte scrolling (requires decent amount of work but would make scrolling and copying better)
* Functionality for dynamic amount of scrolling (right now its a fixed ratio only adjustable through settings)
* Support for "editor" mode where cursor can move freely and standard ST3 keybindings can be used
* 256 color support
* Support for more shells
* Support for re-opening old sessions when ST3 is restarted (may not be feasible, investigation needed)
* QOL shortcut that can find and open filepaths in the terminal window
* Experimentation with Windows support (through WSL)

## Acknowledgments
The pyte terminal emulator (https://github.com/selectel/pyte) is an integral part of this plugin and deserves some credit for making this plugin possible.

During development the SublimePTY plugin (https://github.com/wuub/SublimePTY) was a good source of inspiration for some of the problems that occurred. You can probably find a few bits and pieces from it in this plugin.

For testing stubs and general test structure the Javatar plugin (https://github.com/spywhere/Javatar) was a good point of origin.
