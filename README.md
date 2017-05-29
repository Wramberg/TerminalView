# TerminalView
A Linux/macOS plugin for Sublime Text 3 that allows for terminals inside editor views. The plugin uses a pseudo-terminal to start the underlying shell which means it supports

* Interactive applications
* Password prompts
* Piping
* etc.

**Note that you may have to insert some keybindings in your user keymap file for everything to work - see the keybindings section for details. Furthermore, the plugin is quite new and still needs lots of testing and feature development.**

![example.gif](https://raw.githubusercontent.com/Wramberg/TerminalView/master/example.gif "TerminalView Demonstration")

## Installation
Run
```
git clone https://github.com/Wramberg/TerminalView.git $HOME/.config/sublime-text-3/Packages/TerminalView
```
to install TerminalView.

## Usage
Simply bring up your command pallete and search for "Terminal View". This opens a terminal using 'bash -l' as shell. By default there is no keybinding for opening a terminal view but you can bind a key in your keymap to the "terminal_view_open" command:
```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open" },
```
which does the same. If you want to use another shell or have another title you can specify this as arguments to the "terminal_view_open" command:
```
{ "keys": ["ctrl+alt+1"], "command": "terminal_view_open", "args": {"cmd": "/usr/bin/ipython", "title": "Terminal (IPython)"}},
```
but keep in mind that only bash is tested so this is **very experimental**. If you experience weird behavior the only workaround is falling back to bash and running e.g. IPython or ZSH through that.

When you are done you can close the terminal by closing the view (ctrl+shift+q or ctrl+shift+w as default) or exitting the shell (by e.g. hitting ctrl+d).

## Keybindings
The terminal view should be ready to use as you would with any other terminal. There are some caveats though since many keys are needed in a typical terminal workflow.

First of all, the TerminalView plugin shadows a lot of ST3 keybindings (only when in a terminal view of course). To avoid this you can put the keybindings you do not want shadowed in your user keymap file. For example, if you insist on using ctrl-w to close the current view even when in a terminal view put the following line in your user keymap file

```
{ "keys": ["ctrl+w"], "command": "close" },
```

Second of all, to avoid shadowing too many keys some are left out by default. If you find yourself missing a keybinding like, e.g., Alt+f you can simply insert it in your user keymap file
```
{"keys": ["alt+f"], "command": "terminal_view_keypress", "args": {"key": "f", "alt": true, "ctrl": false}, "context": [{"key": "setting.terminal_view"}]},
```
The default TerminalView keymap file is available in the menu: *Preferences->Package Settings-> TerminalView*.

Lastly, some keybindings in your user keymap file may shadow necessary TerminalView keybindings. To avoid this you must find the necessary keybindings in the TerminalView keymap file and copy them to your user keymap file similar to above.

## Limitations
The plugin should be working fine for many tasks but keep in mind that it has yet to be tested thoroughly and still lacks some functionality, this includes

* Colors
* Keybindings/handling for meta and maybe some other keys
* Various customization
* Copy/paste
* Scrolling
* Lots of other stuff i probably haven't thought of yet

## Color scheme
The color scheme can be tweaked by copying the default color scheme into the user color scheme file. Both of these files are availble in the menu: *Preferences->Package Settings->TerminalView*.

## Acknowledgements
During development the SublimePTY (https://github.com/wuub/SublimePTY) project was a good source of inspiration for some of the problems that occured. You can probably find a few bits and pieces from it in this plugin.
