import os
import time

import sublime
import sublime_plugin

from . import SublimeTerminalBuffer
from . import LinuxPty
from . import utils

# Todo
# clean global_keypress_callback when terminal is closed
# colors
# maybe reset terminal on resize ?

class TerminalViewOpen(sublime_plugin.TextCommand):
    """Main command to glue everything together. One instance of this per view.
    """

    def run(self, 
            edit, 
            cmd="/bin/bash -l", 
            title="Terminal", 
            cwd="${project_path:${folder:${file_path}}}"):
        """
        Open a new terminal view

        Args:
            cmd (str, optional): Shell to execute. Detauls to 'bash -l'.
            title (str, optional): Terminal view title. Defaults to 'Terminal'.
            cwd (str, optional): The working dir to start out with. Defaults to
                                 either the project path, the currently open
                                 folder, the directory of the current file, or
                                 $HOME, in that order of precedence.
        """
        if sublime.platform() not in ("linux", "osx"):
            sublime.error_message("TerminalView: Unsupported OS")
            return
        window = self.view.window()
        cwd = sublime.expand_variables(cwd, window.extract_variables())
        if not cwd:
            cwd = os.environ["HOME"]
        window.new_file().run_command("terminal_view_core", 
                args={"cmd": cmd, "title": title, "cwd": cwd})

class TerminalViewCore(sublime_plugin.TextCommand):
    """
    Main command to glue all parts together in a single instance of a terminal
    view. For each sublime view a instance of this class exists.
    """
    def run(self, edit, cmd, title, cwd):
        """
        Initialize the view in which this command is called as a terminal view.

        Args:
            cmd (str): Command to execute as shell (e.g. 'bash -l').
            title (str): Terminal view title.
            cwd (str): The working directory to start out with.
        """
        self._terminal_buffer = SublimeTerminalBuffer.SublimeTerminalBuffer(self.view, title)
        self._terminal_buffer.set_keypress_callback(self.terminal_view_keypress_callback)
        self._terminal_buffer_is_open = True
        self._terminal_rows = 0
        self._terminal_columns = 0

        # Do an initial buffer draw to fill out terminal with blank spaces
        # before we read initial size
        self._terminal_buffer.update_view()

        self._shell = LinuxPty.LinuxPty(cmd.split(), cwd)
        self._shell_is_running = True

        # Do initial resize instantly to avoid resizing after first shell prompt
        self._schedule_call_to_check_for_screen_resize(delay=0)
        self._schedule_call_to_poll_shell_output()
        self._schedule_call_to_refresh_terminal_view()
        self._schedule_call_to_check_if_terminal_closed_or_shell_exited()

    def terminal_view_keypress_callback(self, key, ctrl=False, alt=False, shift=False, meta=False):
        """
        Callback when a keypress is registered in the Sublime Terminal buffer.

        Args:
            key (str): String describing pressed key. May be a name like 'home'.
            ctrl (boolean, optional)
            alt (boolean, optional)
            shift (boolean, optional)
            meta (boolean, optional)
        """
        self._shell.send_keypress(key, ctrl, alt, shift, meta)

    def _schedule_call_to_check_for_screen_resize(self, delay=250):
        """
        Schedule a call to the screen resize member function in the Sublime Text
        main thread.
        """
        if not self._stopped():
            sublime.set_timeout(self._check_for_screen_resize, delay)

    def _schedule_call_to_poll_shell_output(self):
        """
        Schedule a call to the shell polling member function in the Sublime Text
        main thread.
        """
        if not self._stopped():
            sublime.set_timeout(self._poll_shell_output, 5)

    def _schedule_call_to_refresh_terminal_view(self):
        """
        Schedule a call to the terminal refreshing member function in the
        Sublime Text main thread.
        """
        if not self._stopped():
            sublime.set_timeout(self._refresh_terminal_view, 20)

    def _schedule_call_to_check_if_terminal_closed_or_shell_exited(self):
        """
        Schedule a call to the exit check member function in the Sublime Text
        main thread.
        """
        if not self._stopped():
            sublime.set_timeout(self._check_if_terminal_closed_or_shell_exited, 100)

    def _poll_shell_output(self):
        """
        Poll the output of the shell
        """
        max_read_size = 4096
        data = self._shell.receive_output(max_read_size)
        if data is not None:
            utils.log_to_console("Got %u bytes of data from shell" % (len(data), ))
            self._terminal_buffer.insert_data(data)

        self._schedule_call_to_poll_shell_output()

    def _refresh_terminal_view(self):
        """
        Update the terminal view so its showing the latest data.
        """
        self._terminal_buffer.update_view()
        self._schedule_call_to_refresh_terminal_view()

    def _check_if_terminal_closed_or_shell_exited(self):
        """
        Check if the terminal was closed or the shell exited. If so stop
        everything.
        """
        self._terminal_buffer_is_open = self._terminal_buffer.is_open()
        self._shell_is_running = self._shell.is_running()

        if (not self._terminal_buffer_is_open) or (not self._shell_is_running):
            self._stop()

        self._schedule_call_to_check_if_terminal_closed_or_shell_exited()

    def _check_for_screen_resize(self):
        """
        Check if the terminal view was resized. If so update the screen size of
        the terminal and notify the shell.
        """
        (rows, cols) = self._terminal_buffer.view_size()
        row_diff =  abs(self._terminal_rows - rows)
        col_diff =  abs(self._terminal_columns - cols)

        if row_diff or col_diff:
            log = "Changing screen size from (%i, %i) to (%i, %i)" % \
                  (self._terminal_rows, self._terminal_columns, rows, cols)
            utils.log_to_console(log)

            self._terminal_rows = rows
            self._terminal_columns = cols
            self._shell.update_screen_size(self._terminal_rows, self._terminal_columns)
            self._terminal_buffer.update_terminal_size(self._terminal_rows, self._terminal_columns)

        self._schedule_call_to_check_for_screen_resize()

    def _stop(self):
        """
        Stop the terminal and close everything down.
        """
        if self._terminal_buffer_is_open:
            self._terminal_buffer.close()
            self._terminal_buffer_is_open = False

        if self._shell_is_running:
            self._shell.stop()
            self._shell_is_running = False

    def _stopped(self):
        """
        Check if the terminal and shell are stopped.
        """
        if self._shell_is_running and self._terminal_buffer_is_open:
            return False
        return True
