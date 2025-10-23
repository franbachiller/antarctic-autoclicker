"""Quick test to verify the UI displays correctly"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing Antarctic UI...")
print("1. Importing modules...")

try:
    from antarctic import AntarcticGUI, KeyManager
    print("   ✓ Imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

print("\n2. Creating GUI instance...")
try:
    key_manager = KeyManager()
    app = AntarcticGUI(key_manager)
    print("   ✓ GUI created successfully")
except Exception as e:
    print(f"   ✗ GUI creation failed: {e}")
    sys.exit(1)

print("\n3. Checking UI elements...")
try:
    # Check if timing monitor label exists
    if hasattr(app, 'timing_monitor_label'):
        print("   ✓ Timing monitor label exists")
        print(f"   ✓ Initial text: '{app.timing_monitor_label.cget('text')}'")
    else:
        print("   ✗ Timing monitor label NOT found")
    
    # Check checkboxes
    if hasattr(app, 'markov_checkbox'):
        print("   ✓ Markov checkbox exists")
    else:
        print("   ✗ Markov checkbox NOT found")
    
    if hasattr(app, 'gaussian_checkbox'):
        print("   ✓ Gaussian checkbox exists")
    else:
        print("   ✗ Gaussian checkbox NOT found")
    
    if hasattr(app, 'accel_checkbox'):
        print("   ✓ Accel checkbox exists")
    else:
        print("   ✗ Accel checkbox NOT found")
    
except Exception as e:
    print(f"   ✗ UI check failed: {e}")
    sys.exit(1)

print("\n4. Starting application...")
print("   → The GUI window should now be visible")
print("   → Look for the 'Advanced Timing' section")
print("   → You should see 3 checkboxes and a monitor line")
print("   → Close the window to exit\n")

try:
    app.mainloop()
except KeyboardInterrupt:
    print("\n   ✓ Application closed")
except Exception as e:
    print(f"\n   ✗ Application error: {e}")
    sys.exit(1)

print("\n✓ Test complete!")

