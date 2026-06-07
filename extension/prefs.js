import Adw from 'gi://Adw';
import Gtk from 'gi://Gtk';
import Gdk from 'gi://Gdk';
import { ExtensionPreferences } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class JapaneseWaylandPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        window.search_enabled = true;

        const page = new Adw.PreferencesPage();
        const group = new Adw.PreferencesGroup({
            title: 'Keyboard Shortcuts',
            description: 'Configure hotkeys for capturing the screen'
        });
        page.add(group);

        const settings = this.getSettings('org.gnome.shell.extensions.japanese-wayland');

        const createShortcutRow = (title, subtitle, settingsKey) => {
            const row = new Adw.ActionRow({
                title,
                subtitle
            });

            const button = new Gtk.Button({
                valign: Gtk.Align.CENTER,
                has_frame: true,
            });
            row.add_suffix(button);

            const updateButtonLabel = () => {
                const shortcuts = settings.get_strv(settingsKey);
                button.label = (shortcuts && shortcuts.length > 0 && shortcuts[0]) ? shortcuts[0] : 'Disabled';
            };
            updateButtonLabel();

            settings.connect(`changed::${settingsKey}`, updateButtonLabel);

            const keyController = new Gtk.EventControllerKey();
            button.add_controller(keyController);

            let listening = false;

            button.connect('clicked', () => {
                listening = true;
                button.label = 'Press new shortcut...';
                button.add_css_class('suggested-action');
            });

            keyController.connect('key-pressed', (controller, keyval, keycode, state) => {
                if (!listening) return Gdk.EVENT_PROPAGATE;

                let mask = state & Gtk.accelerator_get_default_mod_mask();
                // We use standard GTK logic to get the string
                const name = Gtk.accelerator_name(keyval, mask);

                // Press Escape (no modifiers) to cancel
                if (name === 'Escape') {
                    listening = false;
                    button.remove_css_class('suggested-action');
                    updateButtonLabel();
                    return Gdk.EVENT_STOP;
                }

                // Press BackSpace (no modifiers) to clear
                if (name === 'BackSpace') {
                    listening = false;
                    button.remove_css_class('suggested-action');
                    settings.set_strv(settingsKey, []);
                    return Gdk.EVENT_STOP;
                }

                if (Gtk.accelerator_valid(keyval, mask)) {
                    settings.set_strv(settingsKey, [name]);
                    listening = false;
                    button.remove_css_class('suggested-action');
                    return Gdk.EVENT_STOP;
                }
                
                return Gdk.EVENT_PROPAGATE;
            });

            button.connect('notify::has-focus', () => {
                if (!button.has_focus && listening) {
                    listening = false;
                    button.remove_css_class('suggested-action');
                    updateButtonLabel();
                }
            });

            return row;
        };

        group.add(createShortcutRow('Area Capture', 'Hotkey for selecting a specific area on screen', 'area-capture'));
        group.add(createShortcutRow('Full Screen Capture', 'Hotkey for capturing the entire screen', 'full-screen-capture'));

        window.add(page);
    }
}
