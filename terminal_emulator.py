from . import pyte
from .pyte import wcwidth


class SlidingHistoryScreen(pyte.Screen):
    def __init__(self, columns, lines):
        self._offset = 0
        self._dirty_history_lines = {}
        super().__init__(columns, lines)

    def get_dirty_history_lines(self):
        return self._dirty_history_lines

    def clear_dirty_history_lines(self):
        self._dirty_history_lines.clear()

    def display_line(self, line_no):
        def render(line):
            is_wide_char = False
            for x in range(self.columns):
                if is_wide_char:  # Skip stub
                    is_wide_char = False
                    continue
                char = line[x].data
                assert sum(map(wcwidth.wcwidth, char[1:])) == 0
                is_wide_char = wcwidth.wcwidth(char[0]) == 2
                yield char

        return "".join(render(self.buffer[line_no]))

    def index(self):
        """
        Move the cursor down one line in the same column. If the
        cursor is at the last line, create a new line at the bottom.
        """
        if self.cursor.y == self.margins.bottom:
            if 0 in self.dirty:
                self._dirty_history_lines[self._offset] = self.display_line(0)
            self._offset = self._offset + 1
            self.dirty.update(range(self.lines))

        top, bottom = self.margins

        if self.cursor.y == bottom:
            for line in range(top, bottom):
                self.buffer[line] = self.buffer[line + 1]
            self.buffer.pop(bottom, None)
        else:
            self.cursor_down()

    def offset(self):
        return self._offset


class TerminalEmulator():
    def __init__(self, lines, cols, history=0):
        # self._screen = pyte.HistoryScreen(400, 150, history=history)
        self._screen = SlidingHistoryScreen(lines, cols)
        self._bytestream = pyte.ByteStream()
        self._bytestream.attach(self._screen)

    def feed(self, data):
        return self._bytestream.feed(data)

    def resize(self, rows, cols):
        return self._screen.resize(lines=rows, columns=cols)

    def dirty_lines(self):
        offset = self._screen.offset()
        display = self._screen.display
        dirty = self._screen.get_dirty_history_lines()
        # dirty = {}
        for line_no in self._screen.dirty:
            if line_no > len(display) - 1:
                break

            dirty[line_no + offset] = display[line_no]

        # if len(dirty):
            # print(dirty)
        return dirty

    def clear_dirty_lines(self):
        self._screen.dirty.clear()
        self._screen.clear_dirty_history_lines()

    def cursor(self):
        if self._screen.cursor:
            offset = self._screen.offset()
            y = self._screen.cursor.y
            x = self._screen.cursor.x
            return (y+offset, x)

        return (0, 0)

    # def color_map(self):


def convert_pyte_buffer_to_colormap(buffer, lines):
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

