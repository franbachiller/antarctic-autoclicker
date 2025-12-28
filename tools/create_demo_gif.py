"""
Create animated GIF demo of Antarctic application
Captures screenshots of the running application and creates an animated GIF
"""

import time
import os
from PIL import Image, ImageGrab
import pyautogui
import subprocess
import sys

def find_window_by_title(title_substring):
    """Find window by title substring"""
    try:
        import win32gui
        
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title_substring.lower() in window_title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None
    except ImportError:
        print("Error: pywin32 not installed. Install with: pip install pywin32")
        return None

def capture_window(hwnd, output_path):
    """Capture a specific window"""
    try:
        import win32gui
        import win32ui
        import win32con
        from ctypes import windll
        
        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        # Bring window to front
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        # Capture the window
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        screenshot.save(output_path)
        return screenshot
    except Exception as e:
        print(f"Error capturing window: {e}")
        return None

def create_demo_gif():
    """Create demo GIF of the application"""
    
    print("Antarctic Demo GIF Creator")
    print("=" * 50)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'demo')
    os.makedirs(output_dir, exist_ok=True)
    
    # Start the application
    print("\n1. Starting Antarctic application...")
    app_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'antarctic.py')
    
    # Launch the app
    process = subprocess.Popen([sys.executable, app_path])
    
    # Wait for app to start
    print("   Waiting for application to start...")
    time.sleep(3)
    
    # Find the window
    print("\n2. Finding application window...")
    hwnd = find_window_by_title("Antarctic")
    
    if not hwnd:
        print("   Error: Could not find Antarctic window!")
        print("   Make sure the application is running.")
        process.terminate()
        return
    
    print("   Window found!")
    
    # Capture sequence
    print("\n3. Capturing screenshots...")
    frames = []
    frame_paths = []
    
    # Define capture sequence (time in seconds, description)
    sequence = [
        (0.5, "Main interface"),
        (1.0, "License section"),
        (1.5, "Click configuration"),
        (2.0, "Timing modes"),
        (2.5, "Latency compensation"),
        (3.0, "Profile management"),
        (3.5, "Statistics"),
        (4.0, "Final view"),
    ]
    
    for i, (delay, description) in enumerate(sequence):
        time.sleep(delay)
        frame_path = os.path.join(output_dir, f'frame_{i:02d}.png')
        print(f"   Capturing frame {i+1}/{len(sequence)}: {description}")
        
        screenshot = capture_window(hwnd, frame_path)
        if screenshot:
            frames.append(screenshot)
            frame_paths.append(frame_path)
    
    # Close the application
    print("\n4. Closing application...")
    process.terminate()
    time.sleep(0.5)
    
    if not frames:
        print("   Error: No frames captured!")
        return
    
    # Create GIF
    print("\n5. Creating animated GIF...")
    gif_path = os.path.join(output_dir, 'antarctic_demo.gif')
    
    # Optimize frames (resize if too large)
    max_width = 800
    optimized_frames = []
    
    for frame in frames:
        if frame.width > max_width:
            ratio = max_width / frame.width
            new_size = (max_width, int(frame.height * ratio))
            frame = frame.resize(new_size, Image.Resampling.LANCZOS)
        optimized_frames.append(frame)
    
    # Save as GIF
    optimized_frames[0].save(
        gif_path,
        save_all=True,
        append_images=optimized_frames[1:],
        duration=800,  # 800ms per frame
        loop=0,  # Loop forever
        optimize=True
    )
    
    print(f"\n✓ GIF created successfully: {gif_path}")
    print(f"  Size: {os.path.getsize(gif_path) / 1024:.1f} KB")
    print(f"  Frames: {len(optimized_frames)}")
    print(f"  Duration: {len(optimized_frames) * 0.8:.1f} seconds")
    
    # Clean up frame files
    print("\n6. Cleaning up temporary files...")
    for frame_path in frame_paths:
        try:
            os.remove(frame_path)
        except:
            pass
    
    print("\n" + "=" * 50)
    print("Demo GIF creation complete!")
    print(f"Add to README.md with:")
    print(f'![Antarctic Demo](assets/demo/antarctic_demo.gif)')
    print("=" * 50)

if __name__ == "__main__":
    try:
        create_demo_gif()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
