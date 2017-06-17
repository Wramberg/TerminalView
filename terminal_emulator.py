"""
Wrapper module for the Pyte terminal emulator
"""
from collections import deque, namedtuple
import math

from . import pyte
from .pyte import modes


class PyteTerminalEmulator():
    """
    Adapter for the pyte terminal emulator
    """
    def __init__(self, cols, lines, history, ratio):
        # Double history size due to pyte splitting it between two queues
        # resulting in only having half the scrollback as expected
        self._screen = CustomHistoryScreen(cols, lines, history * 2, ratio)
        self._bytestream = pyte.ByteStream()
        self._bytestream.attach(self._screen)

    def feed(self, data):
        self._screen.scroll_to_bottom()
        self._bytestream.feed(data)

    def resize(self, lines, cols):
        self._screen.scroll_to_bottom()
        self._screen.dirty.update(range(lines))
        return self._screen.resize(lines, cols)

    def prev_page(self):
        self._screen.prev_page()
        self._screen.ensure_screen_width()

    def next_page(self):
        self._screen.next_page()
        self._screen.ensure_screen_width()

    def dirty_lines(self):
        dirty_lines = {}
        nb_dirty_lines = len(self._screen.dirty)
        if nb_dirty_lines > 0:
            display = self._screen.display
            for line in self._screen.dirty:
                if line >= len(display):
                    # This happens when screen is resized smaller
                    dirty_lines[line] = None
                else:
                    dirty_lines[line] = display[line]

        return dirty_lines

    def clear_dirty(self):
        return self._screen.dirty.clear()

    def cursor(self):
        cursor = self._screen.cursor
        if cursor:
            return (cursor.y, cursor.x)

        return (0, 0)

    def color_map(self, lines):
        return convert_pyte_buffer_to_colormap(self._screen.buffer, lines)


History = namedtuple("History", "top bottom ratio size position")
Margins = namedtuple("Margins", "top bottom")


class CustomHistoryScreen(pyte.Screen):
    """
    Custom history screen customized for this plugin. Basically a copy of the
    standard pyte history screen but with some optimizations.
    """
    def __init__(self, columns, lines, history, ratio):
        self.history = History(deque(maxlen=history // 2),
                               deque(maxlen=history),
                               float(ratio),
                               history,
                               history)

        super(CustomHistoryScreen, self).__init__(columns, lines)

    def scroll_to_bottom(self):
        """
        Ensure a screen is at the bottom of the history buffer
        """
        while self.history.position < self.history.size:
            self.next_page()

    def ensure_screen_width(self):
        """
        Ensure all lines on a screen have proper width columns. Extra characters
        are truncated, missing characters are filled with whitespace.
        """
        for line in self.buffer.values():
            for x in line:
                if x > self.columns:
                    line.pop(x)

        # If we're at the bottom of the history buffer and `DECTCEM`
        # mode is set -- show the cursor.
        self.cursor.hidden = not (
            abs(self.history.position - self.history.size) < self.lines and
            modes.DECTCEM in self.mode
        )

    def _reset_history(self):
        self.history.top.clear()
        self.history.bottom.clear()
        self.history = self.history._replace(position=self.history.size)

    def reset(self):
        """
        Overloaded to reset screen history state: history position
        is reset to bottom of both queues;  queues themselves are
        emptied.
        """
        super(CustomHistoryScreen, self).reset()
        self._reset_history()

    def erase_in_display(self, how=0):
        """
        Overloaded to reset history state
        """
        super(CustomHistoryScreen, self).erase_in_display(how)

        if how == 3:
            self._reset_history()

    def index(self):
        """
        Overloaded to update top history with the removed lines
        """
        top, bottom = self.margins or Margins(0, self.lines - 1)

        if self.cursor.y == bottom:
            self.history.top.append(self.buffer[top])

        super(CustomHistoryScreen, self).index()

    def reverse_index(self):
        """
        Overloaded to update bottom history with the removed lines
        """
        top, bottom = self.margins or Margins(0, self.lines - 1)

        if self.cursor.y == top:
            self.history.bottom.append(self.buffer[bottom])

        super(CustomHistoryScreen, self).reverse_index()

    def prev_page(self):
        """
        Move the screen page up through the history buffer
        """
        if self.history.position > self.lines and self.history.top:
            mid = min(len(self.history.top),
                      int(math.ceil(self.lines * self.history.ratio)))

            self.history.bottom.extendleft(
                self.buffer[y]
                for y in range(self.lines - 1, self.lines - mid - 1, -1))
            self.history = self.history \
                ._replace(position=self.history.position - self.lines)

            for y in range(self.lines - 1, mid - 1, -1):
                self.buffer[y] = self.buffer[y - mid]
            for y in range(mid - 1, -1, -1):
                self.buffer[y] = self.history.top.pop()

            self.dirty = set(range(self.lines))

    def next_page(self):
        """
        Move the screen page down through the history buffer
        """
        if self.history.position < self.history.size and self.history.bottom:
            mid = min(len(self.history.bottom),
                      int(math.ceil(self.lines * self.history.ratio)))

            self.history.top.extend(self.buffer[y] for y in range(mid))
            self.history = self.history \
                ._replace(position=self.history.position + self.lines)

            for y in range(self.lines - mid):
                self.buffer[y] = self.buffer[y + mid]
            for y in range(self.lines - mid, self.lines):
                self.buffer[y] = self.history.bottom.popleft()

            self.dirty = set(range(self.lines))


def convert_pyte_buffer_to_colormap(buffer, lines):
    """
    Convert a pyte buffer to a simple colors
    """
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
        line_len = len(line)
        if line_len == 0:
            continue

        # Initialize vars to keep track of continuous colors
        last_bg = line[0].bg
        if last_bg == "default":
            last_bg = "black"

        last_fg = line[0].fg
        if last_fg == "default":
            last_fg = "white"

        last_color = (last_bg, last_fg)
        last_index = 0
        field_length = 0

        for char_index in line.keys():
            char = line[char_index]

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

            # Check if last color was active to the end of screen
            if last_color != ("black", "white"):
                color_dict = {"color": last_color, "field_length": field_length}
                if line_index not in color_map:
                    color_map[line_index] = {}
                color_map[line_index][last_index] = color_dict

    return color_map
