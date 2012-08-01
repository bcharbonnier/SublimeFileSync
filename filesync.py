import os
import sublime
import sublime_plugin
import os.path
import shutil
import functools
import string

_DEBUG = True
_enabled = False
_settings = None
_preferences = None
_settings_filename = "FileSync.sublime-settings"
_preferences_filename = "Preferences.sublime-settings"

class FileSyncOpenSettingsCommand(sublime_plugin.WindowCommand):
  def run(self, file):
    sublime.active_window().open_file(sublime.packages_path() + file)

  def is_enabled(self):
    global _enabled
    return _enabled

class FileSyncEnableCommand(sublime_plugin.WindowCommand):
  def run(self):
    global _enabled
    _enabled = not _enabled
    _preferences.set("filesync_enabled", _enabled)
    sublime.save_settings(_preferences_filename)

  def is_checked(self):
    global _enabled
    return _enabled

class FileSyncFilesCommand(sublime_plugin.WindowCommand):
  def run(self, files):
    pass

  def is_visible(self, files):
    global _enabled
    return _enabled and len(files) > 1 and check_files_syncables(files)

class FileSyncFileCommand(sublime_plugin.WindowCommand):
  def run(self, files):
    pass

  def is_visible(self, files):
    global _enabled
    return _enabled and len(files) < 2 and check_files_syncables(files)

class FileSyncBuild(sublime_plugin.EventListener):
  def on_post_save(self, view):
    global _enabled
    if _enabled:
      self.do_sync(view)

  def do_sync(self, view):
    global _settings
    #print "Filesync: Syncing " + view.file_name()
    mappings = _settings.get("mappings")
    file = view.file_name()
    for mapping in mappings:
      source_folder = os.path.abspath(mapping.get('source'))
      dest_folder = os.path.abspath(mapping.get('destination'))
      #print source_folder, "\n", dest_folder, "\n", file
      if (source_folder in file):
        dest = file.replace(source_folder, dest_folder)
        final_dest_folder = os.path.dirname(dest)
        if not os.path.exists(final_dest_folder):
          os.makedirs(final_dest_folder)
        shutil.copy2(file, dest)
        #log(file + " -> " + dest)
        self.updateStatus( "FileSync: " + file + " has been synchronised -> " + dest )

  def updateStatus(self, text):
    sublime.set_timeout(functools.partial(sublime.status_message, text), 1000)

def initFilesync():
  global _settings, _preferences, _enabled
  _settings = sublime.load_settings(_settings_filename)
  _preferences = sublime.load_settings(_preferences_filename)
  _enabled = _preferences.get("filesync_enabled")
  #print "FileSync: enabled %s" % _enabled

sublime.set_timeout(functools.partial(initFilesync), 1000)

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

def log(**kwargs):
  print kwargs.keys()
  if _DEBUG:
    print "FileSync:", string.join(kwargs)