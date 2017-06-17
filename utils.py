"""
Some utility functions for the TerminalView plugin
"""
import time
import sublime


class ConsoleLogger():
    """
    Logger service
    """
    def __init__(self):
        settings = sublime.load_settings('TerminalView.sublime-settings')
        self._enabled = settings.get("terminal_view_print_debug", False)

    def log(self, string):
        """
        Log string to sublime text console if debug is enabled
        """
        if self._enabled:
            prefix = "[terminal_view debug] [%.3f] " % (time.time())
            print(prefix + string)
