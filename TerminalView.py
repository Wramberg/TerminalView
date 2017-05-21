import os
import time

import sublime
import sublime_plugin

from . import SublimeTerminalView
from . import linux_pty
from . import utils

# note
# ctrl+e bug with standard sublime

# todo
# screen resize test and fix when small col
# more keybindings i.e. ctrl+e
# colors
# maybe reset terminal on resize ?

# Main entry point for opening a terminal view. Only one instance of this class
# per sublime window. Once a terminal view has been opened the
# TerminalViewCore instance for that view is called to handle everything.
class TerminalViewOpen(sublime_plugin.WindowCommand):
    def run(self):
        win = sublime.active_window()
        view = win.new_file()
        view.run_command("terminal_view_core")


class TerminalViewCore(sublime_plugin.TextCommand):
    def run(self, edit):
        self._terminal_view = SublimeTerminalView.SublimeTerminalView(self.view, "bash")
        self._terminal_view.set_keypress_callback(self.terminal_view_keypress_callback)
        self._terminal_view_is_open = True
        self._terminal_rows = 0
        self._terminal_columns = 0

        self._shell = linux_pty.linux_pty("/bin/bash")
        self._shell_is_running = True

        self._schedule_call_to_check_for_screen_resize()
        self._schedule_call_to_poll_shell_output()
        self._schedule_call_to_refresh_terminal_view()
        self._schedule_call_to_check_if_terminal_closed_or_shell_exited()

    def terminal_view_keypress_callback(self, key, ctrl=False, alt=False, shift=False, meta=False):
        self._shell.send_keypress(key, ctrl, alt, shift, meta)

    def _schedule_call_to_check_for_screen_resize(self):
        if not self._stopped():
            sublime.set_timeout(self._check_for_screen_resize, 250)

    def _schedule_call_to_poll_shell_output(self):
        if not self._stopped():
            sublime.set_timeout(self._poll_shell_output, 5)

    def _schedule_call_to_refresh_terminal_view(self):
        if not self._stopped():
            sublime.set_timeout(self._refresh_terminal_view, 20)

    def _schedule_call_to_check_if_terminal_closed_or_shell_exited(self):
        if not self._stopped():
            sublime.set_timeout(self._check_if_terminal_closed_or_shell_exited, 100)

    def _poll_shell_output(self):
        max_read_size = 4096
        data = self._shell.receive_output(max_read_size)
        if data is not None:
            utils.log_to_console("Got %u bytes of data from shell" % (len(data), ))
            start = time.time()
            self._terminal_view.insert_data(data)

        self._schedule_call_to_poll_shell_output()

    def _refresh_terminal_view(self):
        self._terminal_view.update_view()
        self._schedule_call_to_refresh_terminal_view()

    def _check_if_terminal_closed_or_shell_exited(self):
        self._terminal_view_is_open = self._terminal_view.is_open()
        self._shell_is_running = self._shell.is_running()

        if (not self._terminal_view_is_open) or (not self._shell_is_running):
            self._stop()

        self._schedule_call_to_check_if_terminal_closed_or_shell_exited()

    def _check_for_screen_resize(self):
        (rows, cols) = self._terminal_view.view_size()
        row_diff =  abs(self._terminal_rows - rows)
        col_diff =  abs(self._terminal_columns - cols)

        if row_diff or col_diff:
            # print("Changing screen size from (%i, %i) to (%i, %i)" % (self._terminal_rows, self._terminal_columns, rows, cols))
            self._terminal_rows = rows
            self._terminal_columns = cols
            self._shell.update_screen_size(self._terminal_rows, self._terminal_columns)
            self._terminal_view.update_terminal_size(self._terminal_rows, self._terminal_columns)

        self._schedule_call_to_check_for_screen_resize()

    def _stop(self):
        if self._terminal_view_is_open:
            self._terminal_view.close()
            self._terminal_view_is_open = False

        if self._shell_is_running:
            self._shell.stop()
            self._shell_is_running = False

    def _stopped(self):
        if self._shell_is_running and self._terminal_view_is_open:
            return False
        return True
