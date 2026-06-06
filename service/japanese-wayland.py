#!/usr/bin/env python3
import sys
import os

# Add the directory containing this script to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from dbus_service import JapaneseWaylandService

def on_activate(app):
    pass

def main():
    if not Gtk.init_check():
        print("Error: GTK couldn't be initialized (no display found). Exiting so systemd can restart us.")
        sys.exit(1)

    service = JapaneseWaylandService()
    service.export()

    app = Gtk.Application(application_id="com.japanesewayland.JapaneseWaylandApp")
    app.connect('activate', on_activate)
    app.hold()
    app.run(None)

if __name__ == '__main__':
    main()
