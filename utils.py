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


def unix_signal_name(val):
    UNIX_SIGNAL_NAMES = {
        # Signals described in the original POSIX.1-1990 standard.
        1: "SIGHUP",
        2: "SIGINT",
        3: "SIGQUIT",
        4: "SIGILL",
        6: "SIGABRT",
        8: "SIGFPE",
        9: "SIGKILL",
        10: "SIGUSR1",
        11: "SIGSEGV",
        12: "SIGUSR2",
        13: "SIGPIPE",
        14: "SIGALRM",
        15: "SIGTERM",
        16: "SIGUSR1",
        17: "SIGCHLD",
        18: "SIGCONT",
        19: "SIGSTOP",
        20: "SIGTSTP",
        21: "SIGTTIN",
        22: "SIGTTOU",
        23: "SIGSTOP",
        24: "SIGTSTP",
        25: "SIGCONT",
        26: "SIGTTIN",
        27: "SIGTTOU",
        30: "SIGUSR1",
        31: "SIGUSR2",

        # Signal that are not part of the original POSIX.1-1990 standard but
        # described SUSv2 and POSIX.1-2001.
        5: "SIGTRAP",
        7: "SIGBUS",
    }
    return UNIX_SIGNAL_NAMES.get(val, "UNKNOWN")
