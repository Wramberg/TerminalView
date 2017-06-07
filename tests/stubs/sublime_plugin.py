import sublime
import threading
import imp
import importlib
import os
import sys
import zipfile
import sublime_api
import traceback

api_ready = False

application_command_classes = []
window_command_classes = []
text_command_classes = []

all_command_classes = [application_command_classes, window_command_classes, text_command_classes]

all_callbacks = {'on_new': [], 'on_clone': [], 'on_load': [], 'on_pre_close': [], 'on_close': [],
    'on_pre_save': [], 'on_post_save': [], 'on_modified': [],
    'on_selection_modified': [],'on_activated': [], 'on_deactivated': [],
    'on_query_context': [], 'on_query_completions': [],
    'on_text_command': [], 'on_window_command': [],
    'on_post_text_command': [], 'on_post_window_command': [],

    'on_modified_async': [],
    'on_selection_modified_async': [],
    'on_pre_save_async': [],
    'on_post_save_async': [],
    'on_activated_async': [],
    'on_deactivated_async': [],
    'on_new_async': [],
    'on_load_async': [],
    'on_clone_async': []}

def unload_module(module):
    if "plugin_unloaded" in module.__dict__:
        module.plugin_unloaded()
    # Check unload_handler too, for backwards compat
    if "unload_handler" in module.__dict__:
        module.unload_handler()

    # Unload the old plugins
    if "plugins" in module.__dict__:
        for p in module.plugins:
            for cmd_cls_list in all_command_classes:
                try:
                    cmd_cls_list.remove(p)
                except ValueError:
                    pass
            for c in all_callbacks.values():
                try:
                    c.remove(p)
                except ValueError:
                    pass

def unload_plugin(modulename):
    print("unloading plugin", modulename)

    was_loaded = modulename in sys.modules
    if was_loaded:
        m = sys.modules[modulename]
        unload_module(m)

def reload_plugin(modulename):
    print("reloading plugin", modulename)

    if modulename in sys.modules:
        m = sys.modules[modulename]
        unload_module(m)
        m = imp.reload(m)
    else:
        m = importlib.import_module(modulename)

    module_plugins = []
    on_activated_targets = []
    for type_name in dir(m):
        try:
            t = m.__dict__[type_name]
            if t.__bases__:
                is_plugin = False
                if issubclass(t, ApplicationCommand):
                    application_command_classes.append(t)
                    is_plugin = True
                if issubclass(t, WindowCommand):
                    window_command_classes.append(t)
                    is_plugin = True
                if issubclass(t, TextCommand):
                    text_command_classes.append(t)
                    is_plugin = True

                if is_plugin:
                    module_plugins.append(t)

                if issubclass(t, EventListener):
                    obj = t()
                    for p in all_callbacks.items():
                        if p[0] in dir(obj):
                            p[1].append(obj)

                    if "on_activated" in dir(obj):
                        on_activated_targets.append(obj)

                    module_plugins.append(obj)

        except AttributeError:
            pass

    if len(module_plugins) > 0:
        m.plugins = module_plugins

    if api_ready:
        if "plugin_loaded" in m.__dict__:
            try:
                m.plugin_loaded()
            except:
                traceback.print_exc()

        # Synthesize any required on_activated calls
        for el in on_activated_targets:
            w = sublime.active_window()
            if w:
                v = w.active_view()
                if v:
                    try:
                        el.on_activated(v)
                    except:
                        traceback.print_exc()

def create_application_commands():
    cmds = []
    for class_ in application_command_classes:
        cmds.append(class_())
    sublime_api.notify_application_commands(cmds)

def create_window_commands(window_id):
    window = sublime.Window(window_id)
    cmds = []
    for class_ in window_command_classes:
        cmds.append(class_(window))
    return cmds

def create_text_commands(view_id):
    view = sublime.View(view_id)
    cmds = []
    for class_ in text_command_classes:
        try:
            cmds.append(class_(view))
        except TypeError:
            print(class_)
            raise
    return cmds

def on_api_ready():
    global api_ready
    api_ready = True

    for m in list(sys.modules.values()):
        if "plugin_loaded" in m.__dict__:
            try:
                m.plugin_loaded()
            except:
                traceback.print_exc()

    # Synthesize an on_activated call
    w = sublime.active_window()
    if w:
        view_id = sublime_api.window_active_view(w.window_id)
        if view_id != 0:
            try:
                on_activated(view_id)
            except:
                traceback.print_exc()

def on_new(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_new']:
        try:
            callback.on_new(v)
        except:
            traceback.print_exc()

def on_new_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_new_async']:
        try:
            callback.on_new_async(v)
        except:
            traceback.print_exc()

def on_clone(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_clone']:
        try:
            callback.on_clone(v)
        except:
            traceback.print_exc()

def on_clone_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_clone_async']:
        try:
            callback.on_clone_async(v)
        except:
            traceback.print_exc()

def on_load(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_load']:
        try:
            callback.on_load(v)
        except:
            traceback.print_exc()

def on_load_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_load_async']:
        try:
            callback.on_load_async(v)
        except:
            traceback.print_exc()

def on_pre_close(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_close']:
        try:
            callback.on_pre_close(v)
        except:
            traceback.print_exc()

def on_close(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_close']:
        try:
            callback.on_close(v)
        except:
            traceback.print_exc()

def on_pre_save(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_save']:
        try:
            callback.on_pre_save(v)
        except:
            traceback.print_exc()

def on_pre_save_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_save_async']:
        try:
            callback.on_pre_save_async(v)
        except:
            traceback.print_exc()

def on_post_save(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_save']:
        try:
            callback.on_post_save(v)
        except:
            traceback.print_exc()

def on_post_save_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_save_async']:
        try:
            callback.on_post_save_async(v)
        except:
            traceback.print_exc()

def on_modified(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_modified']:
        try:
            callback.on_modified(v)
        except:
            traceback.print_exc()

def on_modified_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_modified_async']:
        try:
            callback.on_modified_async(v)
        except:
            traceback.print_exc()

def on_selection_modified(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_selection_modified']:
        try:
            callback.on_selection_modified(v)
        except:
            traceback.print_exc()

def on_selection_modified_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_selection_modified_async']:
        try:
            callback.on_selection_modified_async(v)
        except:
            traceback.print_exc()

def on_activated(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_activated']:
        try:
            callback.on_activated(v)
        except:
            traceback.print_exc()

def on_activated_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_activated_async']:
        try:
            callback.on_activated_async(v)
        except:
            traceback.print_exc()

def on_deactivated(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_deactivated']:
        try:
            callback.on_deactivated(v)
        except:
            traceback.print_exc()

def on_deactivated_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_deactivated_async']:
        try:
            callback.on_deactivated_async(v)
        except:
            traceback.print_exc()

def on_query_context(view_id, key, operator, operand, match_all):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_query_context']:
        try:
            val = callback.on_query_context(v, key, operator, operand, match_all)
            if val:
                return True
        except:
            traceback.print_exc()

    return False

def normalise_completion(c):
    if len(c) == 1:
        return (c[0], "", "")
    elif len(c) == 2:
        return (c[0], "", c[1])
    else:
        return c

def on_query_completions(view_id, prefix, locations):
    v = sublime.View(view_id)

    completions = []
    flags = 0
    for callback in all_callbacks['on_query_completions']:
        try:
            res = callback.on_query_completions(v, prefix, locations)

            if isinstance(res, tuple):
                completions += [normalise_completion(c) for c in res[0]]
                flags |= res[1]
            elif isinstance(res, list):
                completions += [normalise_completion(c) for c in res]
        except:
            traceback.print_exc()

    return (completions,flags)

def on_text_command(view_id, name, args):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_text_command']:
        try:
            res = callback.on_text_command(v, name, args)
            if isinstance(res, tuple):
                return res
            elif res:
                return (res, None)
        except:
            traceback.print_exc()

    return ("", None)

def on_window_command(window_id, name, args):
    window = sublime.Window(window_id)
    for callback in all_callbacks['on_window_command']:
        try:
            res = callback.on_window_command(window, name, args)
            if isinstance(res, tuple):
                return res
            elif res:
                return (res, None)
        except:
            traceback.print_exc()

    return ("", None)

def on_post_text_command(view_id, name, args):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_text_command']:
        try:
            callback.on_post_text_command(v, name, args)
        except:
            traceback.print_exc()

def on_post_window_command(window_id, name, args):
    window = sublime.Window(window_id)
    for callback in all_callbacks['on_post_window_command']:
        try:
            callback.on_post_window_command(window, name, args)
        except:
            traceback.print_exc()


class Command(object):
    def name(self):
        clsname = self.__class__.__name__
        name = clsname[0].lower()
        last_upper = False
        for c in clsname[1:]:
            if c.isupper() and not last_upper:
                name += '_'
                name += c.lower()
            else:
                name += c
            last_upper = c.isupper()
        if name.endswith("_command"):
            name = name[0:-8]
        return name

    def is_enabled_(self, args):
        ret = None
        try:
            if args:
                if 'event' in args:
                    del args['event']

                ret = self.is_enabled(**args)
            else:
                ret = self.is_enabled()
        except TypeError:
            ret = self.is_enabled()

        if not isinstance(ret, bool):
            raise ValueError("is_enabled must return a bool", self)

        return ret

    def is_enabled(self):
        return True

    def is_visible_(self, args):
        ret = None
        try:
            if args:
                ret = self.is_visible(**args)
            else:
                ret = self.is_visible()
        except TypeError:
            ret = self.is_visible()

        if not isinstance(ret, bool):
            raise ValueError("is_visible must return a bool", self)

        return ret

    def is_visible(self):
        return True

    def is_checked_(self, args):
        ret = None
        try:
            if args:
                ret = self.is_checked(**args)
            else:
                ret = self.is_checked()
        except TypeError:
            ret = self.is_checked()

        if not isinstance(ret, bool):
            raise ValueError("is_checked must return a bool", self)

        return ret

    def is_checked(self):
        return False

    def description_(self, args):
        try:
            if args != None:
                return self.description(**args)
            else:
                return self.description()
        except TypeError as e:
            return ""

    def description(self):
        return ""


class ApplicationCommand(Command):
    def run_(self, edit_token, args):
        if args:
            if 'event' in args:
                del args['event']

            return self.run(**args)
        else:
            return self.run()

    def run(self):
        pass


class WindowCommand(Command):
    def __init__(self, window):
        self.window = window

    def run_(self, edit_token, args):
        if args:
            if 'event' in args:
                del args['event']

            return self.run(**args)
        else:
            return self.run()

    def run(self):
        pass


class TextCommand(Command):
    def __init__(self, view):
        self.view = view

    def run_(self, edit_token, args):
        if args:
            if 'event' in args:
                del args['event']

            edit = self.view.begin_edit(edit_token, self.name(), args)
            try:
                return self.run(edit, **args)
            finally:
                self.view.end_edit(edit)
        else:
            edit = self.view.begin_edit(edit_token, self.name())
            try:
                return self.run(edit)
            finally:
                self.view.end_edit(edit)

    def run(self, edit):
        pass


class EventListener(object):
    pass


class MultizipImporter(object):
    def __init__(self):
        self.loaders = []
        self.file_loaders = []

    def find_module(self, fullname, path = None):
        if not path:
            for l in self.loaders:
                if l.name == fullname:
                    return l

        for l in self.loaders:
            if path == [l.zippath]:
                if l.has(fullname):
                    return l

        return None


class ZipLoader(object):
    def __init__(self, zippath):
        self.zippath = zippath
        self.name = os.path.splitext(os.path.basename(zippath))[0]

        self.contents = {"":""}
        self.packages = {""}

        z = zipfile.ZipFile(zippath, 'r')
        files = [i.filename for i in z.infolist()]

        for f in files:
            base, ext = os.path.splitext(f)
            if ext != ".py":
                continue

            paths = base.split('/')
            if len(paths) > 0 and paths[len(paths) - 1] == "__init__":
                paths.pop()
                self.packages.add('.'.join(paths))

            try:
                self.contents['.'.join(paths)] = z.read(f).decode('utf-8')
            except UnicodeDecodeError:
                print(f, "in", zippath, "is not utf-8 encoded, unable to load plugin")
                continue

            while len(paths) > 1:
                paths.pop()
                parent = '.'.join(paths)
                if parent not in self.contents:
                    self.contents[parent] = ""
                    self.packages.add(parent)

        z.close()

    def has(self, fullname):
        key = '.'.join(fullname.split('.')[1:])
        if key in self.contents:
            return True

        override_file = os.path.join(override_path, os.sep.join(fullname.split('.')) + '.py')
        if os.path.isfile(override_file):
            return True

        override_package = os.path.join(override_path, os.sep.join(fullname.split('.')))
        if os.path.isdir(override_package):
            return True

        return False

    def load_module(self, fullname):
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))

        mod.__file__ = self.zippath + "/" + fullname
        mod.__name__ = fullname
        mod.__path__ = [self.zippath]
        mod.__loader__ = self

        key = '.'.join(fullname.split('.')[1:])

        if key in self.contents:
            source = self.contents[key]
            source_path = key + " in " + self.zippath

        is_pkg = key in self.packages

        try:
            override_file = os.path.join(override_path, os.sep.join(fullname.split('.')) + '.py')
            override_package_init = os.path.join(os.path.join(override_path, os.sep.join(fullname.split('.'))), '__init__.py')

            if os.path.isfile(override_file):
                with open(override_file, 'r') as f:
                    source = f.read()
                    source_path = override_file
            elif os.path.isfile(override_package_init):
                with open(override_package_init, 'r') as f:
                    source = f.read()
                    source_path = override_package_init
                    is_pkg = True
        except:
            pass

        if is_pkg:
            mod.__package__ = mod.__name__
        else:
            mod.__package__ = fullname.rpartition('.')[0]

        exec(compile(source, source_path, 'exec'), mod.__dict__)
        return mod


override_path = None
multi_importer = MultizipImporter()
sys.meta_path.insert(0, multi_importer)

def update_compressed_packages(pkgs):
    multi_importer.loaders = [ZipLoader(p) for p in pkgs]

def set_override_path(path):
    global override_path
    override_path = path
