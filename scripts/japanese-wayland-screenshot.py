#!/usr/bin/env python3
"""
Helper script to take a screenshot via xdg-desktop-portal
and forward it to the japanese-wayland Rust service.
"""
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import sys
import os

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session = dbus.SessionBus()
    
    # Call the portal screenshot
    portal = session.get_object(
        'org.freedesktop.portal.Desktop',
        '/org/freedesktop/portal/desktop'
    )
    screenshot = dbus.Interface(portal, 'org.freedesktop.portal.Screenshot')
    
    options = dbus.Dictionary({'interactive': dbus.Boolean(False)}, signature='sv')
    request_path = screenshot.Screenshot('', options)
    
    print(f"[portal] Request path: {request_path}", file=sys.stderr)
    
    # Connect to the response signal
    request = session.get_object('org.freedesktop.portal.Desktop', request_path)
    request_iface = dbus.Interface(request, 'org.freedesktop.portal.Request')
    
    def on_response(response, results):
        print(f"[portal] Response: {response}", file=sys.stderr)
        if response == 0:
            uri = results.get('uri', '')
            if uri:
                path = uri.replace('file://', '')
                print(f"[portal] Screenshot saved: {path}", file=sys.stderr)
                
                # Call the Rust service
                service = session.get_object(
                    'com.japanesewayland.JapaneseWayland',
                    '/com/japanesewayland/JapaneseWayland'
                )
                service_iface = dbus.Interface(service, 'com.japanesewayland.JapaneseWayland')
                service_iface.ProcessImage(path)
                print(f"[portal] Called service", file=sys.stderr)
            else:
                print("[portal] No uri in response", file=sys.stderr)
        else:
            print(f"[portal] Failed: {response}", file=sys.stderr)
        loop.quit()
    
    request_iface.connect_to_signal('Response', on_response)
    
    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
