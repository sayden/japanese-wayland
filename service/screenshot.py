from gi.repository import Gio, GLib
import urllib.parse
import sys

PORTAL_BUS = "org.freedesktop.portal.Desktop"
PORTAL_PATH = "/org/freedesktop/portal/desktop"
PORTAL_IFACE = "org.freedesktop.portal.Screenshot"
REQUEST_IFACE = "org.freedesktop.portal.Request"

def screenshot_full_screen(output_path: str, callback, interactive: bool = False):
    """
    Calls the xdg-desktop-portal Screenshot API and waits for the response.
    Returns the path to the saved screenshot file via callback(path, error).
    """
    connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    options = GLib.Variant('a{sv}', {
        'interactive': GLib.Variant('b', interactive)
    })

    def on_call_done(connection, result, user_data):
        try:
            reply = connection.call_finish(result)
            request_path = reply.unpack()[0]
            # Now wait for the Response signal on the request_path
            
            def on_signal(connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
                response_code, results = parameters.unpack()
                connection.signal_unsubscribe(sub_id)
                if response_code == 0:
                    uri = results.get("uri")
                    if uri:
                        # parse file:// URI
                        path = urllib.parse.unquote(uri.replace("file://", ""))
                        callback(path, None)
                    else:
                        callback(None, Exception("No uri in portal response"))
                else:
                    callback(None, Exception(f"Portal screenshot failed with code: {response_code}"))

            sub_id = connection.signal_subscribe(
                PORTAL_BUS,
                REQUEST_IFACE,
                "Response",
                request_path,
                None,
                Gio.DBusSignalFlags.NONE,
                on_signal,
                None
            )

        except Exception as e:
            callback(None, e)

    connection.call(
        PORTAL_BUS,
        PORTAL_PATH,
        PORTAL_IFACE,
        "Screenshot",
        GLib.Variant.new_tuple(GLib.Variant('s', ''), options),
        None,
        Gio.DBusCallFlags.NONE,
        -1,
        None,
        on_call_done,
        None
    )

def screenshot_full_screen_sync(output_path: str) -> str:
    # Since DBus Portal API requires a mainloop to receive signals,
    # and GTK already runs a mainloop, we should ideally use the async approach or run a local loop.
    # To keep it simple, we run a nested loop until we get the response.
    
    loop = GLib.MainLoop()
    result_path = None
    result_err = None

    def cb(path, err):
        nonlocal result_path, result_err
        result_path = path
        result_err = err
        loop.quit()
        
    connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    options = GLib.Variant('a{sv}', {
        'interactive': GLib.Variant('b', False)
    })
    
    reply = connection.call_sync(
        PORTAL_BUS,
        PORTAL_PATH,
        PORTAL_IFACE,
        "Screenshot",
        GLib.Variant.new_tuple(GLib.Variant('s', ''), options),
        None,
        Gio.DBusCallFlags.NONE,
        -1,
        None
    )
    request_path = reply.unpack()[0]
    
    def on_signal(connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
        nonlocal result_path, result_err
        response_code, results = parameters.unpack()
        connection.signal_unsubscribe(sub_id)
        if response_code == 0:
            uri = results.get("uri")
            if uri:
                path = urllib.parse.unquote(uri.replace("file://", ""))
                result_path = path
            else:
                result_err = Exception("No uri in portal response")
        else:
            result_err = Exception(f"Portal screenshot failed with code: {response_code}")
        loop.quit()

    sub_id = connection.signal_subscribe(
        PORTAL_BUS,
        REQUEST_IFACE,
        "Response",
        request_path,
        None,
        Gio.DBusSignalFlags.NONE,
        on_signal,
        None
    )
    
    loop.run()
    
    if result_err:
        raise result_err
    return result_path
