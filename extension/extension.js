/**
 * Japanese Wayland — Minimal GNOME Shell Extension (GNOME 45+ ES modules)
 * 
 * Registers hotkeys and forwards them to the Python DBus service.
 * All logic lives in the Python service.
 */

import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import Meta from 'gi://Meta';
import Shell from 'gi://Shell';
import Gio from 'gi://Gio';

const DBUS_BUS_NAME = 'com.japanesewayland.JapaneseWayland';
const DBUS_OBJECT_PATH = '/com/japanesewayland/JapaneseWayland';
const DBUS_INTERFACE = 'com.japanesewayland.JapaneseWayland';

let _dbusProxy = null;

function _getDBusProxy() {
    if (!_dbusProxy) {
        _dbusProxy = new Gio.DBusProxy({
            g_connection: Gio.DBus.session,
            g_interface_name: DBUS_INTERFACE,
            g_interface_info: Gio.DBusInterfaceInfo.new_for_xml(`
                <node>
                    <interface name="${DBUS_INTERFACE}">
                        <method name="StartFullScreenCapture" />
                        <method name="StartAreaCapture" />
                        <method name="Lookup">
                            <arg type="s" name="word" direction="in" />
                            <arg type="(saa{ss}ds)" name="result" direction="out" />
                        </method>
                        <signal name="CaptureResult">
                            <arg type="(saa{ss}ds)" name="result" />
                        </signal>
                    </interface>
                </node>
            `),
            g_name: DBUS_BUS_NAME,
            g_object_path: DBUS_OBJECT_PATH,
        });
    }
    return _dbusProxy;
}

function _startFullScreenCapture() {
    try {
        const proxy = _getDBusProxy();
        proxy.call_sync(
            'StartFullScreenCapture',
            null,
            Gio.DBusCallFlags.NONE,
            -1,
            null
        );
    } catch (e) {
        logError(e, 'JapaneseWayland');
    }
}

function _startAreaCapture() {
    try {
        const proxy = _getDBusProxy();
        proxy.call_sync(
            'StartAreaCapture',
            null,
            Gio.DBusCallFlags.NONE,
            -1,
            null
        );
    } catch (e) {
        logError(e, 'JapaneseWayland');
    }
}

export default class JapaneseWaylandExtension extends Extension {
    enable() {
        const settings = this.getSettings('org.gnome.shell.extensions.japanese-wayland');

        Main.wm.addKeybinding(
            'full-screen-capture',
            settings,
            Meta.KeyBindingFlags.NONE,
            Shell.ActionMode.NORMAL | Shell.ActionMode.OVERVIEW,
            () => _startFullScreenCapture()
        );

        Main.wm.addKeybinding(
            'area-capture',
            settings,
            Meta.KeyBindingFlags.NONE,
            Shell.ActionMode.NORMAL | Shell.ActionMode.OVERVIEW,
            () => _startAreaCapture()
        );
    }

    disable() {
        Main.wm.removeKeybinding('full-screen-capture');
        Main.wm.removeKeybinding('area-capture');
        _dbusProxy = null;
    }
}
