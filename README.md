# Wayland Overlay — Japanese Wayland

A screen text capture and dictionary lookup tool for Japanese, built for **GNOME + Wayland**.

---

## Features

- **Area Capture** (`Super+Shift+J`): Drag to select a region → OCR → popup definition
- **Full Screen Capture** (`Super+Shift+A`): Capture entire screen → OCR → popup definition
- **Pluggable OCR**: Defaults to Tesseract CLI (with `jpn` + `jpn_vert` data).
Designed to swap in MangaOCR or other engines later.
- **Native GTK4 Popup**: Dark-themed popup with extracted text, readings, and definitions.

---

## Requirements

### System Packages

```bash
# Arch Linux
sudo pacman -S tesseract tesseract-data-jpn tesseract-data-jpn-vert gtk4

# Optional: for precise Wayland popup positioning
sudo pacman -S gtk4-layer-shell
```

### Python

Python 3 is required. The project uses:
- `PyGObject` (`python3-gi`) for DBus communication and GTK4 popup window

---

## Installation

### 1. Download JMdict Database

The application requires the JMdict XML dictionary file to perform word lookups and filter OCR artifacts.

```bash
mkdir -p dictionary
wget http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz
gunzip JMdict_e.gz
mv JMdict_e dictionary/JMdict
```

### 2. Run the Install Script

Clone the repository and run the install script:

```bash
git clone https://github.com/sayden/japanese-wayland.git
cd japanese-wayland
./install.sh
```

This will:
1. Stop any running service
2. Install the new Python service unit to `~/.config/systemd/user/japanese-wayland.service`
3. Install and start the systemd user service
4. Install the GNOME Shell extension
5. Compile the gsettings schema

After installation:

```bash
# Enable the extension
gnome-extensions enable japanese-wayland@japanese-wayland

# Verify the service is running
systemctl --user status japanese-wayland.service

# Check the service logs
journalctl --user -u japanese-wayland.service -f
```

---

## Usage

| Hotkey | Action |
|--------|--------|
| `Super+Shift+J` | Select an area to capture and OCR |
| `Super+Shift+A` | Capture the entire screen and OCR |

After triggering, the service will:
1. Call xdg-desktop-portal Screenshot API
2. Save the image to `/tmp/japanese-wayland-capture.png`
3. Run OCR with Tesseract (`jpn+jpn_vert`)
4. Look up the text in the dictionary
5. Show a GTK4 popup with the results

---

## Project Structure

```
japanese-wayland/
├── service/
│   ├── japanese-wayland.py       # Service entry point
│   ├── dbus_service.py           # DBus service
│   ├── screenshot.py             # Desktop portal Screenshot DBus calls
│   ├── ocr.py                    # Tesseract OCR engine
│   ├── dictionary.py             # Offline dictionary
│   └── popup.py                  # GTK4 popup window
├── extension/
│   ├── extension.js              # GNOME Shell Extension
│   ├── metadata.json             # Extension metadata
│   └── schemas/                  # GSettings schema for hotkeys
├── systemd/
│   └── japanese-wayland.service   # systemd user service unit
├── install.sh                    # One-command install script
└── README.md                     # This file
```

---

## How It Works

### Screenshot Flow

1. The **GNOME Extension** catches the hotkey and calls the Python service via DBus.
2. The **Python service** calls `org.freedesktop.portal.Desktop.Screenshot()`.
3. GNOME Shell handles the area selection UI and saves the image.
4. The service runs **Tesseract OCR** on the image.
5. The extracted text is passed to the **dictionary** module.
6. A **GTK4 popup** is shown with the results.

### Why Not Pure Python DBus?

On Wayland, applications cannot arbitrarily capture other windows' pixels or set global hotkeys easily. The xdg-desktop-portal DBus service is an API that allows capturing the screen interactively. The most robust hotkey integration is achieved with a tiny GNOME Shell Extension for key registration that calls into our Python logic.

---

## Known Limitations

- **Popup Positioning**: Without `gtk4-layer-shell`, the popup window is positioned by the GNOME compositor, not at the exact top-right of the selection. Install `gtk4-layer-shell` and enable the feature flag for precise positioning.
- **OCR Quality**: Tesseract is good for PDFs and standard text, but stylized game text may need [MangaOCR](https://github.com/kha-white/manga-ocr) in the future.
- **DBus API**: `org.gnome.Shell.Screenshot` is an internal GNOME API. It works on GNOME 45–50, but could change in future releases.

---

## License

MIT
