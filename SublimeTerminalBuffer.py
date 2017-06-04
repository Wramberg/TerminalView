import collections

import sublime
import sublime_plugin

from . import pyte
from . import utils


class SublimeTerminalBuffer():
    def __init__(self, sublime_view, title):
        self._view = sublime_view
        sublime_view.set_name(title)
        sublime_view.set_scratch(True)
        sublime_view.set_read_only(True)
        sublime_view.settings().set("gutter", False)
        sublime_view.settings().set("highlight_line", False)
        sublime_view.settings().set("auto_complete_commit_on_tab", False)
        sublime_view.settings().set("draw_centered", False)
        sublime_view.settings().set("word_wrap", False)
        sublime_view.settings().set("auto_complete", False)
        sublime_view.settings().set("draw_white_space", "none")
        sublime_view.settings().set("draw_indent_guides", False)
        sublime_view.settings().set("caret_style", "blink")
        sublime_view.settings().add_on_change('color_scheme', lambda: set_color_scheme(sublime_view))

        # Check if colors are enabled
        settings = sublime.load_settings('TerminalView.sublime-settings')
        self.show_colors = settings.get("terminal_view_show_colors", True)

        # Mark in the views private settings that this is a terminal view so we
        # can use this as context in the keymap
        sublime_view.settings().set("terminal_view", True)
        sublime.active_window().focus_view(sublime_view)

        # Save a dict on the view to store color regions for each line
        sublime_view.terminal_view_color_regions = {}

        # Save keypress callback for this view
        sublime_view.terminal_view_keypress_callback = None

        # Keep track of the content in the buffer (having a local copy is a lot
        # faster than using the ST3 API to get the contents)
        sublime_view.terminal_view_buffer_contents = {}

        # Use pyte as underlying terminal emulator
        self._bytestream = pyte.ByteStream()
        self._screen = pyte.DiffScreen(400, 150)
        self._bytestream.attach(self._screen)

    def set_keypress_callback(self, callback):
        self._view.terminal_view_keypress_callback = callback

    def insert_data(self, data):
        self._bytestream.feed(data)

    def update_view(self):
        if len(self._screen.dirty) > 0:
            # Convert the complex pyte buffer to a simple color map
            color_map = {}
            if self.show_colors:
                color_map = convert_pyte_buffer_lines_to_colormap(self._screen.buffer, self._screen.dirty)

            # Update the view - note that the update is saved on the view
            # instead of being sent as an argument since this is faster and also
            # allows for e.g. integer keys (and screen.dirty does not have to
            # converted to a list)
            update = {
                "lines": self._screen.dirty,
                "display": self._screen.display,
                "color_map": color_map
            }
            self._view.terminal_view_buffer_update = update
            self._view.run_command("terminal_view_update_lines")

        self._update_cursor()
        self._screen.dirty.clear()

    def is_open(self):
        """
        Check if the terminal view is open.
        """
        if self._view.window() is not None:
            return True

        return False

    def close(self):
        if self.is_open():
            sublime.active_window().focus_view(self._view)
            sublime.active_window().run_command("close_file")

    def update_terminal_size(self, nb_rows, nb_cols):
        self._screen.resize(lines=nb_rows, columns=nb_cols)

    def view_size(self):
        view = self._view
        (pixel_width, pixel_height) = view.viewport_extent()
        pixel_per_line = view.line_height()
        pixel_per_char = view.em_width()

        if pixel_per_line == 0 or pixel_per_char == 0:
            return (0, 0)

        nb_columns = int(pixel_width/pixel_per_char) - 2
        if nb_columns < 40:
            nb_columns = 40

        nb_rows = int(pixel_height/pixel_per_line)
        if nb_rows < 20:
            nb_rows = 20

        return (nb_rows, nb_columns)

    def _update_cursor(self):
        cursor = self._screen.cursor
        if cursor:
            update = {"cursor_x": cursor.x, "cursor_y": cursor.y}
            self._view.run_command("terminal_view_move_cursor", update)


class TerminalViewMoveCursor(sublime_plugin.TextCommand):
    def run(self, edit, cursor_x, cursor_y):
        tp = self.view.text_point(cursor_y, cursor_x)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(tp, tp))


class TerminalViewKeypress(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        if type(kwargs["key"]) is not str:
            sublime.error_message("Terminal View: Got keypress with non-string key")
            return

        if "meta" in kwargs and kwargs["meta"]:
            sublime.error_message("Terminal View: Meta key is not supported yet")
            return

        if "meta" not in kwargs:
            kwargs["meta"] = False
        if "alt" not in kwargs:
            kwargs["alt"] = False
        if "ctrl" not in kwargs:
            kwargs["ctrl"] = False
        if "shift" not in kwargs:
            kwargs["shift"] = False

        out_str = "Keypress registered: " + str(kwargs)
        utils.log_to_console(out_str)

        if self.view.terminal_view_keypress_callback:
            cb = self.view.terminal_view_keypress_callback
            cb(kwargs["key"], kwargs["ctrl"], kwargs["alt"], kwargs["shift"], kwargs["meta"])


class TerminalViewUpdateLines(sublime_plugin.TextCommand):
    def run(self, edit):
        # Grab the update data from the view which is not parsed as argument
        # due to reasons described at the calling place.
        lines = self.view.terminal_view_buffer_update["lines"]
        display = self.view.terminal_view_buffer_update["display"]
        color_map = self.view.terminal_view_buffer_update["color_map"]

        self.view.set_read_only(False)
        for line_no in sorted(lines):
            # We may get line numbers outside the current display if it was
            # resized to be smaller
            if line_no > len(display) - 1:
                break

            # Clear any colors on the line
            self._remove_color_regions_on_line(line_no)

            # Update the line
            self._update_line_content(edit, line_no, display[line_no])

            # Apply colors to the line if there are any on it
            if line_no in color_map:
                self._update_line_colors(line_no, color_map[line_no])

        self.view.set_read_only(True)

    def _remove_color_regions_on_line(self, line_no):
        if line_no in self.view.terminal_view_color_regions:
            region_deque = self.view.terminal_view_color_regions[line_no]
            try:
                while(1):
                    region = region_deque.popleft()
                    self.view.erase_regions(region)
            except IndexError:
                pass

    def _update_line_content(self, edit, line_no, content):
        # Note this function has been optimized quite a bit. Calls to the ST3
        # API has been left out on purpose as they are slower than the
        # alternative.

        # Get start and end point of the line
        line_start, line_end = self._get_line_start_and_end_points(line_no)

        # Make region spanning entire line (including any newline at the end)
        line_region = sublime.Region(line_start, line_end)

        # Replace content on the line with new content
        content_w_newline = content + "\n"
        self.view.replace(edit, line_region, content_w_newline)

        # Update our local copy of the ST3 view buffer
        self.view.terminal_view_buffer_contents[line_no] = content_w_newline

    def _update_line_colors(self, line_no, line_color_map):
        # Note this function has been optimized quite a bit. Calls to the ST3
        # API has been left out on purpose as they are slower than the
        # alternative.

        for idx, field in line_color_map.items():
            length = field["field_length"]
            color_scope = "terminalview.%s_%s" % (field["color"][0], field["color"][1])

            # Get text point where color should start
            line_start, _ = self._get_line_start_and_end_points(line_no)
            color_start = line_start + idx

            # Make region that should be colored
            buffer_region = sublime.Region(color_start, color_start+length)
            region_key = "%i,%s" % (line_no, idx)

            # Add the region
            flags = sublime.DRAW_NO_OUTLINE | sublime.PERSISTENT
            self.view.add_regions(region_key, [buffer_region], color_scope, flags=flags)
            self._register_color_region(line_no, region_key)

    def _register_color_region(self, line_no, key):
        if line_no in self.view.terminal_view_color_regions:
            self.view.terminal_view_color_regions[line_no].appendleft(key)
        else:
            self.view.terminal_view_color_regions[line_no] = collections.deque()
            self.view.terminal_view_color_regions[line_no].appendleft(key)

    def _get_line_start_and_end_points(self, line_no):
        start_point = 0

        # Sum all lines leading up to the line we want the start point to
        for i in range(line_no):
            if i in self.view.terminal_view_buffer_contents:
                line_len = len(self.view.terminal_view_buffer_contents[i])
                start_point = start_point + line_len

        # Add length of line to the end_point
        end_point = start_point
        if line_no in self.view.terminal_view_buffer_contents:
            line_len = len(self.view.terminal_view_buffer_contents[line_no])
            end_point = end_point + line_len

        return (start_point, end_point)


def convert_pyte_buffer_lines_to_colormap(buffer, lines):
    color_map = {}
    for line_index in lines:
        # There may be lines outside the buffer after terminal was resized.
        # These are considered blank.
        if line_index > len(buffer) - 1:
            break

        # Get line and process all colors on that. If there are multiple
        # continuous fields with same color we want to combine them for
        # optimization and because it looks better when rendered in ST3.
        line = buffer[line_index]
        if len(line) == 0:
            continue

        # Initialize vars to keep track of continuous colors
        last_color = (line[0].bg, line[0].fg)
        last_index = 0
        field_length = 0

        # for char_index, char in enumerate(line):
        for char_index, char in enumerate(line):
            # Default bg is black
            if char.bg is "default":
                bg = "black"
            else:
                bg = char.bg

            # Default fg is white
            if char.fg is "default":
                fg = "white"
            else:
                fg = char.fg

            color = (bg, fg)

            if last_color == color:
                field_length = field_length + 1
            else:
                color_dict = {"color": last_color, "field_length": field_length}

                if last_color != ("black", "white"):
                    if line_index not in color_map:
                        color_map[line_index] = {}
                    color_map[line_index][last_index] = color_dict

                last_color = color
                last_index = char_index
                field_length = 1

    return color_map


def set_color_scheme(view):
    """
    Set color scheme for view
    """
    color_scheme = "Packages/TerminalView/TerminalView.hidden-tmTheme"

    # Check if user color scheme exists
    try:
        sublime.load_resource("Packages/User/TerminalView.hidden-tmTheme")
        color_scheme = "Packages/User/TerminalView.hidden-tmTheme"
    except:
        pass

    if view.settings().get('color_scheme') != color_scheme:
        view.settings().set('color_scheme', color_scheme)
