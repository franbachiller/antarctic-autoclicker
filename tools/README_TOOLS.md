# Tools Documentation

This directory contains utility scripts for Antarctic development and maintenance.

## Demo GIF Creation

### Option 1: Automatic Capture (Recommended)

**Script**: `create_demo_gif.py`

Automatically launches the application, captures screenshots, and creates an animated GIF.

**Requirements:**
```bash
pip install pillow pyautogui pywin32
```

**Usage:**
```bash
python tools/create_demo_gif.py
```

**What it does:**
1. Launches Antarctic application
2. Finds the window automatically
3. Captures 8 frames showing different sections
4. Creates optimized GIF (800px width)
5. Saves to `assets/demo/antarctic_demo.gif`

**Output:**
- Optimized GIF ready for GitHub
- Automatic cleanup of temporary files
- Instructions for adding to README

---

### Option 2: Manual Screenshots

**Script**: `create_manual_gif.py`

Convert your own screenshots into a GIF.

**Requirements:**
```bash
pip install pillow
```

**Steps:**

1. Create a folder for screenshots:
```bash
mkdir screenshots
```

2. Take screenshots of your app:
   - Press `Win + Shift + S` (Windows Snipping Tool)
   - Or use any screenshot tool
   - Save them as `01.png`, `02.png`, etc.

3. Run the script:
```bash
python tools/create_manual_gif.py screenshots/ assets/demo/antarctic_demo.gif 1000
```

**Arguments:**
- `screenshots/` - Folder with your images
- `assets/demo/antarctic_demo.gif` - Output path
- `1000` - Duration per frame in milliseconds (optional, default: 800)

---

### Option 3: Screen Recording (Easiest)

Use a screen recording tool and convert to GIF:

**Recommended Tools:**

1. **ScreenToGif** (Free, Windows)
   - Download: https://www.screentogif.com/
   - Record your screen
   - Built-in GIF editor
   - Export optimized GIF

2. **LICEcap** (Free, Windows/Mac)
   - Download: https://www.cockos.com/licecap/
   - Simple and lightweight
   - Direct GIF recording

3. **Kap** (Free, Mac)
   - Download: https://getkap.co/
   - Modern interface
   - High-quality output

**Steps:**
1. Open the tool
2. Position the recording area over Antarctic window
3. Start recording
4. Demonstrate features (10-15 seconds)
5. Stop recording
6. Save as `assets/demo/antarctic_demo.gif`

---

## Other Tools

### License Management

**create_licenses.py**
- Bulk license creation
- Supports all license types
- Direct database insertion

**key_generator.py**
- Generate license keys
- Format: XXXX-XXXX-XXXX-XXXX
- Cryptographically secure

### Release Management

**release.py**
- Automated release process
- Version bumping
- Changelog generation
- GitHub release creation

**migrate_to_github_releases.py**
- Migrate old releases to GitHub
- Preserve release history

### Graphics

**create_logo.py**
- Generate application logos
- Multiple sizes
- Icon generation

---

## Adding GIF to README

Once you have your GIF, add it to the README:

```markdown
# Antarctic Autoclicker

![Antarctic Demo](assets/demo/antarctic_demo.gif)

Advanced autoclicker system with license management...
```

**Best Practices:**
- Keep GIF under 5MB for fast loading
- 800px width is optimal for GitHub
- 10-15 seconds duration
- Show key features
- Loop seamlessly

---

## Tips for Great Demo GIFs

1. **Clean Interface**
   - Close unnecessary windows
   - Use default theme
   - Clear any personal data

2. **Show Key Features**
   - License activation
   - Configuration options
   - Timing modes
   - Latency compensation
   - Profile management

3. **Smooth Transitions**
   - Don't rush
   - Pause on important screens
   - Use smooth mouse movements

4. **Optimize Size**
   - Reduce resolution if needed
   - Limit color palette
   - Use tools' optimization features

5. **Test Before Publishing**
   - Preview the GIF
   - Check file size
   - Verify it loops well
   - Test on GitHub (in a draft PR)
