import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, Gtk, Pango


def show_popup(text: str, definitions: list, translation: str = None):
    """
    Shows a popup window with the extracted text and definitions.
    """
    window = Gtk.Window()
    window.set_title("Japanese Wayland")
    window.set_default_size(620, 800)
    window.set_decorated(False)
    window.set_resizable(True)

    # Styling
    display = Gdk.Display.get_default()
    if display:
        provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: #1e1e1e;
            border-radius: 8px;
            border: 1px solid #3a3a3a;
        }
        label {
            color: #e0e0e0;
            font-size: 18px;
        }
        .heading {
            font-weight: bold;
            font-size: 20px;
            color: #ffffff;
        }
        .reading {
            color: #a0a0a0;
            font-size: 16px;
        }
        .pos {
            color: #7aa2f7;
            font-size: 12px;
            font-style: italic;
        }
        .translation {
            color: #e0af68;
            font-size: 14px;
            font-style: italic;
            margin-top: 4px;
            margin-bottom: 8px;
        }
        """
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    vbox.set_margin_top(12)
    vbox.set_margin_bottom(12)
    vbox.set_margin_start(12)
    vbox.set_margin_end(12)

    # Extracted text heading
    text_label = Gtk.Label(label=text)
    text_label.add_css_class("heading")
    text_label.set_wrap(True)
    text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    vbox.append(text_label)

    # Translation label
    if translation:
        trans_label = Gtk.Label(label=translation)
        trans_label.add_css_class("translation")
        trans_label.set_halign(Gtk.Align.START)
        trans_label.set_wrap(True)
        trans_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        vbox.append(trans_label)

    # Definitions list
    if definitions:
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        for def_obj in definitions:
            row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            row_box.set_margin_top(6)
            row_box.set_margin_bottom(6)
            row_box.set_margin_start(6)
            row_box.set_margin_end(6)

            if def_obj.reading and def_obj.reading != text:
                reading = Gtk.Label(label=f"Reading: {def_obj.reading}")
                reading.add_css_class("reading")
                reading.set_halign(Gtk.Align.START)
                row_box.append(reading)

            pos = Gtk.Label(label=def_obj.part_of_speech)
            pos.add_css_class("pos")
            pos.set_halign(Gtk.Align.START)
            row_box.append(pos)

            meanings_str = "; ".join(def_obj.meanings)
            meanings = Gtk.Label(label=meanings_str)
            meanings.set_halign(Gtk.Align.START)
            meanings.set_wrap(True)
            meanings.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            row_box.append(meanings)

            row = Gtk.ListBoxRow()
            row.set_child(row_box)
            list_box.append(row)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(list_box)
        vbox.append(scrolled)
    else:
        no_def = Gtk.Label(label="No definitions found.")
        no_def.set_halign(Gtk.Align.START)
        vbox.append(no_def)

    window.set_child(vbox)

    # Close on Escape
    controller = Gtk.EventControllerKey()

    def on_key_pressed(controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            window.close()
            return True
        return False

    controller.connect("key-pressed", on_key_pressed)
    window.add_controller(controller)

    # Dismiss on focus-out
    def on_notify_is_active(window, param):
        if not window.get_property("is-active"):
            window.close()

    window.connect("notify::is-active", on_notify_is_active)

    window.present()
    return window
