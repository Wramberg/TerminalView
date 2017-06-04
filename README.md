# TerminalView
A Linux/macOS plugin for Sublime Text 3 that allows for terminals inside editor views. The plugin uses a pseudo-terminal to start the underlying shell which means it supports

* Interactive applications
* Password prompts
* Piping
* etc.

**Note that you may have to insert some keybindings in your user keymap for everything to work - see the keybindings section for details. Furthermore, the plugin is quite new and still needs lots of testing.**

![example.gif](https://raw.githubusercontent.com/Wramberg/TerminalView/master/example.gif "TerminalView Demonstration")

## Dependencies
To run this plugin you need

* Linux-based OS
* Sublime Text 3 (build 3092 or newer)
* bash (this is not required but recommended, see "Changing shell" below for details)

## Installation
Run

```
git clone https://github.com/Wramberg/TerminalView.git $HOME/.config/sublime-text-3/Packages/TerminalView
```

to install TerminalView.

## Usage
Simply bring up your command pallete and search for "Terminal View". This opens a terminal using 'bash -l' as shell. By default there is no keybinding for opening a terminal view but you can bind a key in your keymap to the *terminal_view_open* command:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open" },
```

which does the same.

## Changing shell
If you want to use another shell it is highly recommended to do this through bash with the -c command line argument. You can control the shell command through the *cmd* argument to the *terminal_view_open* command. In addition, you can also alter the title of the terminal view to reflect which shell is running.

If you e.g. want to run an IPython shell when hitting ctrl+alt+t, add the following to your keymap file:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open", "args": {"cmd": "/bin/bash -l -c /usr/bin/ipython", "title": "Terminal (IPython)"}},
```

If you really want to avoid using bash you can also run your shell directly:

```
{ "keys": ["ctrl+alt+t"], "command": "terminal_view_open", "args": {"cmd": "/usr/bin/ipython", "title": "Terminal (IPython)"}},
```

but this is **very experimental**. Some future development regarding this is planned, but at the moment only bash is tested.

When you are done you can close the terminal by closing the view (ctrl+shift+q or ctrl+shift+w as default) or exiting the shell (by e.g. hitting ctrl+d).

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

**If some of the keybindings are not working they are probably shadowed by keybindings in your user keymap.** To fix this find the missing keybindings in the default keymap and copy them into your user keymap. For example, if you have bound `alt`+`f` in your user keymap you need to insert the following in your user keymap as well:

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
`ctrl` + `shift` + `w` | close | Close the terminal view
`ctrl` + `shift` + `q` | close | Close the terminal view

## Settings
The settings are available in the menu: *Preferences->Package Settings->TerminalView*. Simply copy the settings you want to change into your user settings which are also available in the menu. The only thing that is currently configurable is color support. This is disabled by default until further testing has been done.

## Color scheme
The color scheme can be tweaked by copying the default color scheme into the user color scheme file. Both of these files are available in the menu: *Preferences->Package Settings->TerminalView*.

## Future development
Development is performed ad-hoc and current plans include:

* Copy/paste functionality through `ctrl`+`shift`+`c`/`v`
* Scrolling functionality
* Unittesting and CI setup
* Support for more shells

## Acknowledgments
During development the SublimePTY (https://github.com/wuub/SublimePTY) project was a good source of inspiration for some of the problems that occurred. You can probably find a few bits and pieces from it in this plugin.
