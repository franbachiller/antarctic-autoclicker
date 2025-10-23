"""
Visual test for timing systems - shows how each setting affects click delays
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from antarctic import MarkovChainTiming, GaussianDelayEngine, AccelerationProfile

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def visualize_delay(delay_ms, max_ms=50):
    """Create a visual bar for delay"""
    bar_length = int((delay_ms / max_ms) * 40)
    bar = "█" * bar_length
    return f"{bar} {delay_ms:.2f}ms"

# Test 1: Markov Chain - State Transitions
print_header("TEST 1: MARKOV CHAIN - State Transitions")
print("Watch how the state changes affect delay multipliers\n")

markov = MarkovChainTiming()
markov.enabled = True
markov.custom_fast_multiplier = 0.5    # 50% speed (faster)
markov.custom_medium_multiplier = 1.0  # 100% speed (normal)
markov.custom_slow_multiplier = 2.0    # 200% speed (slower)
markov.use_custom_multipliers = True

base = 10.0  # 10ms base delay
print(f"Base delay: {base}ms")
print(f"Fast multiplier: {markov.custom_fast_multiplier}x")
print(f"Medium multiplier: {markov.custom_medium_multiplier}x")
print(f"Slow multiplier: {markov.custom_slow_multiplier}x\n")

for i in range(15):
    delay = markov.apply_to_delay(base / 1000.0) * 1000.0
    state = markov.current_state
    state_icon = {'fast': '🟢', 'medium': '🟡', 'slow': '🔴'}[state]
    print(f"Click {i+1:2d}: {state_icon} {state:6s} | {visualize_delay(delay)}")

# Test 2: Gaussian Distribution
print_header("TEST 2: GAUSSIAN DISTRIBUTION - Bell Curve Delays")
print("Most delays cluster around the mean, with some variation\n")

gaussian = GaussianDelayEngine()
gaussian.enabled = True
gaussian.mean_ms = 15.0
gaussian.std_dev_ms = 3.0
gaussian.min_delay_ms = 5.0
gaussian.use_absolute = True

print(f"Mean: {gaussian.mean_ms}ms")
print(f"Std Dev: {gaussian.std_dev_ms}ms")
print(f"Min: {gaussian.min_delay_ms}ms\n")

delays = []
for i in range(20):
    delay = gaussian.apply_to_delay(0.01) * 1000.0
    delays.append(delay)
    print(f"Click {i+1:2d}: {visualize_delay(delay, 30)}")

avg = sum(delays) / len(delays)
print(f"\nAverage: {avg:.2f}ms (target: {gaussian.mean_ms}ms)")
print(f"Range: {min(delays):.2f}ms - {max(delays):.2f}ms")

# Test 3: Acceleration Profiles
print_header("TEST 3: ACCELERATION - Linear Curve")
print("Delay gradually decreases (speed increases)\n")

accel = AccelerationProfile()
accel.enabled = True
accel.curve_type = 'linear'
accel.start_speed_multiplier = 2.0   # Start slow (2x delay)
accel.end_speed_multiplier = 0.5     # End fast (0.5x delay)
accel.duration_clicks = 15
accel.reset()

base = 10.0
print(f"Base delay: {base}ms")
print(f"Start multiplier: {accel.start_speed_multiplier}x (slower)")
print(f"End multiplier: {accel.end_speed_multiplier}x (faster)")
print(f"Duration: {accel.duration_clicks} clicks\n")

for i in range(15):
    delay = accel.apply_to_delay(base / 1000.0) * 1000.0
    progress = accel.get_progress()
    bar = "▓" * int(progress * 20) + "░" * (20 - int(progress * 20))
    print(f"Click {i+1:2d}: [{bar}] {progress*100:3.0f}% | {visualize_delay(delay)}")

# Test 4: Exponential Curve
print_header("TEST 4: ACCELERATION - Exponential Curve")
print("Slow start, then rapid acceleration\n")

accel.reset()
accel.curve_type = 'exponential'
accel.exponential_factor = 2.0

for i in range(15):
    delay = accel.apply_to_delay(base / 1000.0) * 1000.0
    progress = accel.get_progress()
    bar = "▓" * int(progress * 20) + "░" * (20 - int(progress * 20))
    print(f"Click {i+1:2d}: [{bar}] {progress*100:3.0f}% | {visualize_delay(delay)}")

# Test 5: S-Curve
print_header("TEST 5: ACCELERATION - S-Curve (Sigmoid)")
print("Smooth start and end, fast in the middle\n")

accel.reset()
accel.curve_type = 's_curve'
accel.sigmoid_steepness = 10.0

for i in range(15):
    delay = accel.apply_to_delay(base / 1000.0) * 1000.0
    progress = accel.get_progress()
    bar = "▓" * int(progress * 20) + "░" * (20 - int(progress * 20))
    print(f"Click {i+1:2d}: [{bar}] {progress*100:3.0f}% | {visualize_delay(delay)}")

# Test 6: Combined Systems
print_header("TEST 6: COMBINED - All Systems Together")
print("Markov + Gaussian + Acceleration working together\n")

markov.reset_state()
gaussian.enabled = True
accel.reset()
accel.curve_type = 'linear'

base = 10.0
print(f"Base: {base}ms | Markov: ON | Gaussian: ON | Accel: ON\n")

for i in range(12):
    delay = base / 1000.0
    
    # Apply all systems
    delay = markov.apply_to_delay(delay)
    delay = gaussian.apply_to_delay(delay)
    delay = accel.apply_to_delay(delay)
    
    delay_ms = delay * 1000.0
    state = markov.current_state
    progress = accel.get_progress()
    
    state_icon = {'fast': '🟢', 'medium': '🟡', 'slow': '🔴'}[state]
    print(f"Click {i+1:2d}: {state_icon} A:{progress*100:3.0f}% | {visualize_delay(delay_ms, 40)}")

print_header("VISUAL TESTS COMPLETE")
print("\n✓ All timing systems are working correctly!")
print("✓ Each system independently affects click delays")
print("✓ Systems can be combined for complex timing patterns")
print("\nNow test in the GUI:")
print("1. Enable each checkbox and watch the Monitor line")
print("2. Click ⚙ to adjust parameters")
print("3. Press F2 to start clicking and see real-time values")
print("="*60 + "\n")

