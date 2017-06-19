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
* Any `ctrl`+`<char>` combination except `ctrl`+`k`
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

Lastly TerminalView also includes a few utility keybindings.

Shortcut | Command | Description
--- | --- | ---
`alt` + `mouse wheel up` | terminal_view_scroll | Scroll back in terminal history
`alt` + `mouse wheel down` | terminal_view_scroll | Scroll forward in terminal history
`shift` + `pageup` | terminal_view_scroll | Scroll back in terminal history
`shift` + `pagedown` | terminal_view_scroll | Scroll forward in terminal history
`ctrl` + `shift` + `t` | new_file | Open a new file
`ctrl` + `shift` + `n` | new_file | Open a new file
`ctrl` + `shift` + `w` | close | Close the terminal view
`ctrl` + `shift` + `q` | close | Close the terminal view

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
The color scheme can be tweaked by copying the default color scheme into the user color scheme file. Both of these files are available in the menu: *Preferences->Package Settings->TerminalView*.

## Future development
Development is performed ad-hoc and current plans include:

* Copy/paste functionality through `ctrl`+`shift`+`c`/`v`
* Functionality for dynamic amount of scrolling
* 256 color support
* Support for more shells
* Experimentation with Windows support (through WSL)

## Acknowledgments
The pyte terminal emulator (https://github.com/selectel/pyte) is an integral part of this plugin and deserves some credit for making this plugin possible.

During development the SublimePTY plugin (https://github.com/wuub/SublimePTY) was a good source of inspiration for some of the problems that occurred. You can probably find a few bits and pieces from it in this plugin.

For testing stubs and general test structure the Javatar plugin (https://github.com/spywhere/Javatar) was a good point of origin.
