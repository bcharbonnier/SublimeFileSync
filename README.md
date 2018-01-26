++ Project is unmaintained ++
===========================

I am sorry but did not use Sublime anymore (I have switched to Atom and now VSCode). Anyone willing to maintain this plugin, just ask me and I'll transfer the ownership.

What is this?
=============

SublimeFileSync is a plugin for the text editor [SublimeText 2](http://www.sublimetext.com/2) and [3](http://www.sublimetext.com/3) providing an easy way to synchronise files between different locations.

The main goal is to keep files outside of Sublime Text projects in-sync with Sublime Text project files. The plugin works as an EventListener and will synchronise any matching files as soon as you save it.

Be aware that the synchronisation is only in one direction, from sublime Text to the outside world.

Installation
------------

### Package Control

Sublime Package Control allows you to easily install or remove `Filesync` from within the editor. It offers automatically updating packages as well so you no longer need to keep track of changes in `Filesync`.

1. Install Sublime Package Control (if you haven't done so already) from http://wbond.net/sublime_packages/package_control. Be sure to restart Sublime Text 2 to complete the installation.

2. Bring up the command palette (default `ctrl+shift+p` or `cmd+shift+p`) and start typing `Package Control: Install Package` then press return or click on that option to activate it. You will be presented with a new Quick Panel with the list of available packages. Find `Filesync` in the list of packages and press return on its entry to install it.

### Download or Clone

1. Download is also [available](https://github.com/bcharbonnier/SublimeFileSync/zipball/master "download") or clone directly and drop into your Sublime Text 2 packages directory (plugin folder must be named FileSync)

2. You may need to restart Sublime Text 2 after installation

Usage
-----

### Mappings

To synchronise 2 distinct locations you just need to define mappings from within your User preferences file. Open `Preferences\Package Settings\ FileSync\Settings - User`. If the file is new and empty be sure to create an empty JSON Object `{ }` inside the file, then/otherwise add a *mappings* section to it.

    // This is your settings file. Be sure that this is a valid JSON file
    {
      "mappings": [
        {
          "source": "C:/Documents/Work/MyAwesomeProject", //Windows style paths
          "destination": "G:/Apache/project"
        },
        {
          "source": "/Users/Benoit/Work/MySecretProject", //Unix style paths
          "destination": "/www/myproject"
        }
      ]
    }

As *mappings* is an array, you can add as many number of synchronisation definitions as you want.

For each mapping you define, you can also specify a list of patterns to be considered as *excluded*

### Exclusions

There are 2 types of exclusion that you can define

##### Global exclusion

Open your User preferences file `Preferences\Package Settings\ FileSync\Settings - User` and just add an `exclude_folder_names` section as an array.

    "exclude_folder_names": ["myfolder"],
	"mappings": [ ... ]


Any file that is contained inside a folder that name is included in this array will be skipped.

The default value of that array is set to `[".git", ".svn", ".hg"]`

##### Local exclusion

Inside each `mapping` declaration you can define an `exclude_pattern_list`.

    "mappings": [
      {
        "source": "C:/Documents/Work/MyAwesomeProject", //Windows style paths
        "destination": "G:/Apache/project",
		"exclude_pattern_list": ["*.bak"]
      }

With this any file of type `.bak` will not be part of the sync.

### Sidebar

FileSync could also be used from the Sublime sidebar.

For a workspace folder on which FileSync is not yet active you have options to create mappings from the contextual menu.

Select a folder and create a mapping for it, or select a file and create a mapping for the parent folder.

### Force a synchronisation

To force a synchronisation, just click on `Sync this file now` or `Sync this folder now` through the Sidebar Contextual menu.


Debugging
-----

If you want to see what is going on, just hit `` CTRL+` `` to open the python console.

Everything related to FileSync will look like that:

    [FileSync] ----------------------------------------------------------------------------------------------------------------------------
    [FileSync] Starting sync for 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync'
    [FileSync] ----------------------------------------------------------------------------------------------------------------------------
    [FileSync] Folder 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync\.git\hooks' excluded from sync list...
    [FileSync] Folder 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync\.git\info' excluded from sync list...
    [FileSync] Folder 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync\.git\logs' excluded from sync list...
    [FileSync] Trying to sync 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync\.gitignore'
    [FileSync] Copying...
    FileSync] C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync\.gitignore has been synchronised -> D:\Pouet\FileSync\.gitignore
    [FileSync] Trying to sync 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync\tests\popo.jsp'
    [FileSync] Exclusion pattern detected ('*.jsp'), skipping sync...
    [FileSync] ----------------------------------------------------------------------------------------------------------------------------
    [FileSync] End of sync for 'C:\Documents and Settings\bcharbonnier\Application Data\Sublime Text 2\Packages\FileSync'
    [FileSync] ----------------------------------------------------------------------------------------------------------------------------
