#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_UUID="japanese-wayland@japanese-wayland"

echo "=== Wayland Overlay Japanese Wayland — Python Install ==="

# 1. Stop and remove old Rust service if present
systemctl --user stop japanese-wayland.service 2>/dev/null || true
systemctl --user disable japanese-wayland.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/japanese-wayland.service"

# 2. Install new Python service
echo "[1/3] Installing Python service..."
mkdir -p "$HOME/.config/systemd/user"
cp "$SCRIPT_DIR/systemd/japanese-wayland-python.service" "$HOME/.config/systemd/user/japanese-wayland.service"
systemctl --user daemon-reload
systemctl --user enable japanese-wayland.service
systemctl --user start japanese-wayland.service

# 3. Install GNOME extension
echo "[2/3] Installing GNOME extension..."
mkdir -p "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID"
cp "$SCRIPT_DIR/extension/extension.js" "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID/"
cp "$SCRIPT_DIR/extension/prefs.js" "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID/"
cp "$SCRIPT_DIR/extension/metadata.json" "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID/"
mkdir -p "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID/schemas"
cp "$SCRIPT_DIR/extension/schemas/org.gnome.shell.extensions.japanese-wayland.gschema.xml" "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID/schemas/"
glib-compile-schemas "$HOME/.local/share/gnome-shell/extensions/$EXTENSION_UUID/schemas/"

# 4. Verify service
echo "[3/3] Verifying service..."
sleep 2
if busctl --user list | grep -q "com.japanesewayland.JapaneseWayland"; then
    echo "✓ Service is running on DBus"
else
    echo "✗ Service not found on DBus. Check logs:"
    echo "  journalctl --user -u japanese-wayland.service -n 20"
fi

echo ""
echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "  1. Restart GNOME Shell: Alt+F2, type 'r', press Enter"
echo "  2. Enable the extension:"
echo "       gnome-extensions enable $EXTENSION_UUID"
echo "  3. Check the service status:"
echo "       systemctl --user status japanese-wayland.service"
echo "  4. Try the hotkey:"
echo "       Super+Shift+A  → Full screen capture"
echo ""
echo "To check logs:"
echo "  journalctl --user -u japanese-wayland.service -f"
echo ""
