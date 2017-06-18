import unittest

from TerminalView import terminal_emulator


class pyte_buffer_to_color_map(unittest.TestCase):
    def test_no_colors(self):
        buffer_factory = PyteBufferStubFactory(14, 37)
        pyte_buffer = buffer_factory.produce()
        lines = list(range(14))
        color_map = terminal_emulator.convert_pyte_buffer_to_colormap(pyte_buffer, lines)
        self.assertDictEqual(color_map, {})

    def test_lines_selection(self):
        lines = [2, 3, 6, 19]
        colors = ["red", "green", "magenta", "blue", "cyan"]
        buffer_factory = PyteBufferStubFactory(20, 10)
        for i in range(20):
            buffer_factory.set_color(i, 5, colors[i % len(colors)], "default")

        pyte_buffer = buffer_factory.produce()
        color_map = terminal_emulator.convert_pyte_buffer_to_colormap(pyte_buffer, lines)

        expected = {
            2: {
                5: {'color': ('magenta', 'white'), 'field_length': 1}
            },
            3: {
                5: {'color': ('blue', 'white'), 'field_length': 1}
            },
            6: {
                5: {'color': ('green', 'white'), 'field_length': 1}
            },
            19: {
                5: {'color': ('cyan', 'white'), 'field_length': 1}
            }
        }

        self.assertDictEqual(color_map, expected)

    def test_field_length1(self):
        buffer_factory = PyteBufferStubFactory(25, 20)

        buffer_factory.set_color(3, 11, "red", "green")
        buffer_factory.set_color(3, 12, "red", "green")
        buffer_factory.set_color(3, 13, "red", "green")

        buffer_factory.set_color(8, 1, "blue", "yellow")
        buffer_factory.set_color(8, 2, "blue", "yellow")
        buffer_factory.set_color(8, 3, "blue", "yellow")
        buffer_factory.set_color(8, 4, "blue", "yellow")
        buffer_factory.set_color(8, 5, "blue", "yellow")
        buffer_factory.set_color(8, 6, "blue", "yellow")

        buffer_factory.set_color(8, 8, "blue", "yellow")

        buffer_factory.set_color(24, 1, "yellow", "yellow")
        buffer_factory.set_color(24, 17, "yellow", "yellow")
        buffer_factory.set_color(24, 18, "yellow", "yellow")
        buffer_factory.set_color(24, 19, "yellow", "yellow")

        buffer_factory.set_color(0, 0, "yellow", "cyan")
        buffer_factory.set_color(0, 1, "yellow", "cyan")
        buffer_factory.set_color(0, 2, "yellow", "cyan")
        buffer_factory.set_color(0, 3, "red", "cyan")

        pyte_buffer = buffer_factory.produce()
        lines = list(range(25))
        color_map = terminal_emulator.convert_pyte_buffer_to_colormap(pyte_buffer, lines)

        expected = {
            0: {
                0: {'color': ('yellow', 'cyan'), 'field_length': 3},
                3: {'color': ('red', 'cyan'), 'field_length': 1}
            },
            8: {
                8: {'color': ('blue', 'yellow'), 'field_length': 1},
                1: {'color': ('blue', 'yellow'), 'field_length': 6}
            },
            3: {
                11: {'color': ('red', 'green'), 'field_length': 3}
            },
            24: {
                1: {'color': ('yellow', 'yellow'), 'field_length': 1},
                17: {'color': ('yellow', 'yellow'), 'field_length': 3}
            }
        }

        self.assertDictEqual(color_map, expected)

    def test_field_length2(self):
        buffer_factory = PyteBufferStubFactory(4, 9)

        buffer_factory.set_color(3, 4, "red", "green")
        buffer_factory.set_color(3, 5, "red", "green")
        buffer_factory.set_color(3, 6, "red", "green")

        buffer_factory.set_color(0, 3, "yellow", "cyan")
        buffer_factory.set_color(0, 4, "yellow", "cyan")

        pyte_buffer = buffer_factory.produce()
        lines = list(range(4))
        color_map = terminal_emulator.convert_pyte_buffer_to_colormap(pyte_buffer, lines)

        expected = {
            3: {
                4: {
                    'color': ('red', 'green'),
                    'field_length': 3
                },
            },
            0: {
                3: {
                    'color': ('yellow', 'cyan'),
                    'field_length': 2
                }
            },
        }

        self.assertDictEqual(color_map, expected)


class PyteBufferStubFactory():
    def __init__(self, nb_lines, nb_cols):
        default_char = CharStub("default", "default")

        self.buffer = []
        for i in range(nb_lines):
            line = []
            for j in range(nb_cols):
                # line[j] = default_char # in newer version of pyte line is a dict
                line.append(default_char)
            self.buffer.append(line)

    def set_color(self, line, col, bg, fg):
        self.buffer[line][col] = CharStub(bg, fg)

    def produce(self):
        return self.buffer


class CharStub():
    def __init__(self, bg, fg):
        self.bg = bg
        self.fg = fg
