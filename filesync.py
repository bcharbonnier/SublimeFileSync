import os
import sublime
import sublime_plugin
import os.path
import shutil
import functools
import sys
import fnmatch


_DEBUG = False
_enabled = False
_settings = None
_preferences = None

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
is_python3 = sys.version_info[0] > 2


def is_st3():
    return sublime.version()[0] == '3'


class FileSyncEnableCommand(sublime_plugin.WindowCommand):
    def run(self):
        global _enabled
        _enabled = not _enabled
        _preferences.set("filesync_enabled", _enabled)
        self.rename_sidebar_menu(_enabled)
        sublime.save_settings("Preferences.sublime-settings")
        initFilesync()

    def is_checked(self):
        global _enabled
        return _enabled

    def rename_sidebar_menu(self, enable):
        """We dynamically rename the sidebar menu file to deactivate it when
        FileSync is disabled"""
        enabled_menu = os.path.join(BASE_PATH, "Side Bar.sublime-menu")
        disabled_menu = os.path.join(BASE_PATH, "Side Bar.sublime-menu.disabled")
        if enable:
            shutil.move(disabled_menu, enabled_menu)
        else:
            shutil.move(enabled_menu, disabled_menu)


class FileSyncFilesCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        for file in files:
            sync_file(file)

    def is_visible(self, files):
        global _enabled

        if not _enabled:
            return False
        if len(files) > 1:
            return check_files_syncables(files)
        else:
            return False

        # default Falsy return
        return False


class FileSyncFileCommand(sublime_plugin.WindowCommand):
    def run(self, files):
        sync_file(files[0])

    def is_visible(self, files):
        global _enabled

        if not _enabled:
            return False
        if len(files) is 1:
            file = files[0]
            if os.path.isdir(file):
                return False
            else:
                return check_file_syncable(file)

        # default Falsy return
        return False


class FileSyncFolderCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        folder = paths[0]
        log("----------------------------------------------------------------------------------------------------------------------------")
        log("Starting sync for '%s'" % folder)
        log("----------------------------------------------------------------------------------------------------------------------------")
        for file in listdir_fullpath(folder):
            if os.path.isdir(file) is False:
                sync_file(file)
        log("----------------------------------------------------------------------------------------------------------------------------")
        log("End of sync for '%s'" % folder)
        log("----------------------------------------------------------------------------------------------------------------------------")

    def is_visible(self, paths=[]):
        global _enabled
        if not _enabled or check_files_syncables(paths) is False:
            return False
        if len(paths) is 1:
            return os.path.isdir(paths[0]) is True

        # default Falsy return
        return False


class FileSyncAddMappingCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        self.window.run_command('hide_panel')
        self.window.show_input_panel("Enter a destination folder for sync:", '', functools.partial(self.on_done, paths[0]), None, None)

    def is_visible(self, paths=[]):
        global _enabled

        if not _enabled or check_file_syncable(paths[0]):
            return False

        if len(paths) is 1 and check_file_syncable(paths[0]) is False:
            return True

        # default Falsy return
        return False

    def description(self, paths=[]):
        path = paths[0]
        if os.path.isdir(path) is False:
            return u'Add a mapping for the parent folder'
        return u"Add a mapping for this folder"

    def on_done(self, source, destination):
        global _settings
        if os.path.isdir(source) is False:
            source = os.path.abspath(os.path.join(source, os.pardir))

        if source == destination:
            return sublime.error_message("Unable to create FileSync mapping, source and destination are identical.")

        mappings = _settings.get("mappings")
        mappings.append({
            'source': source,
            'destination': destination
        })
        _settings.set("mappings", mappings)
        sublime.save_settings("FileSync.sublime-settings")


class FileSyncNoMappingCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        pass

    def is_enabled(self, paths=[]):
        return False

    def is_visible(self, paths=[]):
        global _enabled

        if not _enabled:
            return False
        #log("Syncable %s" % paths, check_files_syncables(paths))
        return check_files_syncables(paths) is False


class FileSyncBuild(sublime_plugin.EventListener):
    def on_post_save(self, view):
        global _enabled
        if _enabled:
            sync_file(view.file_name())


def updateStatus(text):
    log(text)
    sublime.set_timeout(functools.partial(sublime.status_message, "FileSync: %s" % text), 500)


def initFilesync():
    global _settings, _preferences, _enabled
    _settings = sublime.load_settings("FileSync.sublime-settings")
    _preferences = sublime.load_settings("Preferences.sublime-settings")
    _enabled = _preferences.get("filesync_enabled")
    if(_enabled):
        log("Plugin is enabled")
    else:
        log("Plugin is disabled")

sublime.set_timeout(functools.partial(initFilesync), 500)


def log(text):
    print("[FileSync] %s" % text)


def check_files_syncables(files):
    syncs = False
    for file in files:
        syncs = check_file_syncable(file)
    return syncs


def check_file_syncable(file):
    sync = False
    mappings = _settings.get("mappings")
    for mapping in mappings:
        source_folder = os.path.abspath(mapping.get('source'))
        if source_folder in file:
            sync = True
    return sync


def listdir_fullpath(d):
    global _settings
    files = []
    for root, dirnames, filenames in os.walk(d):
        folder_excluded = False
        for exclusion in _settings.get("exclude_folder_names"):
            if exclusion in os.path.dirname(root):
                log("Folder '%s' excluded from sync list..." % root)
                folder_excluded = True
                break
        if folder_excluded:
            continue
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def sync_file(file):
    global _settings
    log("Trying to sync '%s'" % file)

    for exclusion in _settings.get("exclude_folder_names"):
        if exclusion in os.path.dirname(file):
            log("Global exclusion pattern detected ('%s'), skipping sync..." % exclusion)
            return

    mappings = _settings.get("mappings")
    for mapping in mappings:
        source_folder = os.path.abspath(mapping.get('source'))
        dest_folder = os.path.abspath(mapping.get('destination'))
        if (source_folder in file):
            dest = file.replace(source_folder, dest_folder)

            exclude_pattern_list = mapping.get('exclude_pattern_list')
            if exclude_pattern_list:
                for exclusion in exclude_pattern_list:
                    if fnmatch.fnmatch(file, exclusion):
                        log("Exclusion pattern detected ('%s'), skipping sync..." % exclusion)
                        return

            #log("Syncing %s" % (file + " -> " + dest))

            final_dest_folder = os.path.dirname(dest)
            if not os.path.exists(final_dest_folder):
                os.makedirs(final_dest_folder)
            shutil.copy2(file, dest)
            log("Copying...")
            updateStatus("%s has been synchronised -> %s" % (file, dest))
