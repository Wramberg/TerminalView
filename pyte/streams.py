# -*- coding: utf-8 -*-
"""
    pyte.streams
    ~~~~~~~~~~~~

    This module provides three stream implementations with different
    features; for starters, here's a quick example of how streams are
    typically used:

    >>> import pyte
    >>>
    >>> class Dummy(object):
    ...     def __init__(self):
    ...         self.y = 0
    ...
    ...     def cursor_up(self, count=None):
    ...         self.y += count or 1
    ...
    >>> dummy = Dummy()
    >>> stream = pyte.Stream()
    >>> stream.attach(dummy)
    >>> stream.feed(u"\u001B[5A")  # Move the cursor up 5 rows.
    >>> dummy.y
    5

    :copyright: (c) 2011-2013 by Selectel, see AUTHORS for details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import os
import codecs
import sys
import warnings
from collections import defaultdict, namedtuple

from . import control as ctrl, escape as esc
from .compat import str

#: An entry in the :class:`~pyte.streams.Screen` listeners queue.
ListenerSpec = namedtuple("ListenerSpec", "screen only before after")


def noop(event):
    """A noop before-after hook for :class:`~pyte.streams.ListenerSpec`."""


class Stream(object):
    """A stream is a state machine that parses a stream of characters
    and dispatches events based on what it sees.

    .. note::

       Stream only accepts text as input, but if, for some reason,
       you need to feed it with bytes, consider using
       :class:`~pyte.streams.ByteStream` instead.

    .. seealso::

        `man console_codes <http://linux.die.net/man/4/console_codes>`_
            For details on console codes listed bellow in :attr:`basic`,
            :attr:`escape`, :attr:`csi`, :attr:`sharp` and :attr:`percent`.
    """

    #: Control sequences, which don't require any arguments.
    basic = {
        ctrl.BEL: "bell",
        ctrl.BS: "backspace",
        ctrl.HT: "tab",
        ctrl.LF: "linefeed",
        ctrl.VT: "linefeed",
        ctrl.FF: "linefeed",
        ctrl.CR: "carriage_return",
        ctrl.SO: "shift_out",
        ctrl.SI: "shift_in",
    }

    #: non-CSI escape sequences.
    escape = {
        esc.RIS: "reset",
        esc.IND: "index",
        esc.NEL: "linefeed",
        esc.RI: "reverse_index",
        esc.HTS: "set_tab_stop",
        esc.DECSC: "save_cursor",
        esc.DECRC: "restore_cursor",
    }

    #: "sharp" escape sequences -- ``ESC # <N>``.
    sharp = {
        esc.DECALN: "alignment_display",
    }

    #: "percent" escape sequences (Linux sequence to select character
    #: set) -- ``ESC % <C>``.
    percent = {
        esc.DEFAULT: "charset_default",
        esc.UTF8: "charset_utf8",
        esc.UTF8_OBSOLETE: "charset_utf8",
    }

    #: CSI escape sequences -- ``CSI P1;P2;...;Pn <fn>``.
    csi = {
        esc.ICH: "insert_characters",
        esc.CUU: "cursor_up",
        esc.CUD: "cursor_down",
        esc.CUF: "cursor_forward",
        esc.CUB: "cursor_back",
        esc.CNL: "cursor_down1",
        esc.CPL: "cursor_up1",
        esc.CHA: "cursor_to_column",
        esc.CUP: "cursor_position",
        esc.ED: "erase_in_display",
        esc.EL: "erase_in_line",
        esc.IL: "insert_lines",
        esc.DL: "delete_lines",
        esc.DCH: "delete_characters",
        esc.ECH: "erase_characters",
        esc.HPR: "cursor_forward",
        esc.DA: "report_device_attributes",
        esc.VPA: "cursor_to_line",
        esc.VPR: "cursor_down",
        esc.HVP: "cursor_position",
        esc.TBC: "clear_tab_stop",
        esc.SM: "set_mode",
        esc.RM: "reset_mode",
        esc.SGR: "select_graphic_rendition",
        esc.DSR: "report_device_status",
        esc.DECSTBM: "set_margins",
        esc.HPA: "cursor_to_column"
    }

    def __init__(self):
        self.listeners = []
        self.state = "stream"  # Only used for testing.
        self.parser = self._parser_fsm()
        self.parser.send(None)

    def consume(self, char):
        """Consumes a single string character and advance the state as
        necessary.

        :param str char: a character to consume.

        .. deprecated:: 0.5.0

           Use :meth:`feed` instead.
        """
        warnings.warn(".consume is deprecated and will be removed in "
                      "pyte 0.5.2. Please use .feed instead.",
                      category=DeprecationWarning)
        return self.feed(char)

    def feed(self, chars):
        """Consumes a string and advance the state as necessary.

        :param str chars: a string to feed from.
        """
        if not isinstance(chars, str):
            raise TypeError("{0} requires text input"
                            .format(self.__class__.__name__))

        send = self.parser.send
        for char in chars:
            send(char)

    def attach(self, screen, only=()):
        """Adds a given screen to the listener queue.

        :param pyte.screens.Screen screen: a screen to attach to.
        :param list only: a list of events you want to dispatch to a
                          given screen (empty by default, which means
                          -- dispatch all events).
        """
        before = getattr(screen, "__before__", noop)
        after = getattr(screen, "__after__", noop)
        self.listeners.append(ListenerSpec(screen, set(only), before, after))

    def detach(self, screen):
        """Removes a given screen from the listener queue and fails
        silently if it's not attached.

        :param pyte.screens.Screen screen: a screen to detach.
        """
        for idx, spec in enumerate(self.listeners):
            if screen is spec.screen:
                self.listeners.pop(idx)

    def dispatch(self, event, *args, **kwargs):
        """Dispatches an event.

        Event handlers are looked up implicitly in the screen's
        ``__dict__``, so, if a screen only wants to handle ``DRAW``
        events it should define a ``draw()`` method or pass
        ``only=["draw"]`` argument to :meth:`attach`.

        .. warning::

           If any of the attached listeners throws an exception, the
           subsequent callbacks are be aborted.

        :param str event: event to dispatch.
        """
        for screen, only, before, after in self.listeners:
            if only and event not in only:
                continue

            try:
                handler = getattr(screen, event)
            except AttributeError:
                continue

            before(event)
            handler(*args, **kwargs)
            after(event)

    def _parser_fsm(self):
        # In order to avoid getting KeyError exceptions below, we make sure
        # that these dictionaries resolve to ``"debug"``.
        basic = defaultdict(lambda: "debug", self.basic)
        escape = defaultdict(lambda: "debug", self.escape)
        sharp = defaultdict(lambda: "debug", self.sharp)
        percent = defaultdict(lambda: "debug", self.percent)
        csi = defaultdict(lambda: "debug", self.csi)

        dispatch = self.dispatch

        ESC, CSI, SP = ctrl.ESC, ctrl.CSI, ctrl.SP
        NUL_OR_DEL = [ctrl.NUL, ctrl.DEL]
        CAN_OR_SUB = [ctrl.CAN, ctrl.SUB]
        ALLOWED_IN_CSI = [ctrl.BEL, ctrl.BS, ctrl.HT, ctrl.LF, ctrl.VT,
                          ctrl.FF, ctrl.CR]
        while True:
            self.state = "stream"
            char = yield
            if char == ESC:
                # Most non-VT52 commands start with a left-bracket after the
                # escape and then a stream of parameters and a command; with
                # a single notable exception -- :data:`escape.DECOM` sequence,
                # which starts with a sharp.
                #
                # .. versionchanged:: 0.4.10
                #
                #    For compatibility with Linux terminal stream also
                #    recognizes ``ESC % C`` sequences for selecting control
                #    character set. However, in the current version these
                #    are noop.
                self.state = "escape"
                char = yield
                if char == "[":
                    char = CSI  # Go to CSI.
                else:
                    if char == "#":
                        self.state = "sharp"
                        dispatch(sharp[(yield)])
                    if char == "%":
                        self.state = "percent"
                        dispatch(percent[(yield)])
                    elif char in "()":
                        self.state = "charset"
                        dispatch("set_charset", (yield), mode=char)
                    else:
                        dispatch(escape[char])
                    continue  # Don't go to CSI.

            if char in basic:
                dispatch(basic[char])
            elif char == CSI:
                # All parameters are unsigned, positive decimal integers, with
                # the most significant digit sent first. Any parameter greater
                # than 9999 is set to 9999. If you do not specify a value, a 0
                # value is assumed.
                #
                # .. seealso::
                #
                #    `VT102 User Guide <http://vt100.net/docs/vt102-ug/>`_
                #        For details on the formatting of escape arguments.
                #
                #    `VT220 Programmer Ref. <http://vt100.net/docs/vt220-rm/>`_
                #        For details on the characters valid for use as
                #        arguments.
                self.state = "arguments"

                params = []
                current = ""
                private = False
                while True:
                    char = yield
                    if char == "?":
                        private = True
                    elif char in ALLOWED_IN_CSI:
                        dispatch(basic[char])
                    elif char == SP or char == ">":
                        # We don't handle secondary DA atm.
                        pass
                    elif char in CAN_OR_SUB:
                        # If CAN or SUB is received during a sequence, the
                        # current sequence is aborted; terminal displays the
                        # substitute character, followed by characters in the
                        # sequence received after CAN or SUB.
                        dispatch("draw", char)
                        break
                    elif char.isdigit():
                        current += char
                    else:
                        params.append(min(int(current or 0), 9999))

                        if char == ";":
                            current = ""
                        else:
                            if private:
                                dispatch(csi[char], *params, private=True)
                            else:
                                dispatch(csi[char], *params)
                            break  # CSI is finished.
            elif char not in NUL_OR_DEL:
                dispatch("draw", char)


class ByteStream(Stream):
    """A stream, which takes bytes (instead of strings) as input
    and tries to decode them using a given list of possible encodings.
    It uses :class:`codecs.IncrementalDecoder` internally, so broken
    bytes are not an issue.

    By default, the following decoding strategy is used:

    * First, try strict ``"utf-8"``, proceed if received and
      :exc:`UnicodeDecodeError` ...
    * Try strict ``"cp437"``, failed? move on ...
    * Use ``"utf-8"`` with invalid bytes replaced -- this one will
      always succeed.

    >>> stream = ByteStream()
    >>> stream.feed(b"foo".decode("utf-8"))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyte/streams.py", line 367, in feed
        "{0} requires input in bytes".format(self.__class__.__name__))
    TypeError: ByteStream requires input in bytes
    >>> stream.feed(b"foo")

    :param list encodings: a list of ``(encoding, errors)`` pairs,
                           where the first element is encoding name,
                           ex: ``"utf-8"`` and second defines how
                           decoding errors should be handled; see
                           :meth:`str.decode` for possible values.
    """

    def __init__(self, encodings=None):
        encodings = encodings or [
            ("utf-8", "strict"),
            ("cp437", "strict"),
            ("utf-8", "replace")
        ]

        self.buffer = b"", 0
        self.decoders = [codecs.getincrementaldecoder(encoding)(errors)
                         for encoding, errors in encodings]

        super(ByteStream, self).__init__()

    def feed(self, chars):
        if not isinstance(chars, bytes):
            raise TypeError(
                "{0} requires input in bytes".format(self.__class__.__name__))

        for idx, decoder in enumerate(self.decoders):
            decoder.setstate(self.buffer)

            try:
                chars = decoder.decode(chars)
            except UnicodeDecodeError:
                continue
            else:
                self.buffer = decoder.getstate()
                return super(ByteStream, self).feed(chars)

        raise ValueError("unknown encoding")


class DebugStream(ByteStream):
    r"""Stream, which dumps a subset of the dispatched events to a given
    file-like object (:data:`sys.stdout` by default).

    >>> stream = DebugStream()
    >>> stream.feed("\x1b[1;24r\x1b[4l\x1b[24;1H\x1b[0;10m")
    SET_MARGINS 1; 24
    RESET_MODE 4
    CURSOR_POSITION 24; 1
    SELECT_GRAPHIC_RENDITION 0; 10

    :param file to: a file-like object to write debug information to.
    :param list only: a list of events you want to debug (empty by
                      default, which means -- debug all events).
    """

    def __init__(self, to=sys.stdout, only=(), *args, **kwargs):
        super(DebugStream, self).__init__(*args, **kwargs)

        def safe_str(chunk):
            if isinstance(chunk, bytes):
                chunk = chunk.decode("utf-8")
            elif not isinstance(chunk, str):
                chunk = str(chunk)

            return chunk

        class Bugger(object):
            __before__ = __after__ = lambda *args: None

            def __getattr__(self, event):
                def inner(*args, **kwargs):
                    to.write(event.upper() + " ")
                    to.write("; ".join(map(safe_str, args)))
                    to.write(" ")
                    to.write(", ".join("{0}: {1}".format(k, safe_str(v))
                                       for k, v in kwargs.items()))
                    to.write(os.linesep)
                return inner

        self.attach(Bugger(), only=only)
