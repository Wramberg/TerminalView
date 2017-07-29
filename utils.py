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


class TerminalViewSendString(sublime_plugin.WindowCommand):
    """
    A command to send any text to the active terminal.
    Example to send sigint:
        window.run_command("terminal_view_send_string", args={"string": "\x03"})
    """
    def run(self, string, current_window_only=True):
        if current_window_only:
            windows = [self.window]
        else:
            windows = sublime.windows()

        view = None
        for w in windows:
            for v in w.views():
                if v.settings().get("terminal_view"):
                    group, index = w.get_view_index(v)
                    active_view = w.active_view_in_group(group)
                    if active_view == v:
                        view = v
                        break

        if not view:
            print("no terminal found.")
            return

        terminal_view = TerminalViewManager.load_from_id(view.id())
        terminal_view.send_string_to_shell(string)
