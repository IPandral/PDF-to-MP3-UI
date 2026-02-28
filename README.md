# PDF-to-MP3-UI

PDF-to-MP3-UI is a desktop app that converts PDF text into MP3 audio using a simple graphical interface.

It is designed for users who prefer listening to written content, including accessibility and productivity use cases.

---

## Features

- Convert a single PDF to MP3
- Convert a folder of PDFs
- Save generated MP3 files to a selected output folder
- Open output folder after conversion
- Built-in audio playback controls in the app

---

## Downloads

Get the latest packaged app from the **[Releases page](https://github.com/IPandral/PDF-to-MP3-UI/releases)**.

---

## Prerequisites

### Windows (Important)

This app uses VLC runtime libraries for audio playback.

Before running `PDF-to-MP3-UI.exe`, make sure:

1. **VLC Media Player is installed**  
   Download from the official site: [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)
2. **Architecture matches**  
   - 64-bit app ↔ 64-bit VLC  
   - 32-bit app ↔ 32-bit VLC
3. `libvlc.dll` is present in your VLC installation directory (for example):
   - `C:\Program Files\VideoLAN\VLC\libvlc.dll`
   - `C:\Program Files (x86)\VideoLAN\VLC\libvlc.dll`
   If you installed VLC to a custom location, ensure `libvlc.dll` exists in that install directory.

If VLC is not installed or not found, the app may fail to start with a `libvlc.dll` error.

### macOS

Use the `.dmg` from Releases and drag `PDFtoMP3UI.app` into Applications.

If blocked on first launch, allow it via:  
**System Settings/Preferences → Privacy & Security → Open Anyway**

---

## Usage

### Windows

1. Install VLC (see prerequisites above).
2. Run `PDF-to-MP3-UI.exe`.
3. Select a PDF file (or PDF folder).
4. Select an output folder.
5. Start conversion.

### macOS

1. Open `PDFtoMP3UI.app`.
2. Select a PDF file (or PDF folder).
3. Select an output folder.
4. Start conversion.

---

## Troubleshooting

### Error: `Could not find module ... libvlc.dll`

- Install VLC from VideoLAN.
- Ensure VLC architecture matches the app.
- Restart Windows after installing VLC.
- Confirm `libvlc.dll` exists in the VLC install directory.

### App opens but conversion fails

- Check the PDF is readable and not corrupted.
- Check output folder write permissions.
- Try a different output folder.

---

## Known Issues

- On macOS, first launch may require manual security approval.
- On Windows, missing VLC runtime prevents audio features and can block startup in some builds.

---

## Related Project

Prefer terminal usage?  
See **[PDF-to-MP3-CLI](https://github.com/IPandral/PDF-to-MP3-CLI)**.

---

## License

MIT License. See [LICENSE](LICENSE).
