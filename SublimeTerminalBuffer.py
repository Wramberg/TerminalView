import time
import copy
from collections import deque

import sublime
import sublime_plugin

from . import pyte
from . import utils

global_keypress_callbacks = {}


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

        # Mark in the views private settings that this is a terminal view so we
        # can use this as context in the keymap
        sublime_view.settings().set("terminal_view", True)
        sublime.active_window().focus_view(sublime_view)

        # Save a dict on the view to store color regions in for each line
        sublime_view.terminal_view_color_regions = {}

        # Use pyte as underlying terminal emulator
        self._bytestream = pyte.ByteStream()
        self._screen = pyte.DiffScreen(80, 24)
        self._bytestream.attach(self._screen)

    def set_keypress_callback(self, callback):
        global_keypress_callbacks[self._view.id()] = callback

    def insert_data(self, data):
        self._bytestream.feed(data)

    def update_view(self):
        if len(self._screen.dirty) > 0:
            start = time.time()
            color_map = convert_pyte_buffer_lines_to_colormap(self._screen.buffer, self._screen.dirty)
            t = time.time() - start
            print("time", t*1000.)

            start = time.time()
            update = {
                "lines": list(self._screen.dirty),
                "display": self._screen.display,
                "color_map": color_map
            }
            self._view.run_command("terminal_view_update_lines", update)
            t = time.time() - start
            print("time", t*1000.)

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
    def run(self, edit, key, ctrl=False, alt=False, shift=False, meta=False):
        if type(key) is not str:
            sublime.error_message("Terminal View: Got keypress with non-string key")
            return

        if meta:
            sublime.error_message("Terminal View: Meta key is not supported yet")
            return

        out_str = "Keypress registered: "
        if ctrl:
            out_str += "[ctrl] + "
        if alt:
            out_str += "[alt] + "
        if shift:
            out_str += "[shift] + "
        if meta:
            out_str += "[meta] + "
        out_str += "[" + key + "]"
        utils.log_to_console(out_str)

        if self.view.id() not in global_keypress_callbacks:
            return

        cb = global_keypress_callbacks[self.view.id()]
        cb(key, ctrl, alt, shift, meta)


class TerminalViewUpdateLines(sublime_plugin.TextCommand):
    def run(self, edit, lines, display, color_map):
        clear_time = 0
        update_time = 0
        color_time = 0

        full_screen_width = self.view.full_line(0).size()
        # print(full_screen_width) # TODO fix that this is zero first time !!!!!!!!!
        # TODO try reordering clear, color and update to see which is fastest

        self.view.set_read_only(False)
        for line_no in sorted(lines):
            # We may get line numbers outside the current display if it was
            # resized to be smaller
            if line_no > len(display) - 1:
                break

            # Update the line
            start = time.time()
            self._update_line_content(edit, line_no, display[line_no], full_screen_width)
            t = time.time() - start
            update_time = update_time + t

            # Clear any colors on the line
            start = time.time()
            self._remove_color_regions_on_line(line_no)
            t = time.time() - start
            clear_time = clear_time + t

            # Apply colors to the line if there are any on it
            if str(line_no) in color_map:
                start = time.time()
                self._update_line_colors(line_no, color_map[str(line_no)], full_screen_width)
                t = time.time() - start
                color_time = color_time + t

        self.view.set_read_only(True)
        print("Done")
        print(clear_time*1000.)
        print(update_time*1000.)
        print(color_time*1000.)
        print("---")

    def _update_line_content(self, edit, line_no, content, full_screen_width):
        # Note this function has been highly optimized to work better with color
        # regions. There are a lot of options in the ST3 API could make this
        # function simpler but they are significantly slower! For example, calls
        # to self.view.line() takes a lot longer than calculating the start and
        # end of the line and construction the region manually.

        # Get first point on the line and last (including newline feed)
        line_start = line_no * full_screen_width
        line_end = line_start + full_screen_width

        # Make region spanning entire line
        line_region = sublime.Region(line_start, line_end)

        # Replace content on the line with new content
        self.view.replace(edit, line_region, content + "\n")

    def _remove_color_regions_on_line(self, line_no):
        if str(line_no) in self.view.terminal_view_color_regions:
            region_deque = self.view.terminal_view_color_regions[str(line_no)]
            try:
                while(1):
                    region = region_deque.popleft()
                    self.view.erase_regions(region)
            except IndexError:
                pass

    def _update_line_colors(self, line_no, line_color_map, full_screen_width):
        for idx, field in line_color_map.items():
            length = field["field_length"]
            color_scope = "terminalview.%s_%s" % (field["color"][0], field["color"][1])

            # Get text point for where color should start
            line_start = line_no * full_screen_width
            color_start = line_start + int(idx)

            # Make region that should be colored
            buffer_region = sublime.Region(color_start, color_start+length)
            region_key = "%i,%s,%f" % (line_no, idx, time.time())

            # Add the region
            flags = sublime.DRAW_NO_OUTLINE | sublime.PERSISTENT
            self.view.add_regions(region_key, [buffer_region], color_scope, flags=flags)
            self._register_color_region(line_no, region_key)

    def _register_color_region(self, line_no, key):
        if str(line_no) in self.view.terminal_view_color_regions:
            self.view.terminal_view_color_regions[str(line_no)].appendleft(key)
        else:
            self.view.terminal_view_color_regions[str(line_no)] = deque()
            self.view.terminal_view_color_regions[str(line_no)].appendleft(key)

class TerminalViewOnCloseCleanup(sublime_plugin.EventListener):
    def on_close(self, view):
        if view.id() in global_keypress_callbacks:
            utils.log_to_console("Cleaning up after view %i closed" % view.id())
            del global_keypress_callbacks[view.id()]


# TODO optimiza this is by far the slowest now
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
        last_color = None
        last_index = None
        line = buffer[line_index]
        for char_index, char in enumerate(line):
            # If the current char is different than default color
            if char.fg != "default" or char.bg != "default":
                # If we havent inserted any info about this line in the
                # color_map yet create the empty dict now
                if str(line_index) not in color_map:
                    color_map[str(line_index)] = {}

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

                # If the color is the same as the previous one we parsed
                color = (bg, fg)
                if last_color == color:
                    length = color_map[str(line_index)][str(last_index)]["field_length"]
                    color_map[str(line_index)][str(last_index)]["field_length"] = length + 1
                else:
                    last_color = color
                    last_index = char_index
                    color_map[str(line_index)][str(char_index)] = {"color": color, "field_length": 1}
            else:
                last_color = None

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
