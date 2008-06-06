#!/usr/bin/env python
"""
setup.py - script for building MacLibre .app

Usage:
    % python setup.py py2app
    
For the list of available commands:
    % python setup.py py2app --help
"""
from distutils.core import setup
import py2app
import sys

isOffline = False

for arg in sys.argv:
    if arg == '--offline':
        print 'Adding apps disk images dir for offline distribution'
        isOffline = True
        sys.argv.remove(arg)
        break

if isOffline:
    RES = ['../bin/AppsLogos', '../bin/Images', '../xml', '../bin/AppsDiskImages']
else:
    RES = ['../bin/AppsLogos', '../bin/Images', '../xml']

py2app_options = dict(
    # Map "open document" events to sys.argv.
    # Scripts that expect files as command line arguments
    # can be trivially used as "droplets" using this option.
    # Without this option, sys.argv should not be used at all
    # as it will contain only Mac OS X specific stuff.
    argv_emulation=True,
    plist='../plists/Info_10.4_.plist',
    resources = RES ,
    # This is a shortcut that will place MyApplication.icns
    # in the Contents/Resources folder of the application bundle,
    # and make sure the CFBundleIcon plist key is set appropriately.
    iconfile='../bin/Graphics/maclibre.icns',
    #dylib_excludes=["libwx"],
    #excludes = ['wx']
)

setup(
    app=['MacLibre.py'],
    options=dict(
        # Each command is allowed to have its own
        # options, so we must specify that these
        # options are py2app specific.
        py2app=py2app_options,
    )
)