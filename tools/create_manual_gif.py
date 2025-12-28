"""
Manual GIF Creator - Convert screenshots to GIF
Use this if you want to manually take screenshots and convert them to GIF
"""

import os
from PIL import Image
import glob

def create_gif_from_images(image_folder, output_path, duration=800):
    """
    Create GIF from images in a folder
    
    Args:
        image_folder: Folder containing PNG/JPG images
        output_path: Output GIF path
        duration: Duration per frame in milliseconds
    """
    
    print("Manual GIF Creator")
    print("=" * 50)
    
    # Find all images
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        image_files.extend(glob.glob(os.path.join(image_folder, ext)))
    
    image_files.sort()
    
    if not image_files:
        print(f"Error: No images found in {image_folder}")
        return
    
    print(f"\nFound {len(image_files)} images:")
    for img in image_files:
        print(f"  - {os.path.basename(img)}")
    
    # Load images
    print("\nLoading images...")
    frames = []
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            frames.append(img.convert('RGB'))
        except Exception as e:
            print(f"  Warning: Could not load {img_path}: {e}")
    
    if not frames:
        print("Error: No valid images loaded!")
        return
    
    # Optimize size
    print("\nOptimizing images...")
    max_width = 800
    optimized_frames = []
    
    for frame in frames:
        if frame.width > max_width:
            ratio = max_width / frame.width
            new_size = (max_width, int(frame.height * ratio))
            frame = frame.resize(new_size, Image.Resampling.LANCZOS)
        optimized_frames.append(frame)
    
    # Create GIF
    print(f"\nCreating GIF: {output_path}")
    optimized_frames[0].save(
        output_path,
        save_all=True,
        append_images=optimized_frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )
    
    file_size = os.path.getsize(output_path) / 1024
    print(f"\n✓ GIF created successfully!")
    print(f"  Output: {output_path}")
    print(f"  Size: {file_size:.1f} KB")
    print(f"  Frames: {len(optimized_frames)}")
    print(f"  Duration: {len(optimized_frames) * duration / 1000:.1f} seconds")
    
    print("\n" + "=" * 50)
    print("Add to README.md with:")
    print(f'![Antarctic Demo]({os.path.relpath(output_path, os.path.dirname(__file__) + "/..")})')
    print("=" * 50)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python create_manual_gif.py <image_folder> [output.gif] [duration_ms]")
        print("\nExample:")
        print("  python create_manual_gif.py screenshots/ demo.gif 1000")
        print("\nSteps:")
        print("  1. Create a folder (e.g., 'screenshots')")
        print("  2. Take screenshots of your app and save them there")
        print("  3. Name them in order (e.g., 01.png, 02.png, etc.)")
        print("  4. Run this script")
        sys.exit(1)
    
    image_folder = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.gif"
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 800
    
    create_gif_from_images(image_folder, output_path, duration)
