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


class TerminalViewManager():
    """
    A manager to control all TerminalView instance.
    """
    @classmethod
    def register(cls, terminal_view):
        if not hasattr(cls, "terminal_views"):
            cls.terminal_views = {}
        cls.terminal_views[terminal_view.view.id()] = terminal_view
        return terminal_view

    @classmethod
    def load_from_id(cls, vid):
        if vid in cls.terminal_views:
            return cls.terminal_views[vid]
        else:
            raise Exception("terminal view not found.")
