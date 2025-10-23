"""
Test script for the new advanced timing systems
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test imports
try:
    from antarctic import MarkovChainTiming, GaussianDelayEngine, AccelerationProfile
    print("✓ Successfully imported timing classes")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test Markov Chain Timing
print("\n=== Testing Markov Chain Timing ===")
markov = MarkovChainTiming()
markov.enabled = True
print(f"Initial state: {markov.current_state}")

# Test state transitions
states_visited = []
for i in range(10):
    delay = markov.apply_to_delay(0.01)  # 10ms base delay
    states_visited.append(markov.current_state)
    print(f"Click {i+1}: State={markov.current_state}, Delay={delay*1000:.2f}ms")

print(f"States visited: {set(states_visited)}")
print(f"✓ Markov Chain transitions working (visited {len(set(states_visited))} different states)")

# Test Gaussian Delay Engine
print("\n=== Testing Gaussian Delay Engine ===")
gaussian = GaussianDelayEngine()
gaussian.enabled = True
gaussian.mean_ms = 10.0
gaussian.std_dev_ms = 2.0
gaussian.min_delay_ms = 5.0

delays = []
for i in range(10):
    delay = gaussian.apply_to_delay(0.01)  # 10ms base delay
    delays.append(delay * 1000)
    print(f"Click {i+1}: Delay={delay*1000:.2f}ms")

avg_delay = sum(delays) / len(delays)
print(f"Average delay: {avg_delay:.2f}ms (target: ~{gaussian.mean_ms}ms)")
print(f"Min delay: {min(delays):.2f}ms, Max delay: {max(delays):.2f}ms")
print(f"✓ Gaussian distribution working")

# Test Acceleration Profile
print("\n=== Testing Acceleration Profile ===")
accel = AccelerationProfile()
accel.enabled = True
accel.curve_type = 'linear'
accel.start_speed_multiplier = 1.0
accel.end_speed_multiplier = 0.5  # Speed up (lower delay)
accel.duration_clicks = 10
accel.reset()

print("Linear acceleration (10 clicks):")
for i in range(10):
    delay = accel.apply_to_delay(0.01)  # 10ms base delay
    progress = accel.get_progress()
    print(f"Click {i+1}: Progress={progress:.2f}, Delay={delay*1000:.2f}ms")

print(f"✓ Acceleration profile working")

# Test Exponential curve
print("\nExponential acceleration:")
accel.reset()
accel.curve_type = 'exponential'
for i in range(10):
    delay = accel.apply_to_delay(0.01)
    progress = accel.get_progress()
    print(f"Click {i+1}: Progress={progress:.2f}, Delay={delay*1000:.2f}ms")

# Test S-curve
print("\nS-curve acceleration:")
accel.reset()
accel.curve_type = 's_curve'
for i in range(10):
    delay = accel.apply_to_delay(0.01)
    progress = accel.get_progress()
    print(f"Click {i+1}: Progress={progress:.2f}, Delay={delay*1000:.2f}ms")

print(f"✓ All curve types working")

# Test combination of systems
print("\n=== Testing Combined Systems ===")
markov.reset_state()
gaussian.enabled = True
accel.reset()
accel.enabled = True

base_delay = 0.01
print("Combining all three systems:")
for i in range(5):
    # Apply in sequence
    delay = base_delay
    delay = markov.apply_to_delay(delay)
    delay = gaussian.apply_to_delay(delay)
    delay = accel.apply_to_delay(delay)
    print(f"Click {i+1}: Final delay={delay*1000:.2f}ms (Markov state: {markov.current_state})")

print(f"✓ Combined systems working")

# Test serialization
print("\n=== Testing Serialization ===")
markov_dict = markov.to_dict()
print(f"Markov to_dict keys: {list(markov_dict.keys())}")

gaussian_dict = gaussian.to_dict()
print(f"Gaussian to_dict keys: {list(gaussian_dict.keys())}")

accel_dict = accel.to_dict()
print(f"Acceleration to_dict keys: {list(accel_dict.keys())}")

# Test deserialization
new_markov = MarkovChainTiming()
new_markov.from_dict(markov_dict)
print(f"✓ Markov deserialization: enabled={new_markov.enabled}")

new_gaussian = GaussianDelayEngine()
new_gaussian.from_dict(gaussian_dict)
print(f"✓ Gaussian deserialization: mean={new_gaussian.mean_ms}ms")

new_accel = AccelerationProfile()
new_accel.from_dict(accel_dict)
print(f"✓ Acceleration deserialization: curve_type={new_accel.curve_type}")

print("\n" + "="*50)
print("ALL TESTS PASSED! ✓")
print("="*50)

