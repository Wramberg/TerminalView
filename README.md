# TerminalView
A Linux plugin for Sublime Text 3 that allows for terminals inside editor views. The plugin uses a pseudo-terminal to start the underlying shell which means it supports

* Interactive applications
* Piping
* Password prompts
* etc.

## Installation
Run
```
git clone https://github.com/Wramberg/TerminalView.git $HOME/.config/sublime-text-3/Packages/TerminalView
```
to install TerminalView.

## Usage
Bring up your command palette and search for "Terminal View". Alternatively you can bind a key in your keymap to the "terminal_view_open" command, example
```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open" },
```
You can close the terminal again by closing the view or exitting the shell (by e.g. hitting ctrl-d).

## Keybindings
The terminal view should be ready to use as you would with any other terminal. There are some caveats though since many keys are needed in a typical terminal. First of all, the TerminalView plugin shadows a lot of ST3 keybindings (only when in a terminal view of course). To avoid this you can put the keybindings you do not want shadowed in your custom user keymap file. Second of all, some keybindings in your custom user keymap file may shadow necessary TerminalView keybindings. To avoid this you must find the necessary keybindings in the TerminalView keymap file and copy it to your custom keymap file.

## Limitations
The plugin should be working fine for many tasks but keep in mind that it has yet to be tested thoroughly and still lacks some functionality, this includes

* Colors
* Keybindings/handling for meta, alt and maybe some other keys
* Various customization
* Lots of other stuff i probably haven't thought of yet

## Acknowledgements
During development the SublimePTY (https://github.com/wuub/SublimePTY) project was a good source of inspiration for some of the problems that occured. You can probably find a few bits and pieces from it in this plugin.
