import traceback

from gi.repository import Gio, GLib

from dictionary import JMdictDictionary
from ocr import TesseractEngine
from popup import show_popup
from screenshot import screenshot_full_screen
from translator import translate_japanese_to_english

DBUS_BUS_NAME = "com.japanesewayland.JapaneseWayland"
DBUS_OBJECT_PATH = "/com/japanesewayland/JapaneseWayland"
DBUS_INTERFACE = "com.japanesewayland.JapaneseWayland"

xml = f"""
<node>
  <interface name="{DBUS_INTERFACE}">
    <method name="StartFullScreenCapture" />
    <method name="StartAreaCapture" />
    <method name="Lookup">
      <arg type="s" name="word" direction="in" />
      <arg type="(saa{{ss}}ds)" name="result" direction="out" />
    </method>
    <signal name="CaptureResult">
      <arg type="(saa{{ss}}ds)" name="result" />
    </signal>
  </interface>
</node>
"""


class JapaneseWaylandService:
    def __init__(self):
        self.ocr = TesseractEngine()
        self.dictionary = JMdictDictionary(
            "/home/mcastro/projects/japanese-wayland/dictionary/JMdict"
        )
        self.node_info = Gio.DBusNodeInfo.new_for_xml(xml)
        self.connection = None
        self.reg_id = None

    def export(self):
        Gio.bus_own_name(
            Gio.BusType.SESSION,
            DBUS_BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            self.on_bus_acquired,
            self.on_name_acquired,
            self.on_name_lost,
        )

    def on_bus_acquired(self, connection, name, user_data=None):
        self.connection = connection
        self.reg_id = connection.register_object(
            DBUS_OBJECT_PATH,
            self.node_info.interfaces[0],
            self.handle_method_call,
            None,
            None,
        )

    def on_name_acquired(self, connection, name, user_data=None):
        print(f"Acquired DBus name {name}")

    def on_name_lost(self, connection, name, user_data=None):
        print(f"Lost DBus name {name}")

    def emit_capture_result(self, result_tuple):
        if self.connection:
            self.connection.emit_signal(
                None,
                DBUS_OBJECT_PATH,
                DBUS_INTERFACE,
                "CaptureResult",
                GLib.Variant("((saa{ss}ds))", (result_tuple,)),
            )

    def handle_method_call(
        self,
        connection,
        sender,
        object_path,
        interface_name,
        method_name,
        parameters,
        invocation,
    ):
        try:
            if method_name == "StartFullScreenCapture":
                invocation.return_value(None)
                self.start_full_screen_capture()
            elif method_name == "StartAreaCapture":
                invocation.return_value(None)
                self.start_area_capture()
            elif method_name == "Lookup":
                word = parameters.unpack()[0]
                res = self.lookup_word(word)
                invocation.return_value(GLib.Variant("((saa{ss}ds))", (res,)))
            else:
                invocation.return_dbus_error(
                    "org.freedesktop.DBus.Error.UnknownMethod", "Unknown method"
                )
        except Exception as e:
            traceback.print_exc()
            invocation.return_dbus_error("org.freedesktop.DBus.Error.Failed", str(e))

    def lookup_word(self, word):
        try:
            defs = self.dictionary.lookup(word)
            def_list = []
            for d in defs:
                def_list.append(
                    {
                        "reading": d.reading,
                        "meanings": "; ".join(d.meanings),
                        "part_of_speech": d.part_of_speech,
                    }
                )
            return (word, def_list, 1.0, "")
        except Exception as e:
            return ("", [], 0.0, str(e))

    def _process_screenshot(self, path, error):
        if error:
            print(f"Screenshot error: {error}")
            self.emit_capture_result(("", [], 0.0, str(error)))
            return

        import threading

        def ocr_thread():
            try:
                ocr_result = self.ocr.recognize(path)
                translation = ""
                if ocr_result.text:
                    translation = translate_japanese_to_english(ocr_result.text)
                GLib.idle_add(self._on_ocr_done, ocr_result, translation, None)
            except Exception as e:
                GLib.idle_add(self._on_ocr_done, None, "", e)
            finally:
                try:
                    import os

                    if os.path.exists(path):
                        os.remove(path)
                except Exception as ex:
                    print(f"Failed to delete screenshot {path}: {ex}")

        threading.Thread(target=ocr_thread, daemon=True).start()

    def _on_ocr_done(self, ocr_result, translation, error):
        if error:
            traceback.print_exc()
            self.emit_capture_result(("", [], 0.0, str(error)))
            return

        try:
            text = ocr_result.text
            confidence = ocr_result.confidence

            if not text:
                defs = []
            else:
                defs = self.dictionary.lookup(text)

            def_list = []
            for d in defs:
                def_list.append(
                    {
                        "reading": d.reading,
                        "meanings": "; ".join(d.meanings),
                        "part_of_speech": d.part_of_speech,
                    }
                )

            res_tuple = (text, def_list, confidence, translation)
            self.emit_capture_result(res_tuple)

            show_popup(text, defs, translation)

        except Exception as e:
            traceback.print_exc()
            self.emit_capture_result(("", [], 0.0, str(e)))

    def start_full_screen_capture(self):
        output_path = "/tmp/japanese-wayland-capture.png"
        screenshot_full_screen(output_path, self._process_screenshot, interactive=False)

    def start_area_capture(self):
        output_path = "/tmp/japanese-wayland-capture.png"
        screenshot_full_screen(output_path, self._process_screenshot, interactive=True)
