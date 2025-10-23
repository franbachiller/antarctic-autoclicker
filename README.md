# 🐧 ANTARCTIC - Ultra Clicker

Professional autoclicker with cloud license system and advanced timing features.

## 📁 Project Structure

```
Antarctic/
├── src/                    # Source code
│   ├── antarctic.py       # Main application
│   ├── auth_client.py     # License authentication client
│   └── security.py        # Anti-debugging & security
│
├── build/                  # Build scripts
│   ├── compile.bat        # PyInstaller + PyArmor compilation
│   └── clean.bat          # Clean build artifacts
│
├── dist/                   # Compiled executables
│   └── Antarctic.exe      # Final application
│
├── assets/                 # Images and icons
│   ├── icon.ico           # Application icon
│   ├── logo.png           # Full logo
│   └── logo_compact.png   # Compact logo
│
├── website/                # Landing page
│   ├── index.html         # Main page
│   ├── script.js          # JavaScript
│   └── styles.css         # Styles
│
├── documentation/          # Documentation files
│   ├── README.md          # User guide
│   ├── SLIDERS_GUIDE.md   # Slider configuration guide
│   ├── test_sliders.py    # Testing script
│   └── antarctic_backup.py # Backup version
│
├── tools/                  # Utility scripts
│   ├── key_generator.py   # License key generator
│   ├── create_logo.py     # Logo generator
│   └── create_licenses.py # License creation tool
│
└── docs/                   # Additional documentation

```

## 🚀 Quick Start

### Building from Source

1. Navigate to build directory:
   ```bash
   cd build
   ```

2. Run compilation:
   ```bash
   compile.bat
   ```

3. Find executable in:
   ```
   dist/Antarctic.exe
   ```

### Running the Application

1. Launch `Antarctic.exe`
2. Enter license key (format: `ANTARCTIC-XXXX-XXXX-XXXX`)
3. Configure sliders and options
4. Press `F3` to capture target coordinates
5. Press `F2` to execute burst
6. Press `F5` to toggle auto-burst mode

## 🔧 Configuration

### Sliders
- **Clicks/Batch**: Number of clicks per burst (1-100)
- **Interval (ms)**: Delay between clicks (1-200ms)
- **Duration (s)**: How long each burst lasts (0.01-2.0s)
- **Auto-Burst Delay**: Delay before auto-burst starts (0-1.0s)

### Options
- **Humanization**: Adds random variation to clicks
- **Burst Variations**: Uses advanced timing patterns
- **ULTRA MODE**: Maximum speed (no delays)
- **AUTO-BURST**: Trigger on left click when F5 enabled

### Hotkeys
- `F3` - Capture target coordinates
- `F2` - Execute burst manually
- `F5` - Toggle auto-burst mode

## 🔒 Security Features

- **PyArmor Obfuscation**: Critical modules protected
- **HWID Binding**: License tied to hardware
- **Cloud Authentication**: Online license validation
- **Anti-Debugging**: Detects reverse engineering tools
- **Session Encryption**: Secure local storage

## 🌐 License System

### Server
- Deployed on Vercel: `https://antarctic-autoclicker.vercel.app`
- Backend: Node.js + Supabase
- Real-time validation
- Admin panel included

### Admin Panel
- License management
- Usage statistics
- Activation monitoring
- HWID tracking

## 📊 Features

### Timing Modes
1. **Normal**: Consistent intervals
2. **Humanization**: Random variation
3. **Burst Variations**: Complex patterns
4. **ULTRA**: Maximum speed

### Profile System
- Save/Load up to 5 configurations
- Persistent settings
- Quick switching

### Target Detection
- Auto-connects to BoomBang window
- Real-time status indicator
- Coordinates capture system

## 🛠️ Development

### Requirements
```bash
pip install customtkinter pillow requests psutil pyarmor pyinstaller
```

### Testing
```bash
cd documentation
python test_sliders.py
```

### Cleaning Build Files
```bash
cd build
clean.bat
```

## 📝 Version History

### Current Version
- Fixed slider functionality
- Improved UI design
- Enhanced stats display
- Removed emoji clutter
- Better timing system

## ⚠️ Important Notes

- Requires active internet for license validation
- Grace period: 1 hour offline mode
- Compatible with Windows 10/11
- Target window: "BoomBang"

## 🤝 Support

For license issues or support, contact the administrator through the admin panel.

---

**Built with:** Python 3.13 | CustomTkinter | PyArmor | PyInstaller
**Security Level:** ★★★★★ (5/5)
