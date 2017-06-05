import sys
import os

dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir_path)

import unittest
import time

# Module to test
import LinuxPty


class BashTestBase(unittest.TestCase):
    def setUp(self):
        """
        Start bash shell
        """
        cwd = os.path.dirname(os.path.abspath(__file__))
        self.linux_pty_bash = LinuxPty.LinuxPty(["/bin/bash", "-l"], cwd)
        self.assertTrue(self.linux_pty_bash.is_running())

        # Update screen size to avoid wrapping during test
        self.linux_pty_bash.update_screen_size(80, 500)

        # Read the initial prompt
        self.linux_pty_bash.receive_output(1024, timeout=0.2)

    def tearDown(self):
        """
        Stop bash shell
        """
        self.assertTrue(self.linux_pty_bash.is_running())
        self.linux_pty_bash.stop()
        self.assertFalse(self.linux_pty_bash.is_running())

    def _reset_shell_output(self):
        self.linux_pty_bash.send_keypress("c", ctrl=True)
        self._read_bytes_from_shell(1024, timeout=0.1)
        self.linux_pty_bash.send_keypress("l", ctrl=True)
        self._read_bytes_from_shell(1024, timeout=0.1)

    def _prepare_verbatim_insert(self):
        """
        Prepare verbatim insert so the shell echoes the pressed key
        """
        self.linux_pty_bash.send_keypress("v", ctrl=True)
        # Read bytes if shell sends any
        self._read_bytes_from_shell(1024, timeout=0.1)

    def _read_bytes_from_shell(self, num_bytes, timeout=1):
        """
        Try to read X bytes from shell but timeout after Y seconds
        """
        data = b''
        start = time.time()
        while (len(data) < num_bytes) and (time.time() < start + timeout):
            new_data = self.linux_pty_bash.receive_output(2048, timeout=0.1)
            if new_data is not None:
                data = data + new_data

        return data


class BashIOTest(BashTestBase):
    def test_single_ascii_chars(self):
        """
        Ensure that the LinuxPty module can send all single chars, numbers,
        signs to bash and that they are received correctly
        """
        # Make a list of all single chars/numbers etc. from ascii value 33 to
        # 126
        input_list = [chr(a) for a in range(33, 127)]

        # Send each input to the shell
        for char in input_list:
            self.linux_pty_bash.send_keypress(char)
            data = self.linux_pty_bash.receive_output(32, timeout=0.01)
            self.assertEqual(len(data), 1)
            self.assertEqual(data.decode('ascii'), char)

    def test_special_keys(self):
        """
        Ensure special keys like home, end, space, enter, arrow keys, etc. are
        sent and handled corretly by the shell
        """
        # Tested in Linux term (TERM=linux) on Centos 7 the shell responded with
        # the following.
        keymap = {
            "enter": "^M",
            "backspace": "^?",
            "tab": "   ",
            "space": " ",
            "escape": "^[",
            "down": "^[[B",
            "up": "^[[A",
            "right": "^[[C",
            "left": "^[[D",
            "home": "^[[1~",
            "end": "^[[4~",
            "pageup": "^[[5~",
            "pagedown": "^[[6~",
            "delete": "^[[3~",
            "insert": "^[[2~",
        }

        # Send each input to the shell
        for key in keymap:
            # Use verbatim insert to see which keys are pressed
            self._prepare_verbatim_insert()

            # Send keypress
            self.linux_pty_bash.send_keypress(key)

            # Check response
            if key == "tab":
                expected_response = " "
                data = self._read_bytes_from_shell(64, timeout=0.1)
                data = data.decode('ascii')
                for char in data:
                    self.assertEqual(char, " ", msg="Non-space in tab")
            else:
                expected_response = keymap[key]
                data = self._read_bytes_from_shell(len(expected_response))
                fail_msg = "Key: [%s], Data: [%s]" % (key, data.decode('ascii'))
                self.assertEqual(len(data), len(expected_response), msg=fail_msg)
                self.assertEqual(data.decode('ascii'), expected_response, msg=fail_msg)

    def test_ctrl_key_combinations(self):
        """
        Ensure that the LinuxPty module can send all ctrl + char combinations to
        bash and that they are received correctly
        """
        # Make a list of all single chars from ascii value 97 to 122
        input_list = [chr(a) for a in range(97, 123)]

        # Send each input to the shell
        for char in input_list:
            # Use verbatim insert to see which keys are pressed
            self._prepare_verbatim_insert()

            # Send key
            self.linux_pty_bash.send_keypress(char, ctrl=True)

            # Read back result we expect ^A, ^B, ^C, etc. Note that the ctrl+i
            # and ctrl+j combination are ignored and translates differently
            if char == "i":
                data = self._read_bytes_from_shell(64, timeout=0.1)
                data = data.decode('ascii')
                # Ensure data is only spaces
                for char in data:
                    self.assertEqual(char, " ")
            elif char == "j":
                data = self._read_bytes_from_shell(3)
                self.assertEqual(len(data), 3)
                self.assertEqual(data.decode('ascii'), "\r\n\r")
            else:
                data = self._read_bytes_from_shell(2)
                self.assertEqual(len(data), 2)
                self.assertEqual(data.decode('ascii'), "^" + char.upper())

    def test_ctrl_key_sign_combinations(self):
        """
        Ensure that the LinuxPty module can send all ctrl + sign combinations to
        bash and that they are received correctly
        """
        # Make a list of signs to test (note that arrow keys are included)
        keymap = {
            "[": "^[",
            "\\": "^\\",
            "]": "^]",
            "^": "^^",
            "_": "^_",
            "?": "^?",
            "left": "^[[1;5D",
            "right": "^[[1;5C",
        }

        # Send each input to the shell
        for sign in keymap:
            # Use verbatim insert to see which keys are pressed
            self._prepare_verbatim_insert()

            # Send key
            self.linux_pty_bash.send_keypress(sign, ctrl=True)

            # Read back result we expect ^[, ^\, ^], etc.
            expected_response = keymap[sign]
            data = self._read_bytes_from_shell(len(expected_response))
            fail_msg = "Sign: [%s], Data: [%s]" % (sign, data.decode('ascii'))
            self.assertEqual(len(data), len(expected_response), msg=fail_msg)
            self.assertEqual(data.decode('ascii'), expected_response, msg=fail_msg)

    def test_alt_key_combinations(self):
        """
        Ensure that the LinuxPty module can send all alt + char combinations to
        bash and that they are received correctly
        """
        # Make a list of all single chars from ascii value 97 to 122
        input_list = [chr(a) for a in range(97, 123)]

        # Send each input to the shell
        for char in input_list:
            # Use verbatim insert to see which keys are pressed
            self._prepare_verbatim_insert()

            # Send key
            self.linux_pty_bash.send_keypress(char, alt=True)

            # Read back result we expect ^[a, ^[b, ^[c, etc.
            data = self._read_bytes_from_shell(3)
            fail_msg = "Char: [%s], Data: [%s]" % (char, data.decode('ascii'))
            self.assertEqual(len(data), 3, msg=fail_msg)
            self.assertEqual(data.decode('ascii'), "^[" + char, msg=fail_msg)


class BashResizeTest(BashTestBase):
    def test_tput_output(self):
        screen_sizes = [(80, 500), (800, 45), (30, 250)]

        # Get the screen size a shell script reads when run in the terminal
        cmd = "sh echo_screen_size.sh"
        for size in screen_sizes:
            self.linux_pty_bash.update_screen_size(size[0], size[1])
            self._reset_shell_output()
            for char in cmd:
                self.linux_pty_bash.send_keypress(char)

            # Read the prompt and chars we dont need it
            self._read_bytes_from_shell(512, timeout=0.1)
            self.linux_pty_bash.send_keypress("enter")

            # Read output of shell script
            data = self._read_bytes_from_shell(512, timeout=0.1)
            data = data.decode('ascii')
            data = data.split("\r\n")
            cols = data[1]
            lines = data[2]
            self.assertEqual(int(lines), size[0])
            self.assertEqual(int(cols), size[1])


if __name__ == "__main__":
    unittest.main()
