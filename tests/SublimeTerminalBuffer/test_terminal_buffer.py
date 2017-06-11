"""
Unittests for the SublimeTerminalBuffer module
"""
import unittest

# Import sublime stub
import sublime

# Module to test
from TerminalView import SublimeTerminalBuffer


# still some stuff todo with this testcase - lacks color tests and more edge
# cases
class line_updates(unittest.TestCase):
    def setUp(self):
        self._test_view = sublime.SublimeViewStub(1)
        self._test_view.terminal_view_color_regions = {}
        self._test_view.terminal_view_buffer_contents = {}
        self._test_view.terminal_view_buffer_update = {
            "lines": [],
            "display": [],
            "color_map": [],
        }
        self._test_line_cmd = SublimeTerminalBuffer.TerminalViewUpdateLines(self._test_view)

        # We assume the view is 5 lines and 11 chars wide
        self._expected_buffer_contents = []
        for i in range(5):
            self._expected_buffer_contents.append("           \n")

        # Update lines 0 to 5 with blanks as we should under normal operation
        self._test_view.terminal_view_buffer_update["lines"] = list(range(5))
        disp = ["           "] * 5
        self._test_view.terminal_view_buffer_update["display"] = disp
        self._test_line_cmd.run(None)

        # Check that local copy of buffer is correct
        buffer_cache = self._test_view.terminal_view_buffer_contents
        for i in range(5):
            self.assertEqual(buffer_cache[i], self._expected_buffer_contents[i])

        # Check that replace calls are done correctly
        replaces = self._test_view.get_replace_calls()
        for i in range(5):
            self.assertEqual(replaces[i].region.a, i * 12)
            self.assertEqual(replaces[i].region.b, i * 12)
            self.assertEqual(replaces[i].content, self._expected_buffer_contents[i])
        self._test_view.clear_replace_calls()

    def test_line_insert(self):
        # Update lines 1 and 3 with new content
        self._test_view.terminal_view_buffer_update["lines"] = [0, 2]
        disp = ["           "] * 5
        disp[0] = "test line 1"
        self._expected_buffer_contents[0] = "test line 1\n"
        disp[2] = "line 1     "
        self._expected_buffer_contents[2] = "line 1     \n"
        self._test_view.terminal_view_buffer_update["display"] = disp
        self._test_line_cmd.run(None)

        # Check that local copy of buffer is correct
        buffer_cache = self._test_view.terminal_view_buffer_contents
        for i in range(5):
            self.assertEqual(buffer_cache[i], self._expected_buffer_contents[i])

        # Check that replace calls are done correctly
        replaces = self._test_view.get_replace_calls()
        self.assertEqual(replaces[0].region.a, 0)
        self.assertEqual(replaces[0].region.b, 12)
        self.assertEqual(replaces[0].content, self._expected_buffer_contents[0])
        self.assertEqual(replaces[1].region.a, 24)
        self.assertEqual(replaces[1].region.b, 36)
        self.assertEqual(replaces[1].content, self._expected_buffer_contents[2])
        self._test_view.clear_replace_calls()


class terminal_buffer(unittest.TestCase):
    def test_view_size(self):
        # Set up test view
        test_view = sublime.SublimeViewStub(3)
        test_view.set_viewport_extent((300, 200))
        test_view.set_line_height(10)
        test_view.set_em_width(5)

        # Make test buffer
        buf = SublimeTerminalBuffer.SublimeTerminalBuffer(test_view, "sometitle")

        rows, cols = buf.view_size()
        self.assertEqual(rows, 20)
        self.assertEqual(cols, 58)  # Note the module subtracts two to avoid the edge

    def test_keypress_callback(self):
        # Set up test view
        test_view = sublime.SublimeViewStub(1337)

        # Make test buffer
        buf = SublimeTerminalBuffer.SublimeTerminalBuffer(test_view, "test")

        # Define test callback function
        expected_key = None
        expected_ctrl = False
        expected_alt = False

        def keypress_cb(key, ctrl=False, alt=False, shift=False, meta=False):
            self.assertEqual(key, expected_key)
            self.assertEqual(ctrl, expected_ctrl)
            self.assertEqual(alt, expected_alt)

        # Set callback
        buf.set_keypress_callback(keypress_cb)

        # Make the textcommand manually and execute it
        keypress_cmd = SublimeTerminalBuffer.TerminalViewKeypress(test_view)
        expected_key = "dummy_key"
        keypress_cmd.run(None, key=expected_key)

        # Now with modifiers
        expected_key = "a"
        expected_alt = True
        keypress_cmd.run(None, key=expected_key, alt=expected_alt)

        expected_key = "a"
        expected_alt = False
        expected_ctrl = True
        keypress_cmd.run(None, key=expected_key, ctrl=expected_ctrl)


class pyte_buffer_to_color_map(unittest.TestCase):
    def test_no_colors(self):
        buffer_factory = PyteBufferStubFactory(14, 37)
        pyte_buffer = buffer_factory.produce()
        lines = list(range(14))
        color_map = SublimeTerminalBuffer.convert_pyte_buffer_lines_to_colormap(pyte_buffer, lines)
        self.assertDictEqual(color_map, {})

    def test_lines_selection(self):
        lines = [2, 3, 6, 19]
        colors = ["red", "green", "magenta", "blue", "cyan"]
        buffer_factory = PyteBufferStubFactory(20, 10)
        for i in range(20):
            buffer_factory.set_color(i, 5, colors[i % len(colors)], "default")

        pyte_buffer = buffer_factory.produce()
        color_map = SublimeTerminalBuffer.convert_pyte_buffer_lines_to_colormap(pyte_buffer, lines)

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
        color_map = SublimeTerminalBuffer.convert_pyte_buffer_lines_to_colormap(pyte_buffer, lines)

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
        color_map = SublimeTerminalBuffer.convert_pyte_buffer_lines_to_colormap(pyte_buffer, lines)

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
            self.buffer.append([default_char] * nb_cols)

    def set_color(self, line, col, bg, fg):
        self.buffer[line][col] = CharStub(bg, fg)

    def produce(self):
        return self.buffer


class CharStub():
    def __init__(self, bg, fg):
        self.bg = bg
        self.fg = fg
