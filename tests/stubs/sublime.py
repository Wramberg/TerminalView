import sublime_api
import sys

class _LogWriter:
    def flush(self):
        pass

    def write(self, s):
        sublime_api.log_message(s)

# sys.stdout = _LogWriter()
# sys.stderr = _LogWriter()

ENCODED_POSITION = 1
TRANSIENT = 4
FORCE_GROUP = 8
IGNORECASE = 2
LITERAL = 1
MONOSPACE_FONT = 1

DRAW_EMPTY = 1
HIDE_ON_MINIMAP = 2
DRAW_EMPTY_AS_OVERWRITE = 4
PERSISTENT = 16
# Deprecated, use DRAW_NO_FILL instead
DRAW_OUTLINED = 32
DRAW_NO_FILL = 32
DRAW_NO_OUTLINE = 256
DRAW_SOLID_UNDERLINE = 512
DRAW_STIPPLED_UNDERLINE = 1024
DRAW_SQUIGGLY_UNDERLINE = 2048
HIDDEN = 128

OP_EQUAL = 0
OP_NOT_EQUAL = 1
OP_REGEX_MATCH = 2
OP_NOT_REGEX_MATCH = 3
OP_REGEX_CONTAINS = 4
OP_NOT_REGEX_CONTAINS = 5
CLASS_WORD_START = 1
CLASS_WORD_END = 2
CLASS_PUNCTUATION_START = 4
CLASS_PUNCTUATION_END = 8
CLASS_SUB_WORD_START = 16
CLASS_SUB_WORD_END = 32
CLASS_LINE_START = 64
CLASS_LINE_END = 128
CLASS_EMPTY_LINE = 256
INHIBIT_WORD_COMPLETIONS = 8
INHIBIT_EXPLICIT_COMPLETIONS = 16

def version():
    return sublime_api.version()

def platform():
    return sublime_api.platform()

def arch():
    return sublime_api.architecture()

def channel():
    return sublime_api.channel()

def executable_path():
    return sublime_api.executable_path()

def executable_hash():
    import hashlib
    return (version(), platform() + '_' + arch(),
        hashlib.md5(open(executable_path(), 'rb').read()).hexdigest())

def packages_path():
    return sublime_api.packages_path()

def installed_packages_path():
    return sublime_api.installed_packages_path()

def cache_path():
    """ Returns the path where Sublime Text stores cache files """
    return sublime_api.cache_path()

def status_message(msg):
    sublime_api.status_message(msg)

def error_message(msg):
    sublime_api.error_message(msg)

def message_dialog(msg):
    sublime_api.message_dialog(msg)

def ok_cancel_dialog(msg, ok_title = ""):
    return sublime_api.ok_cancel_dialog(msg, ok_title)

def run_command(cmd, args = None):
    sublime_api.run_command(cmd, args)

def get_clipboard(size_limit = 16777216):
    """ Returns the content of the clipboard, for performance reason if the size
    of the clipboard content is bigger than size_limit, empty string will be returned
    """
    return sublime_api.get_clipboard(size_limit)

def set_clipboard(text):
    return sublime_api.set_clipboard(text)

def log_commands(flag):
    sublime_api.log_commands(flag)

def log_input(flag):
    """ Enables or disables input logging. This is useful to find the names of certain keys on the keyboard """
    sublime_api.log_input(flag)

def log_result_regex(flag):
    """ Enables or disables result regex logging. This is useful when trying to debug file_regex and line_regex in build systems """
    sublime_api.log_result_regex(flag)

def log_indexing(flag):
    sublime_api.log_indexing(flag)

def score_selector(scope_name, selector):
    return sublime_api.score_selector(scope_name, selector)

def load_resource(name):
    s = sublime_api.load_resource(name)
    if s == None:
        raise IOError("resource not found")
    return s

def load_binary_resource(name):
    bytes = sublime_api.load_binary_resource(name)
    if bytes == None:
        raise IOError("resource not found")
    return bytes

def find_resources(pattern):
    return sublime_api.find_resources(pattern)

def encode_value(val, pretty = False):
    return sublime_api.encode_value(val, pretty)

def decode_value(data):
    val, err = sublime_api.decode_value(data)

    if err:
        raise ValueError(err)

    return val

def load_settings(base_name):
    settings_id = sublime_api.load_settings(base_name)
    return Settings(settings_id)

def save_settings(base_name):
    sublime_api.save_settings(base_name)

def set_timeout(f, timeout_ms = 0):
    """ Schedules a function to be called in the future. Sublime Text will block while the function is running """
    sublime_api.set_timeout(f, timeout_ms)

def set_timeout_async(f, timeout_ms = 0):
    """ Schedules a function to be called in the future. The function will be
    called in a worker thread, and Sublime Text will not block while the function is running """
    sublime_api.set_timeout_async(f, timeout_ms)

def active_window():
    return Window(sublime_api.active_window())

def windows():
    return [Window(id) for id in sublime_api.windows()]

def get_macro():
    return sublime_api.get_macro()

class Window(object):
    def __init__(self, id):
        self.window_id = id
        self.settings_object = None
        self.template_settings_object = None

    def __eq__(self, other):
        return isinstance(other, Window) and other.window_id == self.window_id

    def __bool__(self):
        return self.window_id != 0

    def id(self):
        return self.window_id

    def is_valid(self):
        return sublime_api.window_num_groups(self.window_id) != 0

    def hwnd(self):
        """ Platform specific window handle, only returns a meaningful result under Windows """
        return sublime_api.window_system_handle(self.window_id)

    def active_sheet(self):
        sheet_id = sublime_api.window_active_sheet(self.window_id)
        if sheet_id == 0:
            return None
        else:
            return Sheet(sheet_id)

    def active_view(self):
        view_id = sublime_api.window_active_view(self.window_id)
        if view_id == 0:
            return None
        else:
            return View(view_id)

    def run_command(self, cmd, args = None):
        sublime_api.window_run_command(self.window_id, cmd, args)

    def new_file(self, flags = 0, syntax = ""):
        """ flags must be either 0 or TRANSIENT """
        return View(sublime_api.window_new_file(self.window_id, flags, syntax))

    def open_file(self, fname, flags = 0, group = -1):
        """
        valid bits for flags are:
        ENCODED_POSITION: fname name may have :row:col or :row suffix
        TRASIENT: don't add the file to the list of open buffers
        FORCE_GROUP: don't select the file if it's opened in a different group
        """
        return View(sublime_api.window_open_file(self.window_id, fname, flags, group))

    def find_open_file(self, fname):
        view_id = sublime_api.window_find_open_file(self.window_id, fname)
        if view_id == 0:
            return None
        else:
            return View(view_id)

    def num_groups(self):
        return sublime_api.window_num_groups(self.window_id)

    def active_group(self):
        return sublime_api.window_active_group(self.window_id)

    def focus_group(self, idx):
        sublime_api.window_focus_group(self.window_id, idx)

    def focus_sheet(self, sheet):
        if sheet:
            sublime_api.window_focus_sheet(self.window_id, sheet.sheet_id)

    def focus_view(self, view):
        if view:
            sublime_api.window_focus_view(self.window_id, view.view_id)

    def get_sheet_index(self, sheet):
        if sheet:
            return sublime_api.window_get_sheet_index(self.window_id, sheet.sheet_id)
        else:
            return (-1, -1)

    def get_view_index(self, view):
        if view:
            return sublime_api.window_get_view_index(self.window_id, view.view_id)
        else:
            return (-1, -1)

    def set_sheet_index(self, sheet, group, idx):
        sublime_api.window_set_sheet_index(self.window_id, sheet.sheet_id, group, idx)

    def set_view_index(self, view, group, idx):
        sublime_api.window_set_view_index(self.window_id, view.view_id, group, idx)

    def sheets(self):
        sheet_ids = sublime_api.window_sheets(self.window_id)
        return [Sheet(x) for x in sheet_ids]

    def views(self):
        view_ids = sublime_api.window_views(self.window_id)
        return [View(x) for x in view_ids]

    def active_sheet_in_group(self, group):
        sheet_id = sublime_api.window_active_sheet_in_group(self.window_id, group)
        if sheet_id == 0:
            return None
        else:
            return Sheet(sheet_id)

    def active_view_in_group(self, group):
        view_id = sublime_api.window_active_view_in_group(self.window_id, group)
        if view_id == 0:
            return None
        else:
            return View(view_id)

    def sheets_in_group(self, group):
        sheet_ids = sublime_api.window_sheets_in_group(self.window_id, group)
        return [Sheet(x) for x in sheet_ids]

    def views_in_group(self, group):
        view_ids = sublime_api.window_views_in_group(self.window_id, group)
        return [View(x) for x in view_ids]

    def transient_sheet_in_group(self, group):
        sheet_id = sublime_api.window_transient_sheet_in_group(self.window_id, group)
        if sheet_id != 0:
            return Sheet(sheet_id)
        else:
            return None

    def transient_view_in_group(self, group):
        view_id = sublime_api.window_transient_view_in_group(self.window_id, group)
        if view_id != 0:
            return View(view_id)
        else:
            return None

    def layout(self):
        return sublime_api.window_get_layout(self.window_id)

    def get_layout(self):
        """ get_layout() is deprecated, use layout() """
        return sublime_api.window_get_layout(self.window_id)

    def set_layout(self, layout):
        sublime_api.window_set_layout(self.window_id, layout)

    def create_output_panel(self, name):
        return View(sublime_api.window_create_output_panel(self.window_id, name))

    def get_output_panel(self, name):
        """ deprecated, use create_output_panel """
        return self.create_output_panel(name)

    def show_input_panel(self, caption, initial_text, on_done, on_change, on_cancel):
        """ on_done and on_change should accept a string argument, on_cancel should have no arguments """
        return View(sublime_api.window_show_input_panel(self.window_id,
            caption, initial_text, on_done, on_change, on_cancel))

    def show_quick_panel(self, items, on_select, flags = 0, selected_index = -1, on_highlight = None):
        """
        on_select is called when the the quick panel is finished, and should accept a single integer, specifying which item was selected, or -1 for none
        on_highlight is called when the quick panel is still active, and indicates the current highlighted index
        """
        items_per_row = 1
        flat_items = items
        if len(items) > 0 and isinstance(items[0], list):
            items_per_row = len(items[0])
            flat_items = []

            for i in range(len(items)):
                if isinstance(items[i], str):
                    flat_items.append(items[i])
                    for j in range(1, items_per_row):
                        flat_items.append("")
                else:
                    for j in range(items_per_row):
                        flat_items.append(items[i][j])

        return sublime_api.window_show_quick_panel(self.window_id, flat_items,
            items_per_row, on_select, on_highlight, flags, selected_index)

    def folders(self):
        return sublime_api.window_folders(self.window_id)

    def project_file_name(self):
        name = sublime_api.window_project_file_name(self.window_id)
        if len(name) == 0:
            return None
        else:
            return name

    def project_data(self):
        return sublime_api.window_get_project_data(self.window_id)

    def set_project_data(self, v):
        sublime_api.window_set_project_data(self.window_id, v)

    def settings(self):
        """ Per-window settings, the contents are persisted in the session """
        if not self.settings_object:
            self.settings_object = Settings(
                sublime_api.window_settings(self.window_id))

        return self.settings_object

    def template_settings(self):
        """ Per-window settings that are persisted in the session, and duplicated into new windows """
        if not self.template_settings_object:
            self.template_settings_object = Settings(
                sublime_api.window_template_settings(self.window_id))

        return self.template_settings_object

    def lookup_symbol_in_index(self, sym):
        """ Finds all files and locations where sym in defined, using the symbol index """
        return sublime_api.window_lookup_symbol(self.window_id, sym)

    def lookup_symbol_in_open_files(self, sym):
        """ Finds all files and locations where sym in defined, searching through open files """
        return sublime_api.window_lookup_symbol_in_open_files(self.window_id, sym)


class Edit(object):
    def __init__(self, token):
        self.edit_token = token

class Region(object):
    def __init__(self, a, b = None, xpos = -1):
        if b == None:
            b = a
        self.a = a
        self.b = b
        self.xpos = xpos

    def __str__(self):
        return "(" + str(self.a) + ", " + str(self.b) + ")"

    def __repr__(self):
        return "(" + str(self.a) + ", " + str(self.b) + ")"

    def __len__(self):
        return self.size()

    def __eq__(self, rhs):
        return isinstance(rhs, Region) and self.a == rhs.a and self.b == rhs.b

    def __lt__(self, rhs):
        lhs_begin = self.begin()
        rhs_begin = rhs.begin()

        if lhs_begin == rhs_begin:
            return self.end() < rhs.end()
        else:
            return lhs_begin < rhs_begin

    def empty(self):
        return self.a == self.b

    def begin(self):
        if self.a < self.b:
            return self.a
        else:
            return self.b

    def end(self):
        if self.a < self.b:
            return self.b
        else:
            return self.a

    def size(self):
        return abs(self.a - self.b)

    def contains(self, x):
        if isinstance(x, Region):
            return self.contains(x.a) and self.contains(x.b)
        else:
            return x >= self.begin() and x <= self.end()

    def cover(self, rhs):
        a = min(self.begin(), rhs.begin())
        b = max(self.end(), rhs.end())

        if self.a < self.b:
            return Region(a, b)
        else:
            return Region(b, a)

    def intersection(self, rhs):
        if self.end() <= rhs.begin():
            return Region(0)
        if self.begin() >= rhs.end():
            return Region(0)

        return Region(max(self.begin(), rhs.begin()), min(self.end(), rhs.end()))

    def intersects(self, rhs):
        lb = self.begin()
        le = self.end()
        rb = rhs.begin()
        re = rhs.end()

        return ((lb == rb and le == re) or
            (rb > lb and rb < le) or (re > lb and re < le) or
            (lb > rb and lb < re) or (le > rb and le < re))

class Selection(object):
    def __init__(self, id):
        self.view_id = id

    def __len__(self):
        return sublime_api.view_selection_size(self.view_id)

    def __getitem__(self, index):
        r = sublime_api.view_selection_get(self.view_id, index)
        if r.a == -1:
            raise IndexError()
        return r

    def __delitem__(self, index):
        sublime_api.view_selection_erase(self.view_id, index)

    def __eq__(self, rhs):
        return rhs != None and list(self) == list(rhs)

    def __lt__(self, rhs):
        return rhs != None and list(self) < list(rhs)

    def __bool__(self):
        return self.view_id != 0

    def is_valid(self):
        return sublime_api.view_buffer_id(self.view_id) != 0

    def clear(self):
        sublime_api.view_selection_clear(self.view_id)

    def add(self, x):
        if isinstance(x, Region):
            sublime_api.view_selection_add_region(self.view_id, x.a, x.b, x.xpos)
        else:
            sublime_api.view_selection_add_point(self.view_id, x)

    def add_all(self, regions):
        for r in regions:
            self.add(r)

    def subtract(self, region):
        sublime_api.view_selection_subtract_region(self.view_id, region.a, region.b)

    def contains(self, region):
        return sublime_api.view_selection_contains(self.view_id, region.a, region.b)

class Sheet(object):
    def __init__(self, id):
        self.sheet_id = id

    def __eq__(self, other):
        return isinstance(other, Sheet) and other.sheet_id == self.sheet_id

    def id(self):
        return self.sheet_id

    def window(self):
        window_id = sublime_api.sheet_window(self.sheet_id)
        if window_id == 0:
            return None
        else:
            return Window(window_id)

class View(object):
    def __init__(self, id):
        self.view_id = id
        self.selection = Selection(id)
        self.settings_object = None

    def __len__(self):
        return self.size()

    def __eq__(self, other):
        return isinstance(other, View) and other.view_id == self.view_id

    def __bool__(self):
        return self.view_id != 0

    def id(self):
        return self.view_id

    def buffer_id(self):
        return sublime_api.view_buffer_id(self.view_id)

    def is_valid(self):
        """ Returns true if the View is still a valid handle. Will return False for a closed view, for example. """
        return sublime_api.view_buffer_id(self.view_id) != 0

    def window(self):
        window_id = sublime_api.view_window(self.view_id)
        if window_id == 0:
            return None
        else:
            return Window(window_id)

    def file_name(self):
        name = sublime_api.view_file_name(self.view_id)
        if len(name) == 0:
            return None
        else:
            return name

    def close(self):
        window_id = sublime_api.view_window(self.view_id)
        return sublime_api.window_close_file(window_id, self.view_id)

    def retarget(self, new_fname):
        sublime_api.view_retarget(self.view_id, new_fname)

    def name(self):
        return sublime_api.view_get_name(self.view_id)

    def set_name(self, name):
        sublime_api.view_set_name(self.view_id, name)

    def is_loading(self):
        return sublime_api.view_is_loading(self.view_id)

    def is_dirty(self):
        return sublime_api.view_is_dirty(self.view_id)

    def is_read_only(self):
        return sublime_api.view_is_read_only(self.view_id)

    def set_read_only(self, read_only):
        return sublime_api.view_set_read_only(self.view_id, read_only)

    def is_scratch(self):
        return sublime_api.view_is_scratch(self.view_id)

    def set_scratch(self, scratch):
        """ Sets the scratch flag on the text buffer. When a modified scratch buffer is closed, it will be closed without prompting to save. """
        return sublime_api.view_set_scratch(self.view_id, scratch)

    def encoding(self):
        return sublime_api.view_encoding(self.view_id)

    def set_encoding(self, encoding_name):
        return sublime_api.view_set_encoding(self.view_id, encoding_name)

    def line_endings(self):
        return sublime_api.view_line_endings(self.view_id)

    def set_line_endings(self, line_ending_name):
        return sublime_api.view_set_line_endings(self.view_id, line_ending_name)

    def size(self):
        return sublime_api.view_size(self.view_id)

    def begin_edit(self, edit_token, cmd, args = None):
        sublime_api.view_begin_edit(self.view_id, edit_token, cmd, args)
        return Edit(edit_token)

    def end_edit(self, edit):
        sublime_api.view_end_edit(self.view_id, edit.edit_token)
        edit.edit_token = 0

    def is_in_edit(self):
        return sublime_api.view_is_in_edit(self.view_id)

    def insert(self, edit, pt, text):
        if edit.edit_token == 0:
            raise ValueError("Edit objects may not be used after the TextCommand's run method has returned")

        return sublime_api.view_insert(self.view_id, edit.edit_token, pt, text)

    def erase(self, edit, r):
        if edit.edit_token == 0:
            raise ValueError("Edit objects may not be used after the TextCommand's run method has returned")

        sublime_api.view_erase(self.view_id, edit.edit_token, r)

    def replace(self, edit, r, text):
        if edit.edit_token == 0:
            raise ValueError("Edit objects may not be used after the TextCommand's run method has returned")

        sublime_api.view_replace(self.view_id, edit.edit_token, r, text)

    def change_count(self):
        """ The change_count is incremented whenever the underlying buffer is modified """
        return sublime_api.view_change_count(self.view_id)

    def run_command(self, cmd, args = None):
        sublime_api.view_run_command(self.view_id, cmd, args)

    def sel(self):
        return self.selection

    def substr(self, x):
        if isinstance(x, Region):
            return sublime_api.view_cached_substr(self.view_id, x.a, x.b)
        else:
            s = sublime_api.view_cached_substr(self.view_id, x, x + 1)
            # S2 backwards compat
            if len(s) == 0:
                return "\x00";
            else:
                return s

    def find(self, pattern, start_pt, flags = 0):
        return sublime_api.view_find(self.view_id, pattern, start_pt, flags)

    def find_all(self, pattern, flags = 0, fmt = None, extractions = None):
        if fmt == None:
            return sublime_api.view_find_all(self.view_id, pattern, flags)
        else:
            results = sublime_api.view_find_all_with_contents(self.view_id, pattern, flags, fmt)
            ret = []
            for region, contents in results:
                ret.append(region)
                extractions.append(contents)
            return ret

    def settings(self):
        if not self.settings_object:
            self.settings_object = Settings(sublime_api.view_settings(self.view_id))

        return self.settings_object

    def meta_info(self, key, pt):
        return sublime_api.view_meta_info(self.view_id, key, pt)

    def extract_scope(self, pt):
        return sublime_api.view_extract_scope(self.view_id, pt)

    def scope_name(self, pt):
        return sublime_api.view_scope_name(self.view_id, pt)

    def match_selector(self, pt, selector):
        return sublime_api.view_match_selector(self.view_id, pt, selector)

    def score_selector(self, pt, selector):
        return sublime_api.view_score_selector(self.view_id, pt, selector)

    def find_by_selector(self, selector):
        return sublime_api.view_find_by_selector(self.view_id, selector)

    def indented_region(self, pt):
        return sublime_api.view_indented_region(self.view_id, pt)

    def indentation_level(self, pt):
        return sublime_api.view_indentation_level(self.view_id, pt)

    def has_non_empty_selection_region(self):
        return sublime_api.view_has_non_empty_selection_region(self.view_id)

    def lines(self, r):
        return sublime_api.view_lines(self.view_id, r)

    def split_by_newlines(self, r):
        return sublime_api.view_split_by_newlines(self.view_id, r)

    def line(self, x):
        if isinstance(x, Region):
            return sublime_api.view_line_from_region(self.view_id, x)
        else:
            return sublime_api.view_line_from_point(self.view_id, x)

    def full_line(self, x):
        if isinstance(x, Region):
            return sublime_api.view_full_line_from_region(self.view_id, x)
        else:
            return sublime_api.view_full_line_from_point(self.view_id, x)

    def word(self, x):
        if isinstance(x, Region):
            return sublime_api.view_word_from_region(self.view_id, x)
        else:
            return sublime_api.view_word_from_point(self.view_id, x)

    def classify(self, pt):
        """ Classifies pt, returning a bitwise OR of zero or more of these flags:
        CLASS_WORD_START
        CLASS_WORD_END
        CLASS_PUNCTUATION_START
        CLASS_PUNCTUATION_END
        CLASS_SUB_WORD_START
        CLASS_SUB_WORD_END
        CLASS_LINE_START
        CLASS_LINE_END
        CLASS_EMPTY_LINE
        """

        return sublime_api.view_classify(self.view_id, pt)

    def find_by_class(self, pt, forward, classes, separators = ""):
        return sublime_api.view_find_by_class(self.view_id, pt, forward, classes, separators)

    def expand_by_class(self, x, classes, separators = ""):
        if isinstance(x, Region):
            return sublime_api.view_expand_by_class(self.view_id, x.a, x.b, classes, separators)
        else:
            return sublime_api.view_expand_by_class(self.view_id, x, x, classes, separators)

    def rowcol(self, tp):
        return sublime_api.view_row_col(self.view_id, tp)

    def text_point(self, row, col):
        """ Converts a row and column into a text point """
        return sublime_api.view_text_point(self.view_id, row, col)

    def visible_region(self):
        """ Returns the approximate visible region """
        return sublime_api.view_visible_region(self.view_id)

    def show(self, x, show_surrounds = True):
        """ Scrolls the view to reveal x, which may be a Region or point """
        if isinstance(x, Region):
            return sublime_api.view_show_region(self.view_id, x, show_surrounds)
        if isinstance(x, Selection):
            for i in x:
                return sublime_api.view_show_region(self.view_id, i, show_surrounds)
        else:
            return sublime_api.view_show_point(self.view_id, x, show_surrounds)

    def show_at_center(self, x):
        """ Scrolls the view to center on x, which may be a Region or point """
        if isinstance(x, Region):
            return sublime_api.view_show_region_at_center(self.view_id, x)
        else:
            return sublime_api.view_show_point_at_center(self.view_id, x)

    def viewport_position(self):
        """ Returns the (x, y) scroll position of the view in layout coordinates """
        return sublime_api.view_viewport_position(self.view_id)

    def set_viewport_position(self, xy, animate = True):
        """ Scrolls the view to the given position in layout coordinates """
        return sublime_api.view_set_viewport_position(self.view_id, xy, animate)

    def viewport_extent(self):
        """ Returns the width and height of the viewport, in layout coordinates """
        return sublime_api.view_viewport_extents(self.view_id)

    def layout_extent(self):
        """ Returns the total height and width of the document, in layout coordinates """
        return sublime_api.view_layout_extents(self.view_id)

    def text_to_layout(self, tp):
        """ Converts a text point to layout coordinates """
        return sublime_api.view_text_to_layout(self.view_id, tp)

    def layout_to_text(self, xy):
        """ Converts a point in layout coordinates to a text coodinate """
        return sublime_api.view_layout_to_text(self.view_id, xy)

    def line_height(self):
        """ Returns the height of a line in layout coordinates """
        return sublime_api.view_line_height(self.view_id)

    def em_width(self):
        """ Returns the em-width of the current font in layout coordinates """
        return sublime_api.view_em_width(self.view_id)

    def is_folded(self, sr):
        return sublime_api.view_is_folded(self.view_id, sr)

    def folded_regions(self):
        return sublime_api.view_folded_regions(self.view_id)

    def fold(self, x):
        if isinstance(x, Region):
            return sublime_api.view_fold_region(self.view_id, x)
        else:
            return sublime_api.view_fold_regions(self.view_id, x)

    def unfold(self, x):
        if isinstance(x, Region):
            return sublime_api.view_unfold_region(self.view_id, x)
        else:
            return sublime_api.view_unfold_regions(self.view_id, x)

    def add_regions(self, key, regions, scope = "", icon = "", flags = 0):
        # S2 has an add_regions overload that accepted flags as the 5th
        # positional argument, however this usage is no longer supported
        if not isinstance(icon, "".__class__):
            raise ValueError("icon must be a string")

        sublime_api.view_add_regions(self.view_id, key, regions, scope, icon, flags)

    def get_regions(self, key):
        return sublime_api.view_get_regions(self.view_id, key)

    def erase_regions(self, key):
        sublime_api.view_erase_regions(self.view_id, key)

    def assign_syntax(self, syntax_file):
        sublime_api.view_assign_syntax(self.view_id, syntax_file)

    def set_syntax_file(self, syntax_file):
        """ Deprecated, use assign_syntax instead """
        self.assign_syntax(syntax_file)

    def symbols(self):
        return sublime_api.view_symbols(self.view_id)

    def get_symbols(self):
        """ Deprecated, use symbols """
        return self.symbols()

    def indexed_symbols(self):
        return sublime_api.view_indexed_symbols(self.view_id)

    def set_status(self, key, value):
        sublime_api.view_set_status(self.view_id, key, value)

    def get_status(self, key):
        return sublime_api.view_get_status(self.view_id, key)

    def erase_status(self, key):
        sublime_api.view_erase_status(self.view_id, key)

    def extract_completions(self, prefix, tp = -1):
        return sublime_api.view_extract_completions(self.view_id, prefix, tp)

    def find_all_results(self):
        return sublime_api.view_find_all_results(self.view_id)

    def command_history(self, delta, modifying_only = False):
        return sublime_api.view_command_history(self.view_id, delta, modifying_only)

    def overwrite_status(self):
        return sublime_api.view_get_overwrite_status(self.view_id)

    def set_overwrite_status(self, value):
        sublime_api.view_set_overwrite_status(self.view_id, value)

    def show_popup_menu(self, items, on_select, flags = 0):
        """
        on_select is called when the the quick panel is finished, and should accept a
        single integer, specifying which item was selected, or -1 for none
        """
        return sublime_api.view_show_popup_table(self.view_id, items,
            on_select, flags, -1)


class Settings(object):
    def __init__(self, id):
        self.settings_id = id

    def get(self, key, default = None):
        if default != None:
            return sublime_api.settings_get_default(self.settings_id, key, default)
        else:
            return sublime_api.settings_get(self.settings_id, key)

    def has(self, key):
        return sublime_api.settings_has(self.settings_id, key)

    def set(self, key, value):
        sublime_api.settings_set(self.settings_id, key, value)

    def erase(self, key):
        sublime_api.settings_erase(self.settings_id, key)

    def add_on_change(self, tag, callback):
        sublime_api.settings_add_on_change(self.settings_id, tag, callback)

    def clear_on_change(self, tag):
        sublime_api.settings_clear_on_change(self.settings_id, tag)
