"""
reimplements enough of sublime text's internals that we can test the
code that uses 'error_message
"""

import re
import os
import sys
import json
import glob
import platform as platform_module  # avoid collision with function
import tempfile
from itertools import chain
from os.path import join, dirname, abspath

HERE = dirname(__file__)
ROOT = abspath(join(HERE, '..', '..'))


def raiser(*args, **kw):
    raise Exception((args, kw))


class SettingsBackend(object):
    def __init__(self):
        self.settings_instances = {}

    def load_settings(self, base_name):
        if base_name in self.settings_instances:
            return base_name

        try:
            with open(join(ROOT, base_name)) as fh:
                contents = fh.read()

        except FileNotFoundError:
            self.settings_instances[base_name] = {}

        else:
            self.settings_instances[base_name] = decode_value(contents)

        return base_name

    def settings_get(self, settings_id, key):
        return self.settings_instances[settings_id][key]

    def settings_set(self, settings_id, key, value):
        self.settings_instances[settings_id][key] = value

    def save_settings(self, base_name):
        # don't bother actually doing anything
        ...


settings_storage = SettingsBackend()
load_settings = settings_storage.load_settings
save_settings = settings_storage.save_settings
settings_get = settings_storage.settings_get
settings_set = settings_storage.settings_set


active_window = lambda: 'active'
architecture = lambda: platform_module.architecture()[0]
cache_path = raiser
channel = lambda: '3dev'
decode_value = lambda contents: json.loads(re.sub(r'//[^\n]*\n', '', contents))
encode_value = json.dumps
error_message = lambda s: print(s)
executable_path = raiser
find_resources = lambda pattern: chain.from_iterable(
    glob.glob(join(directory, pattern))
    for directory, _, _ in os.walk(ROOT)
    if '.git' not in directory
)
get_clipboard = raiser
get_macro = raiser
installed_packages_path = lambda: ''
load_binary_resource = lambda filename: open(filename, 'wb').read(0)
load_resource = lambda filename: open(filename).read()
log_commands = lambda switch: None
log_indexing = lambda switch: None
log_input = lambda switch: None
log_message = lambda s: print(s)
log_result_regex = lambda switch: None
message_dialog = raiser
ok_cancel_dialog = raiser
PACKAGES_PATH = tempfile.mkdtemp()
packages_path = lambda: PACKAGES_PATH
platform = lambda: sys.platform
run_command = raiser
score_selector = raiser
set_clipboard = raiser
set_timeout = lambda func, timeout_ms: None
set_timeout_async = raiser
settings_add_on_change = raiser
settings_clear_on_change = raiser
settings_erase = raiser
settings_get_default = raiser
settings_has = raiser
sheet_window = raiser
status_message = raiser
version = lambda: 0
view_add_regions = raiser
view_assign_syntax = raiser
view_begin_edit = raiser
view_buffer_id = raiser
view_cached_substr = raiser
view_change_count = raiser
view_classify = raiser
view_command_history = raiser
view_em_width = raiser
view_encoding = raiser
view_end_edit = raiser
view_erase = raiser
view_erase_regions = raiser
view_erase_status = lambda view_id, key: None
view_expand_by_class = raiser
view_extract_completions = raiser
view_extract_scope = raiser
view_file_name = lambda view_id: ''
view_find = raiser
view_find_all = raiser
view_find_all_results = raiser
view_find_all_with_contents = raiser
view_find_by_class = raiser
view_find_by_selector = lambda view_id, selector: []
view_fold_region = raiser
view_fold_regions = raiser
view_folded_regions = raiser
view_full_line_from_point = raiser
view_full_line_from_region = raiser
view_get_name = raiser
view_get_overwrite_status = raiser
view_get_regions = raiser
view_get_status = raiser
view_has_non_empty_selection_region = raiser
view_indentation_level = raiser
view_indented_region = raiser
view_indexed_symbols = raiser
view_insert = raiser
view_is_dirty = raiser
view_is_folded = raiser
view_is_in_edit = raiser
view_is_loading = raiser
view_is_read_only = raiser
view_is_scratch = raiser
view_layout_extents = raiser
view_layout_to_text = raiser
view_line_endings = raiser
view_line_from_point = raiser
view_line_from_region = raiser
view_line_height = raiser
view_lines = raiser
view_match_selector = raiser
view_meta_info = raiser
view_replace = raiser
view_retarget = raiser
view_row_col = raiser
view_run_command = lambda view_id, cmd, args: None
view_scope_name = raiser
view_score_selector = raiser
view_selection_add_point = raiser
view_selection_add_region = raiser
view_selection_clear = raiser
view_selection_contains = raiser
view_selection_erase = raiser
view_selection_get = raiser
view_selection_size = raiser
view_selection_subtract_region = raiser
view_set_encoding = raiser
view_set_line_endings = raiser
view_set_name = lambda view_id, name: None
view_set_overwrite_status = raiser
view_set_read_only = lambda view_id, read_only: None
view_set_scratch = lambda view_id, scratch: None
view_set_status = raiser
view_set_viewport_position = raiser
view_settings = raiser
view_show_point = raiser
view_show_point_at_center = raiser
view_show_popup_table = raiser
view_show_region = raiser
view_show_region_at_center = raiser
view_size = raiser
view_split_by_newlines = raiser
view_symbols = raiser
view_text_point = raiser
view_text_to_layout = raiser
view_unfold_region = raiser
view_unfold_regions = raiser
view_viewport_extents = raiser
view_viewport_position = raiser
view_visible_region = raiser
view_window = raiser
view_word_from_point = raiser
view_word_from_region = raiser
window_active_group = raiser
window_active_sheet = raiser
window_active_sheet_in_group = raiser
window_active_view = lambda window_id: None
window_active_view_in_group = raiser
window_close_file = raiser
window_create_output_panel = raiser
window_find_open_file = raiser
window_focus_group = raiser
window_focus_sheet = raiser
window_focus_view = raiser
window_folders = lambda window_id: []
window_get_layout = raiser
window_get_project_data = raiser
window_get_project_data = lambda window_id: None
window_get_sheet_index = raiser
window_get_view_index = raiser
window_lookup_symbol = raiser
window_lookup_symbol_in_open_files = raiser
window_new_file = lambda window_id, flags, syntax: None
window_num_groups = raiser
window_open_file = raiser
window_project_file_name = raiser
window_run_command = raiser
window_set_layout = raiser
window_set_project_data = raiser
window_set_sheet_index = raiser
window_set_view_index = raiser
window_settings = raiser
window_sheets = raiser
window_sheets_in_group = raiser
window_show_input_panel = raiser
window_show_quick_panel = raiser
window_system_handle = raiser
window_template_settings = raiser
window_transient_sheet_in_group = raiser
window_transient_view_in_group = raiser
window_views = raiser
window_views_in_group = raiser
windows = lambda: []
