"""
Some utility functions for the TerminalView plugin
"""
import time
import sublime
import sublime_plugin


class ConsoleLogger():
    """
    Logger service
    """
    @classmethod
    def log(cls, string):
        """
        Log string to sublime text console if debug is enabled
        """
        if not hasattr(cls, "enabled"):
            settings = sublime.load_settings('TerminalView.sublime-settings')
            cls.enabled = settings.get("terminal_view_print_debug", False)

        if cls.enabled:
            prefix = "[terminal_view debug] [%.3f] " % (time.time())
            print(prefix + string)
