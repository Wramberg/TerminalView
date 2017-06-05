"""
Some utility functions for the TerminalView plugin
"""
import time
import sublime


def log_to_console(string):
    """
    Log string to sublime text console if debug is enabled
    """
    settings = sublime.load_settings('TerminalView.sublime-settings')
    print_debug = settings.get("terminal_view_print_debug", False)
    if print_debug:
        prefix = "[terminal_view debug] [%.3f] " % (time.time())
        print(prefix + string)
