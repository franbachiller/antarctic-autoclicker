import ctypes
import time
import threading
import random
import math
from ctypes import wintypes
import customtkinter as ctk
from tkinter import messagebox
import json
import os
import hashlib
import base64
import sys
from PIL import Image
from auth_client import AuthClient
from security import SecurityGuard
from latency_compensator import LatencyCompensator
from updater import Updater, get_version_from_file

# GUI Configuration - Frutiger Aero Style
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Dark Theme - Pure Black with Fire Red Accent
COLORS = {
    'bg_primary': '#000000',      # Pure black
    'bg_secondary': '#0A0A0A',    # Almost black
    'bg_card': '#121212',         # Dark card background
    'accent_blue': '#FF3030',     # Fire red (primary accent)
    'accent_cyan': '#FF3030',     # Fire red (same as accent)
    'accent_green': '#FF3030',    # Fire red (for consistency)
    'text_primary': '#FFFFFF',    # Pure white text
    'text_secondary': '#808080',  # Gray text
    'text_dim': '#505050',        # Dim gray
    'border': '#1A1A1A',          # Subtle dark border
    'glow': '#FF3030',            # Fire red glow
    'accent_red': '#FF0000',      # Bright red for delete
}

# Windows API handles
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Resource path helper
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        # If not compiled, use the parent directory of src folder
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

# Get AppData folder for config files
def get_app_data_dir():
    """Get or create the application data directory in AppData/Local"""
    try:
        # Get user's AppData/Local folder
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(appdata, '.antarctic')

        # Create directory if it doesn't exist
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)

            # Set hidden attribute on Windows
            if sys.platform == 'win32':
                try:
                    import ctypes
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    ctypes.windll.kernel32.SetFileAttributesW(app_dir, FILE_ATTRIBUTE_HIDDEN)
                except:
                    pass

        return app_dir
    except:
        # Fallback to current directory if something fails
        return '.'

class ToolTip:
    """Simple tooltip for CTk widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            tw,
            text=self.text,
            fg_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
            corner_radius=6,
            font=("Segoe UI", 9),
            padx=8,
            pady=4
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# Windows Messages Constants
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C

# Mouse/Key Constants
MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002
MK_MBUTTON = 0x0010
MK_SHIFT = 0x0004
MK_CONTROL = 0x0008
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

# Virtual Key Codes
VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F5 = 0x74
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_LBUTTON = 0x01

# Thread Priority Constants
THREAD_PRIORITY_BELOW_NORMAL = -1
THREAD_PRIORITY_NORMAL = 0
THREAD_PRIORITY_ABOVE_NORMAL = 1
THREAD_PRIORITY_TIME_CRITICAL = 15

# Mouse Input Constants
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [('mi', MOUSEINPUT)]
    _anonymous_ = ('_input',)
    _fields_ = [
        ('type', wintypes.DWORD),
        ('_input', _INPUT)
    ]

class ClickConfig:
    def __init__(self):
        self.clicks = 24
        self.interval = 10
        self.duration = 0.30
        self.click_type = 'single'
        self.mouse_button = 'left'
        self.humanize_enabled = False
        self.time_jitter_ms = 2.0
        self.humanize_advanced = False
        self.click_mode = 'normal'
        self.hold_duration_ms = 100
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.input_method = 'postmessage'
        self.timing_profile = 'precise'
        self.ultra_mode = False
        self.auto_burst_enabled = False
        self.auto_burst_delay = 0.0

        # Advanced timing system (for burst variations)
        self.advanced_timing_enabled: bool = False
        self.advanced_profile: AdvancedTimingProfile | None = None
        self.event_sequence: ClickEventSequence | None = None
        self.delay_pattern: DelayPatternEngine | None = None

        # New advanced timing systems
        self.markov_chain_enabled = False
        self.gaussian_delay_enabled = False
        self.acceleration_enabled = False

        # Markov Chain parameters
        self.markov_fast_multiplier = 0.5
        self.markov_medium_multiplier = 1.0
        self.markov_slow_multiplier = 1.8

        # Gaussian delay parameters
        self.gaussian_mean_ms = 10.0
        self.gaussian_std_dev_ms = 3.0
        self.gaussian_min_delay_ms = 1.0
        self.gaussian_use_absolute = False

        # Acceleration profile parameters
        self.accel_curve_type = 'linear'  # 'linear', 'exponential', 's_curve', 'custom'
        self.accel_start_multiplier = 1.0
        self.accel_end_multiplier = 0.5
        self.accel_duration_clicks = 50
        self.accel_duration_type = 'clicks'  # 'clicks' or 'time'

        # Latency compensation parameters
        self.latency_compensation_enabled = False
        self.latency_devtools_port = 9222
        self.latency_multiplier = 1.0

    def to_dict(self):
        data = {}
        for k, v in self.__dict__.items():
            # Skip None values for advanced profiles
            if v is None:
                continue
            # Handle special objects
            if hasattr(v, 'to_dict'):
                data[k] = v.to_dict()
            else:
                data[k] = v
        return data

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                # Type conversion for boolean fields
                boolean_fields = [
                    'advanced_timing_enabled', 'humanize_enabled', 'humanize_advanced',
                    'ultra_mode', 'auto_burst_enabled', 'markov_chain_enabled',
                    'gaussian_delay_enabled', 'acceleration_enabled', 'gaussian_use_absolute'
                ]
                if key in boolean_fields:
                    value = bool(value)
                setattr(self, key, value)

class AdvancedTimingProfile:
    def __init__(self, name="Custom Profile"):
        self.name = name
        self.base_delay = 0.001  # Base timing in seconds
        self.jitter_range = (0.0001, 0.0005)  # Micro-jitter for race conditions
        self.burst_pattern = [1, 1, 1, 2, 1, 1, 3]  # Click sequences
        self.delay_pattern = [0.001, 0.002, 0.001, 0.003, 0.001, 0.002, 0.004]
        self.priority_boost = True  # Thread priority management
        self.event_optimization = True  # Windows message optimization
        self.cpu_affinity = False  # Lock to specific CPU core
        self.memory_locking = False  # Prevent page faults
        self.interrupt_protection = False  # Handle interrupts

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class ClickEventSequence:
    def __init__(self):
        self.events = [
            {'type': 'down', 'delay': 0.0001, 'flags': MK_LBUTTON},
            {'type': 'up', 'delay': 0.0002, 'flags': 0},
            {'type': 'pause', 'delay': 0.001, 'flags': 0},
        ]
        self.loop_count = 1
        self.conditional_delays = True

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class DelayPatternEngine:
    def __init__(self):
        self.patterns = {
            'linear': lambda x: x * 0.001,
            'exponential': lambda x: 0.001 * (2 ** x),
            'fibonacci': self._fibonacci_delay,
            'prime': self._prime_delay,
            'custom': [0.001, 0.002, 0.003, 0.001, 0.004]
        }
        self.current_pattern = 'linear'
        self.pattern_length = 10
        self.custom_pattern = [0.001, 0.002, 0.003, 0.001, 0.004]

    def _fibonacci_delay(self, x):
        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)
        return fib(x) * 0.0001

    def _prime_delay(self, x):
        def is_prime(n):
            if n <= 1:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True

        count = 0
        num = 2
        while count < x + 1:
            if is_prime(num):
                count += 1
                if count == x + 1:
                    return num * 0.001
            num += 1
        return 0.001

    def get_delay(self, index):
        if self.current_pattern == 'custom':
            return self.custom_pattern[index % len(self.custom_pattern)]
        elif self.current_pattern in self.patterns:
            return self.patterns[self.current_pattern](index)
        else:
            return 0.001

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class MarkovChainTiming:
    """Markov Chain-based timing system with state transitions"""
    def __init__(self):
        # Define speed states
        self.states = ['fast', 'medium', 'slow']
        self.current_state = 'medium'

        # Transition probability matrix
        # Format: {current_state: {next_state: probability}}
        self.transition_matrix = {
            'fast': {'fast': 0.3, 'medium': 0.5, 'slow': 0.2},
            'medium': {'fast': 0.3, 'medium': 0.4, 'slow': 0.3},
            'slow': {'fast': 0.2, 'medium': 0.5, 'slow': 0.3}
        }

        # Delay multipliers for each state (relative to base delay)
        self.state_multipliers = {
            'fast': 0.5,      # 50% of base delay
            'medium': 1.0,    # 100% of base delay
            'slow': 1.8       # 180% of base delay
        }

        # Configurable parameters
        self.enabled = False
        self.use_custom_multipliers = False
        self.custom_fast_multiplier = 0.5
        self.custom_medium_multiplier = 1.0
        self.custom_slow_multiplier = 1.8

    def get_next_state(self):
        """Transition to next state based on probability matrix"""
        if self.current_state not in self.transition_matrix:
            self.current_state = 'medium'

        transitions = self.transition_matrix[self.current_state]
        states = list(transitions.keys())
        probabilities = list(transitions.values())

        # Normalize probabilities to ensure they sum to 1.0
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            probabilities = [1.0 / len(states)] * len(states)

        # Choose next state based on probabilities
        self.current_state = random.choices(states, weights=probabilities, k=1)[0]
        return self.current_state

    def get_delay_multiplier(self):
        """Get the delay multiplier for current state"""
        if self.use_custom_multipliers:
            multipliers = {
                'fast': self.custom_fast_multiplier,
                'medium': self.custom_medium_multiplier,
                'slow': self.custom_slow_multiplier
            }
            return multipliers.get(self.current_state, 1.0)
        else:
            return self.state_multipliers.get(self.current_state, 1.0)

    def apply_to_delay(self, base_delay):
        """Apply Markov chain timing to base delay"""
        if not self.enabled:
            return base_delay

        # Transition to next state
        self.get_next_state()

        # Apply state multiplier
        multiplier = self.get_delay_multiplier()
        return base_delay * multiplier

    def set_transition_probability(self, from_state, to_state, probability):
        """Set custom transition probability"""
        if from_state in self.transition_matrix:
            if to_state in self.transition_matrix[from_state]:
                self.transition_matrix[from_state][to_state] = probability

    def reset_state(self):
        """Reset to medium state"""
        self.current_state = 'medium'

    def to_dict(self):
        return {
            'enabled': self.enabled,
            'current_state': self.current_state,
            'transition_matrix': self.transition_matrix,
            'state_multipliers': self.state_multipliers,
            'use_custom_multipliers': self.use_custom_multipliers,
            'custom_fast_multiplier': self.custom_fast_multiplier,
            'custom_medium_multiplier': self.custom_medium_multiplier,
            'custom_slow_multiplier': self.custom_slow_multiplier
        }

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class GaussianDelayEngine:
    """Gaussian (Normal) distribution-based delay system"""
    def __init__(self):
        self.enabled = False
        self.mean_ms = 10.0          # Mean delay in milliseconds
        self.std_dev_ms = 3.0        # Standard deviation in milliseconds
        self.min_delay_ms = 1.0      # Minimum allowed delay
        self.max_delay_ms = 100.0    # Maximum allowed delay (cap outliers)
        self.use_absolute = False    # If True, use absolute values; if False, use as multiplier

    def get_gaussian_delay(self, base_delay=None):
        """Generate delay using Gaussian distribution"""
        if not self.enabled:
            return base_delay if base_delay is not None else 0.01

        if self.use_absolute:
            # Use absolute Gaussian values (ignore base_delay)
            delay_ms = random.gauss(self.mean_ms, self.std_dev_ms)
        else:
            # Use Gaussian as multiplier on base_delay
            if base_delay is None:
                base_delay = 0.01  # Default 10ms

            # Generate multiplier with mean=1.0 and configurable std dev
            multiplier = random.gauss(1.0, self.std_dev_ms / self.mean_ms)
            delay_ms = (base_delay * 1000.0) * multiplier

        # Clamp to min/max bounds
        delay_ms = max(self.min_delay_ms, min(self.max_delay_ms, delay_ms))

        # Convert to seconds
        return delay_ms / 1000.0

    def apply_to_delay(self, base_delay):
        """Apply Gaussian distribution to base delay"""
        if not self.enabled:
            return base_delay

        return self.get_gaussian_delay(base_delay)

    def to_dict(self):
        return {
            'enabled': self.enabled,
            'mean_ms': self.mean_ms,
            'std_dev_ms': self.std_dev_ms,
            'min_delay_ms': self.min_delay_ms,
            'max_delay_ms': self.max_delay_ms,
            'use_absolute': self.use_absolute
        }

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class AccelerationProfile:
    """Acceleration/Deceleration profile system for smooth speed transitions"""
    def __init__(self):
        self.enabled = False
        self.curve_type = 'linear'  # 'linear', 'exponential', 's_curve', 'custom'

        # Speed parameters (as multipliers of base delay)
        self.start_speed_multiplier = 1.0   # Starting speed (1.0 = normal)
        self.end_speed_multiplier = 0.5     # Ending speed (0.5 = 2x faster)

        # Duration parameters
        self.duration_type = 'clicks'  # 'clicks' or 'time'
        self.duration_clicks = 50      # Number of clicks for transition
        self.duration_seconds = 5.0    # Time in seconds for transition

        # Current state
        self.current_click = 0
        self.start_time = None
        self.is_accelerating = True  # True = speed up, False = slow down

        # Custom curve points (for custom curve type)
        # List of (progress, multiplier) tuples where progress is 0.0 to 1.0
        self.custom_curve_points = [
            (0.0, 1.0),
            (0.5, 0.75),
            (1.0, 0.5)
        ]

        # Exponential curve parameters
        self.exponential_factor = 2.0  # Higher = more aggressive curve

        # S-curve (sigmoid) parameters
        self.sigmoid_steepness = 10.0  # Higher = steeper transition

    def reset(self):
        """Reset acceleration state"""
        self.current_click = 0
        self.start_time = time.time()

    def get_progress(self):
        """Calculate current progress (0.0 to 1.0)"""
        if self.duration_type == 'clicks':
            if self.duration_clicks <= 0:
                return 1.0
            progress = self.current_click / self.duration_clicks
        else:  # time-based
            if self.start_time is None:
                self.start_time = time.time()
            elapsed = time.time() - self.start_time
            if self.duration_seconds <= 0:
                return 1.0
            progress = elapsed / self.duration_seconds

        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, progress))

    def calculate_multiplier(self, progress):
        """Calculate speed multiplier based on curve type and progress"""
        start = self.start_speed_multiplier
        end = self.end_speed_multiplier

        if self.curve_type == 'linear':
            # Linear interpolation
            multiplier = start + (end - start) * progress

        elif self.curve_type == 'exponential':
            # Exponential curve
            # Use exponential function for smooth acceleration
            exp_progress = (math.exp(self.exponential_factor * progress) - 1) / (math.exp(self.exponential_factor) - 1)
            multiplier = start + (end - start) * exp_progress

        elif self.curve_type == 's_curve':
            # S-curve (sigmoid function)
            # Maps 0-1 input to smooth S-shaped curve
            x = (progress - 0.5) * self.sigmoid_steepness
            sigmoid = 1 / (1 + math.exp(-x))
            multiplier = start + (end - start) * sigmoid

        elif self.curve_type == 'custom':
            # Custom curve using interpolation between points
            multiplier = self._interpolate_custom_curve(progress)

        else:
            multiplier = start

        return multiplier

    def _interpolate_custom_curve(self, progress):
        """Interpolate multiplier from custom curve points"""
        if not self.custom_curve_points:
            return self.start_speed_multiplier

        # Sort points by progress
        points = sorted(self.custom_curve_points, key=lambda p: p[0])

        # Find surrounding points
        for i in range(len(points) - 1):
            p1, m1 = points[i]
            p2, m2 = points[i + 1]

            if p1 <= progress <= p2:
                # Linear interpolation between points
                if p2 - p1 == 0:
                    return m1
                t = (progress - p1) / (p2 - p1)
                return m1 + (m2 - m1) * t

        # If progress is beyond last point, return last multiplier
        return points[-1][1]

    def apply_to_delay(self, base_delay):
        """Apply acceleration profile to base delay"""
        if not self.enabled:
            return base_delay

        # Get current progress
        progress = self.get_progress()

        # Calculate multiplier
        multiplier = self.calculate_multiplier(progress)

        # Increment click counter
        self.current_click += 1

        # Apply multiplier to delay
        return base_delay * multiplier

    def to_dict(self):
        return {
            'enabled': self.enabled,
            'curve_type': self.curve_type,
            'start_speed_multiplier': self.start_speed_multiplier,
            'end_speed_multiplier': self.end_speed_multiplier,
            'duration_type': self.duration_type,
            'duration_clicks': self.duration_clicks,
            'duration_seconds': self.duration_seconds,
            'current_click': self.current_click,
            'is_accelerating': self.is_accelerating,
            'custom_curve_points': self.custom_curve_points,
            'exponential_factor': self.exponential_factor,
            'sigmoid_steepness': self.sigmoid_steepness
        }

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        # Reset start_time as it shouldn't be serialized
        self.start_time = None

class ThreadingOptimizer:
    def __init__(self):
        self.real_time_priority = True
        self.cpu_affinity = True
        self.memory_locking = False
        self.interrupt_handling = True

    def optimize_for_race_conditions(self, profile):
        """Apply threading optimizations for race condition scenarios"""
        if profile.priority_boost:
            # Set thread to high priority for timing-critical operations
            current_thread = kernel32.GetCurrentThread()
            if profile.name == 'Race Condition Master':
                kernel32.SetThreadPriority(current_thread, THREAD_PRIORITY_TIME_CRITICAL)
            else:
                kernel32.SetThreadPriority(current_thread, THREAD_PRIORITY_ABOVE_NORMAL)

        # Note: CPU affinity and memory locking would require additional Windows API calls
        # These are advanced features that may need admin privileges

    def restore_normal_priority(self):
        """Restore normal thread priority"""
        current_thread = kernel32.GetCurrentThread()
        kernel32.SetThreadPriority(current_thread, THREAD_PRIORITY_NORMAL)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class ProfileManager:
    def __init__(self, max_profiles=5):
        self.max_profiles = max_profiles
        self.profiles = {}
        self.current_profile = None
        # Store config file in AppData folder
        app_dir = get_app_data_dir()
        self.config_file = os.path.join(app_dir, 'antarctic_profiles.json')
        self.load_profiles()

    def save_profiles(self):
        try:
            data = {'profiles': self.profiles, 'current_profile': self.current_profile}
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def load_profiles(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.profiles = data.get('profiles', {})
                    self.current_profile = data.get('current_profile', None)
        except Exception as e:
            print(f"Error loading profiles: {e}")
            self.profiles = {}
            self.current_profile = None

    def save_profile(self, name, config):
        if len(self.profiles) >= self.max_profiles and name not in self.profiles:
            return False, f"Maximum {self.max_profiles} profiles reached"
        self.profiles[name] = config.to_dict()
        self.current_profile = name
        self.save_profiles()
        return True, f"Profile '{name}' saved"

    def load_profile(self, name):
        if name in self.profiles:
            self.current_profile = name
            self.save_profiles()
            return True, self.profiles[name]
        return False, None

    def delete_profile(self, name):
        if name in self.profiles:
            del self.profiles[name]
            if self.current_profile == name:
                self.current_profile = None
            self.save_profiles()
            return True, f"Profile '{name}' deleted"
        return False, "Profile not found"

    def get_profile_names(self):
        return list(self.profiles.keys())

    def get_current_profile(self):
        return self.current_profile

class KeyManager:
    def __init__(self, server_url="https://antarctic-autoclicker.vercel.app"):
        self.auth_client = AuthClient(server_url=server_url)

    def is_activated(self):
        return self.auth_client.is_activated()

    def activate(self, key):
        success, message, data = self.auth_client.activate(key)
        return success, message

    def deactivate(self):
        return self.auth_client.deactivate()

    def validate(self, skip_network=False):
        return self.auth_client.validate(skip_network=skip_network)

    def get_license_info(self):
        """Get license information for display"""
        return self.auth_client.get_license_info()

    def get_time_remaining(self):
        """Get time remaining on license"""
        return self.auth_client.get_time_remaining()

class AutoClicker:
    def __init__(self, gui_callback=None):
        self.target_x = 0
        self.target_y = 0
        self.active_bursts = 0
        self.burst_lock = threading.Lock()
        self.running = True
        self.gui_callback = gui_callback
        self.config = ClickConfig()
        self.target_hwnd = None
        self.is_connected = False
        self.target_window_title = "BoomBang"
        self.total_clicks_sent = 0
        self.current_burst_clicks = 0
        self.last_burst_clicks = 0
        self.circular_jitter_angle = 0

        # Timing monitoring
        self.last_delay_ms = 0.0
        self.last_markov_state = "medium"
        self.last_gaussian_value = 0.0
        self.last_accel_progress = 0.0

        # Advanced timing system components
        self.threading_optimizer = ThreadingOptimizer()
        self.delay_engine = DelayPatternEngine()
        self.event_sequence = ClickEventSequence()

        # New advanced timing engines
        self.markov_chain = MarkovChainTiming()
        self.gaussian_delay = GaussianDelayEngine()
        self.acceleration_profile = AccelerationProfile()

        # Latency compensation system
        self.latency_compensator = LatencyCompensator(callback=self._latency_callback)

        # Predefined advanced profiles
        self.advanced_profiles = self._create_advanced_profiles()

    def _latency_callback(self, event_type, data):
        """Callback para eventos del compensador de latencia"""
        if self.gui_callback:
            self.gui_callback('latency_event', {'type': event_type, 'data': data})

    def _create_advanced_profiles(self):
        """Create predefined advanced timing profiles"""
        profiles = {}

        # Race Condition Master Profile
        race_master = AdvancedTimingProfile("Race Condition Master")
        race_master.base_delay = 0.0001  # 100 microseconds
        race_master.jitter_range = (0.00001, 0.00005)  # 10-50 microseconds
        race_master.burst_pattern = [1] * 100  # 100 rapid clicks
        race_master.delay_pattern = [0.0001] * 100  # Consistent timing
        race_master.priority_boost = True
        race_master.event_optimization = True
        race_master.cpu_affinity = True
        race_master.interrupt_protection = True
        profiles['race_master'] = race_master

        # Timing Critical Profile
        timing_critical = AdvancedTimingProfile("Timing Critical")
        timing_critical.base_delay = 0.0005  # 500 microseconds
        timing_critical.jitter_range = (0.0001, 0.0002)  # Controlled variation
        timing_critical.burst_pattern = [1, 1, 2, 1, 1, 3, 1, 1, 1, 4]  # Complex sequence
        timing_critical.delay_pattern = [0.0005, 0.0006, 0.0007, 0.0005, 0.0006, 0.0008, 0.0005, 0.0006, 0.0007, 0.0009]
        timing_critical.priority_boost = True
        timing_critical.event_optimization = True
        profiles['timing_critical'] = timing_critical

        # Precision Burst Profile
        precision_burst = AdvancedTimingProfile("Precision Burst")
        precision_burst.base_delay = 0.001  # 1 millisecond
        precision_burst.jitter_range = (0.0001, 0.0003)  # Minimal variation
        precision_burst.burst_pattern = [5, 3, 8, 2, 10]  # Variable burst sizes
        precision_burst.delay_pattern = [0.001, 0.002, 0.001, 0.003, 0.001]
        precision_burst.priority_boost = True
        precision_burst.event_optimization = True
        profiles['precision_burst'] = precision_burst

        return profiles

    def get_window_from_point(self, x, y):
        point = wintypes.POINT(x, y)
        return user32.WindowFromPoint(point)

    def screen_to_client(self, hwnd, x, y):
        point = wintypes.POINT(x, y)
        user32.ScreenToClient(hwnd, ctypes.byref(point))
        return point.x, point.y

    def apply_position_jitter(self, x, y):
        return x, y

    def get_timing_delay(self):
        # Ultra mode: no delay
        if self.config.ultra_mode:
            self.last_delay_ms = 0.0
            return 0

        # Start with the interval slider value (in milliseconds, convert to seconds)
        base_delay = self.config.interval / 1000.0

        # Apply latency compensation FIRST (if enabled)
        original_delay = base_delay
        if self.config.latency_compensation_enabled and self.latency_compensator.compensation_enabled:
            base_delay_ms = base_delay * 1000.0
            compensated_ms = self.latency_compensator.get_compensated_delay(base_delay_ms)
            base_delay = compensated_ms / 1000.0

            # Log compensation (only occasionally to avoid spam)
            if random.random() < 0.01:  # 1% of the time
                print(f"[LATENCY] Original: {original_delay*1000:.2f}ms → Compensated: {base_delay*1000:.2f}ms (RTT: {self.latency_compensator.current_rtt_ms:.1f}ms)")

        # Apply humanization if enabled
        if self.config.humanize_enabled:
            if self.config.timing_profile == 'human_slow':
                # Add random delay on top of base
                base_delay += random.uniform(0.010, 0.025)
            elif self.config.timing_profile == 'human_fast':
                # Add smaller random delay
                base_delay += random.uniform(0.002, 0.008)
            elif self.config.timing_profile == 'random':
                # Random multiplier
                base_delay *= random.uniform(0.5, 2.0)

            # Apply time jitter if configured
            if self.config.time_jitter_ms > 0:
                jitter = random.uniform(-self.config.time_jitter_ms, self.config.time_jitter_ms) / 1000.0
                base_delay += jitter

        # Apply advanced timing modifications if enabled
        if self.config.advanced_timing_enabled and self.config.advanced_profile:
            profile = self.config.advanced_profile

            # Apply micro-jitter for race conditions (additive)
            if profile.jitter_range:
                jitter = random.uniform(profile.jitter_range[0], profile.jitter_range[1])
                base_delay += jitter

        # === NEW ADVANCED TIMING SYSTEMS ===

        # 1. Apply Markov Chain Timing (state-based transitions)
        if self.config.markov_chain_enabled:
            # Sync config parameters to engine
            self.markov_chain.enabled = True
            self.markov_chain.use_custom_multipliers = True
            self.markov_chain.custom_fast_multiplier = self.config.markov_fast_multiplier
            self.markov_chain.custom_medium_multiplier = self.config.markov_medium_multiplier
            self.markov_chain.custom_slow_multiplier = self.config.markov_slow_multiplier

            base_delay = self.markov_chain.apply_to_delay(base_delay)
            self.last_markov_state = self.markov_chain.current_state
        else:
            self.markov_chain.enabled = False
            self.last_markov_state = "off"

        # 2. Apply Gaussian Distribution Delays
        if self.config.gaussian_delay_enabled:
            # Sync config parameters to engine
            self.gaussian_delay.enabled = True
            self.gaussian_delay.mean_ms = self.config.gaussian_mean_ms
            self.gaussian_delay.std_dev_ms = self.config.gaussian_std_dev_ms
            self.gaussian_delay.min_delay_ms = self.config.gaussian_min_delay_ms
            self.gaussian_delay.use_absolute = self.config.gaussian_use_absolute

            before_gaussian = base_delay
            base_delay = self.gaussian_delay.apply_to_delay(base_delay)
            self.last_gaussian_value = base_delay - before_gaussian
        else:
            self.gaussian_delay.enabled = False
            self.last_gaussian_value = 0.0

        # 3. Apply Acceleration/Deceleration Profile
        if self.config.acceleration_enabled:
            # Sync config parameters to engine
            self.acceleration_profile.enabled = True
            self.acceleration_profile.curve_type = self.config.accel_curve_type
            self.acceleration_profile.start_speed_multiplier = self.config.accel_start_multiplier
            self.acceleration_profile.end_speed_multiplier = self.config.accel_end_multiplier
            self.acceleration_profile.duration_clicks = self.config.accel_duration_clicks
            self.acceleration_profile.duration_type = self.config.accel_duration_type

            base_delay = self.acceleration_profile.apply_to_delay(base_delay)
            self.last_accel_progress = self.acceleration_profile.get_progress()
        else:
            self.acceleration_profile.enabled = False
            self.last_accel_progress = 0.0

        # Ensure minimum delay and store for monitoring
        final_delay = max(0.001, base_delay)
        self.last_delay_ms = final_delay * 1000.0

        return final_delay

    def get_button_messages(self, button):
        buttons = {
            'left': (WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON),
            'right': (WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON),
            'middle': (WM_MBUTTONDOWN, WM_MBUTTONUP, MK_MBUTTON),
            'x1': (WM_XBUTTONDOWN, WM_XBUTTONUP, XBUTTON1),
            'x2': (WM_XBUTTONDOWN, WM_XBUTTONUP, XBUTTON2)
        }
        return buttons.get(button, buttons['left'])

    def get_modifier_flags(self):
        return 0

    def send_single_click_postmessage(self, hwnd, x, y):
        user32.SendMessageW(hwnd, self._msg_down, self._wparam, self._lparam)
        if not self.config.ultra_mode:
            if self.config.click_mode == 'hold':
                time.sleep(self.config.hold_duration_ms / 1000.0)
            else:
                time.sleep(self._timing_delay)
        user32.SendMessageW(hwnd, self._msg_up, 0, self._lparam_up)
        self.total_clicks_sent += 1
        self.current_burst_clicks += 1

    def _precalculate_click_params(self, x, y):
        msg_down, msg_up, button_flag = self.get_button_messages(self.config.mouse_button)
        modifier_flags = self.get_modifier_flags()
        jittered_x, jittered_y = self.apply_position_jitter(x, y)
        lparam = (jittered_y << 16) | jittered_x
        wparam = button_flag | modifier_flags
        if self.config.mouse_button in ['x1', 'x2']:
            wparam = (button_flag << 16) | modifier_flags
        if self.config.click_mode == 'drag':
            drag_x = jittered_x + self.config.drag_offset_x
            drag_y = jittered_y + self.config.drag_offset_y
            lparam_up = (drag_y << 16) | drag_x
        else:
            lparam_up = lparam
        self._msg_down = msg_down
        self._msg_up = msg_up
        self._wparam = wparam
        self._lparam = lparam
        self._lparam_up = lparam_up
        self._timing_delay = self.get_timing_delay()

    def send_single_click_sendinput(self, x, y):
        if self.target_hwnd:
            client_x, client_y = self.screen_to_client(self.target_hwnd, x, y)
            self.send_single_click_postmessage(self.target_hwnd, client_x, client_y)

    def send_single_click(self, hwnd, x, y):
        if self.config.input_method == 'sendinput':
            screen_x, screen_y = x, y
            self.send_single_click_sendinput(screen_x, screen_y)
        else:
            self.send_single_click_postmessage(hwnd, x, y)

    def send_click_sequence(self, hwnd, x, y):
        clicks = 1
        if self.config.click_type == 'double':
            clicks = 2
        elif self.config.click_type == 'triple':
            clicks = 3
        for i in range(clicks):
            self.send_single_click(hwnd, x, y)
            if i < clicks - 1:
                time.sleep(0.05)

    def find_target_window(self):
        return user32.FindWindowW(None, self.target_window_title)

    def check_window_valid(self, hwnd):
        if not hwnd or hwnd == 0:
            return False
        return user32.IsWindow(hwnd)

    def monitor_connection(self):
        while self.running:
            hwnd = self.find_target_window()
            if hwnd and self.check_window_valid(hwnd):
                if not self.is_connected:
                    self.target_hwnd = hwnd
                    self.is_connected = True
                    if self.gui_callback:
                        self.gui_callback('connection_changed')
            else:
                if self.is_connected:
                    self.target_hwnd = None
                    self.is_connected = False
                    if self.gui_callback:
                        self.gui_callback('connection_changed')
            time.sleep(1)

    def is_key_pressed(self, vk_code):
        return user32.GetAsyncKeyState(vk_code) & 0x8000 != 0

    def execute_burst(self, delay=None):
        if not self.is_connected or not self.target_hwnd or not self.target_x or not self.target_y:
            return

        if delay is not None and delay > 0:
            time.sleep(delay)

        with self.burst_lock:
            self.active_bursts += 1
            if self.active_bursts == 1 and self.gui_callback:
                self.gui_callback('burst_started')

        # Reset acceleration profile for new burst
        if self.config.acceleration_enabled:
            self.acceleration_profile.reset()

        # Apply advanced threading optimizations
        if self.config.advanced_timing_enabled and self.config.advanced_profile:
            self.threading_optimizer.optimize_for_race_conditions(self.config.advanced_profile)
        else:
            current_thread = kernel32.GetCurrentThread()
            priority = THREAD_PRIORITY_BELOW_NORMAL if self.config.ultra_mode else THREAD_PRIORITY_NORMAL
            kernel32.SetThreadPriority(current_thread, priority)

        try:
            end_time = time.time() + self.config.duration
            click_count = 0
            client_x, client_y = self.screen_to_client(self.target_hwnd, self.target_x, self.target_y)
            self._precalculate_click_params(client_x, client_y)
            ultra_mode = self.config.ultra_mode
            humanize = self.config.humanize_advanced
            stats_update_interval = 50 if ultra_mode else 10
            hwnd = self.target_hwnd

            if not self.check_window_valid(hwnd):
                return

            # Execute burst with timing system
            config_clicks = self.config.clicks
            
            while time.time() < end_time and self.running:
                # Determine clicks per batch
                if humanize:
                    clicks_to_send = random.randint(5, 15)
                elif self.config.advanced_timing_enabled and self.config.advanced_profile:
                    # Use burst pattern from advanced profile
                    profile = self.config.advanced_profile
                    pattern_index = click_count % len(profile.burst_pattern)
                    clicks_to_send = profile.burst_pattern[pattern_index]
                else:
                    clicks_to_send = config_clicks
                
                # Determine click multiplier based on click_type
                click_multiplier = 1
                if self.config.click_type == 'double':
                    click_multiplier = 2
                elif self.config.click_type == 'triple':
                    click_multiplier = 3

                # Send the batch of clicks (multiplied by click_type)
                for i in range(clicks_to_send):
                    if not self.running:
                        break

                    # Send multiple clicks rapidly (for double/triple)
                    for click_num in range(click_multiplier):
                        # Send click down
                        user32.SendMessageW(hwnd, self._msg_down, self._wparam, self._lparam)
                        # Send click up
                        user32.SendMessageW(hwnd, self._msg_up, 0, self._lparam_up)

                    # Apply delay AFTER all clicks in the sequence
                    if not ultra_mode:
                        delay = self.get_timing_delay()
                        if delay > 0:
                            time.sleep(delay)

                    # Update counters (count actual clicks sent)
                    self.total_clicks_sent += click_multiplier
                    self.current_burst_clicks += click_multiplier
                    click_count += 1

                    # Update stats periodically
                    if click_count % stats_update_interval == 0 and self.gui_callback:
                        self.gui_callback('stats_update')
                
                # Small pause between batches if needed
                if time.time() < end_time and self.running and not ultra_mode:
                    time.sleep(0.001)

            if self.gui_callback:
                self.gui_callback('stats_update')
        finally:
            # Restore normal priority
            if self.config.advanced_timing_enabled and self.config.advanced_profile:
                self.threading_optimizer.restore_normal_priority()
            else:
                current_thread = kernel32.GetCurrentThread()
                kernel32.SetThreadPriority(current_thread, THREAD_PRIORITY_NORMAL)

            with self.burst_lock:
                self.active_bursts -= 1
                if self.active_bursts == 0 and self.gui_callback:
                    self.gui_callback('burst_stopped')



    def capture_coordinates(self):
        cursor_pos = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(cursor_pos))
        self.target_x = cursor_pos.x
        self.target_y = cursor_pos.y
        if self.gui_callback:
            self.gui_callback('coords_captured')

    def monitor_keys(self):
        f2_pressed = False
        f3_pressed = False
        f5_pressed = False
        lbutton_pressed = False
        while self.running:
            if self.is_key_pressed(VK_F3):
                if not f3_pressed:
                    self.capture_coordinates()
                    f3_pressed = True
            else:
                f3_pressed = False
            if self.is_key_pressed(VK_F2):
                if not f2_pressed:
                    burst_thread = threading.Thread(target=self.execute_burst, daemon=True)
                    burst_thread.start()
                    f2_pressed = True
            else:
                f2_pressed = False
            if self.is_key_pressed(VK_F5):
                if not f5_pressed:
                    self.config.auto_burst_enabled = not self.config.auto_burst_enabled
                    if self.gui_callback:
                        self.gui_callback('auto_burst_toggled')
                    f5_pressed = True
            else:
                f5_pressed = False
            if self.config.auto_burst_enabled and self.is_connected:
                if self.is_key_pressed(VK_LBUTTON):
                    if not lbutton_pressed:
                        burst_thread = threading.Thread(
                            target=self.execute_burst,
                            args=(self.config.auto_burst_delay,),
                            daemon=True
                        )
                        burst_thread.start()
                        lbutton_pressed = True
                else:
                    lbutton_pressed = False
            time.sleep(0.01)

    def execute_trigger_at(self, x, y):
        if not self.is_connected:
            return
        self.target_x = x
        self.target_y = y
        burst_thread = threading.Thread(target=self.execute_burst, daemon=True)
        burst_thread.start()

    def start(self):
        connection_thread = threading.Thread(target=self.monitor_connection, daemon=True)
        connection_thread.start()
        monitor_thread = threading.Thread(target=self.monitor_keys, daemon=True)
        monitor_thread.start()

    def stop(self):
        self.running = False
        if self.latency_compensator:
            self.latency_compensator.disconnect()

class AdvancedTimingDialog(ctk.CTkToplevel):
    """Dialog for configuring advanced timing parameters"""
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("Advanced Timing Configuration")
        self.geometry("500x600")
        self.resizable(False, False)
        self.config = config

        # Configure window
        self.configure(fg_color=COLORS['bg_primary'])

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (250)
        y = (self.winfo_screenheight() // 2) - (300)
        self.geometry(f'+{x}+{y}')

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=12,
            border_width=2,
            border_color=COLORS['accent_blue']
        )
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # === MARKOV CHAIN SECTION ===
        self.create_section_header(main_frame, "🔗 Markov Chain Timing")

        markov_frame = self.create_section_frame(main_frame)

        self.create_slider_with_label(
            markov_frame, "Fast Speed Multiplier", 0.1, 2.0,
            self.config.markov_fast_multiplier,
            lambda v: setattr(self.config, 'markov_fast_multiplier', v)
        )

        self.create_slider_with_label(
            markov_frame, "Medium Speed Multiplier", 0.1, 2.0,
            self.config.markov_medium_multiplier,
            lambda v: setattr(self.config, 'markov_medium_multiplier', v)
        )

        self.create_slider_with_label(
            markov_frame, "Slow Speed Multiplier", 0.1, 3.0,
            self.config.markov_slow_multiplier,
            lambda v: setattr(self.config, 'markov_slow_multiplier', v)
        )

        # === GAUSSIAN DELAY SECTION ===
        self.create_section_header(main_frame, "📊 Gaussian Distribution")

        gaussian_frame = self.create_section_frame(main_frame)

        self.create_slider_with_label(
            gaussian_frame, "Mean Delay (ms)", 1.0, 100.0,
            self.config.gaussian_mean_ms,
            lambda v: setattr(self.config, 'gaussian_mean_ms', v)
        )

        self.create_slider_with_label(
            gaussian_frame, "Std Deviation (ms)", 0.5, 20.0,
            self.config.gaussian_std_dev_ms,
            lambda v: setattr(self.config, 'gaussian_std_dev_ms', v)
        )

        self.create_slider_with_label(
            gaussian_frame, "Min Delay (ms)", 0.1, 10.0,
            self.config.gaussian_min_delay_ms,
            lambda v: setattr(self.config, 'gaussian_min_delay_ms', v)
        )

        # Gaussian mode toggle
        mode_frame = ctk.CTkFrame(gaussian_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=5)

        self.gaussian_mode_var = ctk.StringVar(
            value="Multiplier" if not self.config.gaussian_use_absolute else "Absolute"
        )

        ctk.CTkLabel(
            mode_frame,
            text="Mode:",
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 10))

        mode_selector = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Multiplier", "Absolute"],
            variable=self.gaussian_mode_var,
            command=self.on_gaussian_mode_change,
            font=("Segoe UI", 9),
            fg_color=COLORS['bg_primary'],
            selected_color=COLORS['accent_blue'],
            unselected_color=COLORS['bg_card']
        )
        mode_selector.pack(side="left", fill="x", expand=True)

        # === ACCELERATION SECTION ===
        self.create_section_header(main_frame, "⚡ Acceleration Profile")

        accel_frame = self.create_section_frame(main_frame)

        # Curve type selector
        curve_frame = ctk.CTkFrame(accel_frame, fg_color="transparent")
        curve_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            curve_frame,
            text="Curve Type:",
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 10))

        self.curve_type_var = ctk.StringVar(value=self.config.accel_curve_type.title())

        curve_selector = ctk.CTkSegmentedButton(
            curve_frame,
            values=["Linear", "Exponential", "S_curve"],
            variable=self.curve_type_var,
            command=self.on_curve_type_change,
            font=("Segoe UI", 8),
            fg_color=COLORS['bg_primary'],
            selected_color=COLORS['accent_green'],
            unselected_color=COLORS['bg_card']
        )
        curve_selector.pack(side="left", fill="x", expand=True)

        self.create_slider_with_label(
            accel_frame, "Start Speed Multiplier", 0.1, 3.0,
            self.config.accel_start_multiplier,
            lambda v: setattr(self.config, 'accel_start_multiplier', v)
        )

        self.create_slider_with_label(
            accel_frame, "End Speed Multiplier", 0.1, 3.0,
            self.config.accel_end_multiplier,
            lambda v: setattr(self.config, 'accel_end_multiplier', v)
        )

        self.create_slider_with_label(
            accel_frame, "Duration (clicks)", 10, 200,
            self.config.accel_duration_clicks,
            lambda v: setattr(self.config, 'accel_duration_clicks', int(v))
        )

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            height=40,
            corner_radius=10,
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan'],
            font=("Segoe UI", 12, "bold"),
            command=self.destroy
        )
        close_btn.pack(fill="x", padx=10, pady=(15, 10))

    def create_section_header(self, parent, text):
        """Create a section header"""
        header = ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['accent_cyan']
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))

    def create_section_frame(self, parent):
        """Create a frame for section content"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        frame.pack(fill="x", padx=5, pady=(0, 10))
        return frame

    def create_slider_with_label(self, parent, label_text, from_, to, default_value, command):
        """Create a slider with label and value display"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=10, pady=5)

        # Label and value
        label_frame = ctk.CTkFrame(container, fg_color="transparent")
        label_frame.pack(fill="x")

        ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=("Segoe UI", 9),
            text_color=COLORS['text_secondary']
        ).pack(side="left")

        value_label = ctk.CTkLabel(
            label_frame,
            text=f"{default_value:.2f}",
            font=("Segoe UI", 9, "bold"),
            text_color=COLORS['accent_cyan']
        )
        value_label.pack(side="right")

        # Slider
        slider = ctk.CTkSlider(
            container,
            from_=from_,
            to=to,
            number_of_steps=100,
            fg_color=COLORS['bg_primary'],
            progress_color=COLORS['accent_blue'],
            button_color=COLORS['accent_cyan'],
            button_hover_color=COLORS['glow'],
            command=lambda v: self.on_slider_change(v, value_label, command)
        )
        slider.set(default_value)
        slider.pack(fill="x", pady=(2, 0))

    def on_slider_change(self, value, label, command):
        """Handle slider value change"""
        label.configure(text=f"{value:.2f}")
        command(value)

    def on_gaussian_mode_change(self, value):
        """Handle Gaussian mode change"""
        self.config.gaussian_use_absolute = (value == "Absolute")

    def on_curve_type_change(self, value):
        """Handle curve type change"""
        self.config.accel_curve_type = value.lower()

class ActivationWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ANTARCTIC")
        self.geometry("400x340")
        self.resizable(False, False)

        # Set window icon
        try:
            icon_path = resource_path('assets/icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon loading error: {e}")
            pass

        self.key_manager = KeyManager()
        self.activation_successful = False
        self._after_ids = []  # Track scheduled callbacks

        self.setup_ui()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def setup_ui(self):
        # Background color
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Header with logo
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=0, pady=(20, 15))
        header_frame.pack_propagate(False)
        
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        title = ctk.CTkLabel(
            logo_frame,
            text="A N T A R C T I C",
            font=("Bahnschrift SemiBold", 32, "bold"),
            text_color=COLORS['accent_cyan']
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="License Activation",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim']
        )
        subtitle.pack(pady=(3, 0))
        
        # Main content container
        content_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=16,
            border_width=2,
            border_color=COLORS['accent_blue']
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))
        
        # Key entry
        entry_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        entry_container.pack(pady=(25, 10), padx=20)
        
        ctk.CTkLabel(
            entry_container,
            text="Enter License Key",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=(0, 8))
        
        self.key_entry = ctk.CTkEntry(
            entry_container,
            width=340,
            height=42,
            font=("Consolas", 12),
            placeholder_text="ANTARCTIC-XXXX-XXXX-XXXX",
            border_width=2,
            corner_radius=10,
            border_color=COLORS['border'],
            fg_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_dim']
        )
        self.key_entry.pack()
        self.key_entry.focus()
        
        # Status label
        self.status_label = ctk.CTkLabel(
            entry_container,
            text="",
            font=("Segoe UI", 10),
            text_color=COLORS['accent_red']
        )
        self.status_label.pack(pady=(8, 0))
        
        # Buttons
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 25), padx=20)
        
        activate_btn = ctk.CTkButton(
            btn_frame,
            text="ACTIVATE",
            width=155,
            height=48,
            font=("Segoe UI", 13, "bold"),
            corner_radius=10,
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan'],
            border_width=2,
            border_color=COLORS['border'],
            command=self.activate
        )
        activate_btn.pack(side="left", padx=5)
        
        exit_btn = ctk.CTkButton(
            btn_frame,
            text="EXIT",
            width=155,
            height=48,
            font=("Segoe UI", 12),
            corner_radius=10,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['border'],
            border_width=2,
            border_color=COLORS['border'],
            command=self.exit_app
        )
        exit_btn.pack(side="left", padx=5)

        self.key_entry.bind('<Return>', lambda e: self.activate())

    def activate(self):
        key = self.key_entry.get().strip()
        if not key:
            self.status_label.configure(
                text="Please enter a license key",
                text_color=COLORS['accent_red']
            )
            return
        success, message = self.key_manager.activate(key)
        if success:
            self.status_label.configure(
                text="✓ Activation successful!",
                text_color=COLORS['accent_green']
            )
            self.activation_successful = True
            after_id = self.after(1000, self.close_window)
            self._after_ids.append(after_id)
        else:
            self.status_label.configure(
                text=f"✗ {message}",
                text_color=COLORS['accent_red']
            )
            self.key_entry.delete(0, 'end')

    def close_window(self):
        self._cancel_all_callbacks()
        self.destroy()

    def exit_app(self):
        self._cancel_all_callbacks()
        self.destroy()

    def _cancel_all_callbacks(self):
        """Cancel all scheduled after callbacks"""
        for after_id in self._after_ids:
            try:
                self.after_cancel(after_id)
            except:
                pass
        self._after_ids.clear()

    def run(self):
        self.mainloop()
        return self.activation_successful


class AntarcticGUI(ctk.CTk):
    def __init__(self, key_manager):
        super().__init__()
        self.title("ANTARCTIC")
        self.geometry("400x670")  # Compact initial size (all sections closed)
        self.resizable(False, False)

        # Set window icon
        try:
            icon_path = resource_path('assets/icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon loading error: {e}")
            pass

        self.key_manager = key_manager
        self.clicker = AutoClicker(gui_callback=self.handle_callback)
        self.profile_manager = ProfileManager(max_profiles=5)
        self._after_ids = []  # Track scheduled callbacks
        self._is_closing = False  # Flag to prevent callbacks after close
        self.license_label = None  # Will be created in create_footer

        # Initialize updater
        try:
            from config_updater import GITHUB_REPO
        except:
            GITHUB_REPO = "TU_USUARIO/antarctic-autoclicker"

        self.updater = Updater(
            current_version=get_version_from_file(),
            github_repo=GITHUB_REPO
        )

        self.setup_ui()
        self.clicker.start()
        self.load_last_profile()

        # Start background license validation (every 5 minutes)
        self.start_license_validation()

        # Check for updates on startup (after 3 seconds)
        after_id = self.after(3000, self.check_for_updates)
        self._after_ids.append(after_id)

    def setup_ui(self):
        self.configure(fg_color=COLORS['bg_primary'])
        self.create_header()
        self.create_main_content()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_header(self):
        """Frutiger Aero styled header with text logo"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=70)
        header_frame.pack(fill="x", padx=0, pady=(12, 8))
        header_frame.pack_propagate(False)

        # Stylized text logo - Frutiger Aero style
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Main title - Neon blue glow effect
        title = ctk.CTkLabel(
            logo_frame,
            text="A N T A R C T I C",
            font=("Bahnschrift SemiBold", 36, "bold"),
            text_color=COLORS['accent_blue']
        )
        title.pack()

        # Subtle tagline
        tagline = ctk.CTkLabel(
            logo_frame,
            text="by bachi",
            font=("Arial", 9),
            text_color=COLORS['text_secondary']
        )
        tagline.pack(pady=(4, 0))
    def create_main_content(self):
        """Create all main content in Frutiger Aero style"""
        # Main container with fire red border
        main_container = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=18,
            border_width=3,
            border_color=COLORS['accent_blue']
        )
        main_container.pack(fill="x", padx=12, pady=(0, 12))

        # Status bar at top
        self.create_status_bar(main_container)

        # Controls section
        self.create_controls(main_container)

        # Action buttons
        self.create_action_buttons(main_container)

        # Footer
        self.create_footer(main_container)
    
    def create_status_bar(self, parent):
        """Status bar with fire red accents"""
        status_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            height=40,
            border_width=1,
            border_color=COLORS['border']
        )
        status_frame.pack(fill="x", padx=12, pady=(12, 8))
        status_frame.pack_propagate(False)

        # Connection status with glow
        self.conn_indicator = ctk.CTkLabel(
            status_frame,
            text="⬤ OFFLINE",
            font=("Segoe UI", 10, "bold"),
            text_color="#FF4757"
        )
        self.conn_indicator.pack(side="left", padx=15)

        # Coordinates - center
        self.coords_label = ctk.CTkLabel(
            status_frame,
            text="―――",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim']
        )
        self.coords_label.pack(side="left", expand=True)

        # Stats - right with glow effect
        self.stats_label = ctk.CTkLabel(
            status_frame,
            text="0",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['accent_cyan']
        )
        self.stats_label.pack(side="right", padx=15)
        
    def create_controls(self, parent):
        """Compact controls with collapsible sections"""
        controls_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        controls_frame.pack(fill="x", padx=12, pady=0)

        # Collapsible sliders section (CLOSED by default)
        self.create_collapsible_sliders(controls_frame)

        # Quick settings row (always visible)
        self.create_quick_settings(controls_frame)

        # Profile management (always visible)
        self.create_profile_section(controls_frame)

        # Advanced timing controls (collapsible, closed by default)
        self.create_advanced_timing_section(controls_frame)

        # Latency compensation (collapsible, closed by default) - with spacing
        self.create_latency_section(controls_frame)

    def create_advanced_timing_section(self, parent):
        """Advanced timing controls - compact section"""
        # Main container with fixed height
        timing_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border'],
            height=90
        )
        timing_frame.pack(fill="x", pady=(0, 8))
        timing_frame.pack_propagate(False)

        # Content container
        content_frame = ctk.CTkFrame(timing_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=12, pady=8)

        # Header row with label and settings button
        header_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            header_row,
            text="⚡ Advanced Timing",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS['accent_cyan']
        ).pack(side="left")

        # Help icon
        adv_help = ctk.CTkLabel(
            header_row,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        adv_help.pack(side="left", padx=(4, 0))
        ToolTip(adv_help, "Timing avanzado: Markov, Gaussian, Acceleration")

        # Settings button
        settings_btn = ctk.CTkButton(
            header_row,
            text="⚙",
            width=28,
            height=22,
            corner_radius=6,
            fg_color=COLORS['bg_primary'],
            hover_color=COLORS['accent_blue'],
            font=("Segoe UI", 11),
            command=self.open_advanced_timing_dialog
        )
        settings_btn.pack(side="right")

        # Toggles row
        toggles_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        toggles_row.pack(fill="x", pady=(0, 4))

        # Markov Chain toggle
        self.markov_checkbox = ctk.CTkCheckBox(
            toggles_row,
            text="Markov",
            font=("Segoe UI", 9),
            command=self.toggle_markov_chain,
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=4,
            text_color=COLORS['text_primary'],
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan']
        )
        self.markov_checkbox.pack(side="left", padx=(0, 10))

        # Gaussian toggle
        self.gaussian_checkbox = ctk.CTkCheckBox(
            toggles_row,
            text="Gaussian",
            font=("Segoe UI", 9),
            command=self.toggle_gaussian,
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=4,
            text_color=COLORS['text_primary'],
            fg_color=COLORS['accent_green'],
            hover_color=COLORS['accent_green']
        )
        self.gaussian_checkbox.pack(side="left", padx=(0, 10))

        # Acceleration toggle
        self.accel_checkbox = ctk.CTkCheckBox(
            toggles_row,
            text="Accel",
            font=("Segoe UI", 9),
            command=self.toggle_acceleration,
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=4,
            text_color=COLORS['text_primary'],
            fg_color=COLORS['glow'],
            hover_color=COLORS['glow']
        )
        self.accel_checkbox.pack(side="left")

        # Timing monitor (shows real-time values)
        monitor_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        monitor_row.pack(fill="x")

        self.timing_monitor_label = ctk.CTkLabel(
            monitor_row,
            text="Monitor: Ready",
            font=("Consolas", 9),
            text_color=COLORS['text_dim'],
            anchor="w"
        )
        self.timing_monitor_label.pack(side="left", fill="x", expand=True)

    def create_latency_section(self, parent):
        """Sección de compensación de latencia"""
        # Main container
        self.latency_section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        self.latency_section.pack(fill="x", pady=(0, 8))

        # Header (clickable)
        header = ctk.CTkFrame(self.latency_section, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=10)

        # Expand/collapse indicator
        self.latency_expand_label = ctk.CTkLabel(
            header,
            text="▶",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim'],
            width=20
        )
        self.latency_expand_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header,
            text="🌐 Latency Compensation",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['accent_cyan']
        )
        title_label.pack(side="left")

        # Help icon
        latency_help = ctk.CTkLabel(
            header,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        latency_help.pack(side="left", padx=(4, 0))
        ToolTip(latency_help, "Compensa latencia de red en juegos online")

        # Enable toggle
        self.latency_enabled_var = ctk.BooleanVar(value=False)
        self.latency_toggle = ctk.CTkSwitch(
            header,
            text="",
            variable=self.latency_enabled_var,
            command=self.toggle_latency_compensation,
            width=40,
            height=20,
            progress_color=COLORS['accent_green']
        )
        self.latency_toggle.pack(side="right")

        # Make header clickable
        for widget in [header, self.latency_expand_label, title_label]:
            widget.bind("<Button-1>", lambda e: self.toggle_latency_section())

        # Content (collapsible) - INICIA COLAPSADO
        self.latency_content = ctk.CTkFrame(self.latency_section, fg_color="transparent")
        self.latency_expanded = False  # Inicia colapsado

        # Port input
        port_row = ctk.CTkFrame(self.latency_content, fg_color="transparent")
        port_row.pack(fill="x", pady=2)

        # Auto-detect button
        self.latency_auto_btn = ctk.CTkButton(
            port_row,
            text="Auto",
            width=50,
            height=24,
            corner_radius=6,
            fg_color=COLORS['accent_green'],
            hover_color=COLORS['accent_green'],
            font=("Segoe UI", 9, "bold"),
            command=self.auto_detect_game
        )
        self.latency_auto_btn.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            port_row,
            text="Port:",
            font=("Segoe UI", 9),
            text_color=COLORS['text_secondary']
        ).pack(side="left")

        self.latency_port_entry = ctk.CTkEntry(
            port_row,
            width=60,
            height=24,
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary']
        )
        self.latency_port_entry.insert(0, "9222")
        self.latency_port_entry.pack(side="left", padx=5)

        # Connect button
        self.latency_connect_btn = ctk.CTkButton(
            port_row,
            text="Connect",
            width=65,
            height=24,
            corner_radius=6,
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan'],
            font=("Segoe UI", 9),
            command=self.connect_latency_system
        )
        self.latency_connect_btn.pack(side="left", padx=2)

        # Calibrate button
        self.latency_calibrate_btn = ctk.CTkButton(
            port_row,
            text="Calibrate",
            width=70,
            height=24,
            corner_radius=6,
            fg_color=COLORS['accent_green'],
            hover_color=COLORS['accent_green'],
            font=("Segoe UI", 9),
            command=self.start_latency_calibration,
            state="disabled"
        )
        self.latency_calibrate_btn.pack(side="left", padx=2)

        # Stats display
        stats_row = ctk.CTkFrame(self.latency_content, fg_color="transparent")
        stats_row.pack(fill="x", pady=5)

        self.latency_stats_label = ctk.CTkLabel(
            stats_row,
            text="RTT: -- ms | Avg: -- ms | Offset: -- ms",
            font=("Consolas", 9),
            text_color=COLORS['text_dim'],
            anchor="w"
        )
        self.latency_stats_label.pack(fill="x")

        # Compensation status indicator
        status_row = ctk.CTkFrame(self.latency_content, fg_color="transparent")
        status_row.pack(fill="x", pady=2)

        self.latency_status_label = ctk.CTkLabel(
            status_row,
            text="⚫ Disconnected",
            font=("Segoe UI", 9, "bold"),
            text_color="#FF4757",
            anchor="w"
        )
        self.latency_status_label.pack(side="left")

        self.latency_active_label = ctk.CTkLabel(
            status_row,
            text="",
            font=("Segoe UI", 9),
            text_color=COLORS['accent_green'],
            anchor="e"
        )
        self.latency_active_label.pack(side="right")

        # Multiplier slider
        self.latency_mult_slider, self.latency_mult_label = self.create_aero_slider(
            self.latency_content, "Compensation", 0.0, 2.0, 1.0,
            lambda v: self.clicker.latency_compensator.set_compensation_multiplier(v)
        )

    def create_profile_section(self, parent):
        """Compact profile management"""
        profile_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            height=44,
            border_width=1,
            border_color=COLORS['border']
        )
        profile_frame.pack(fill="x", pady=(8, 0))
        profile_frame.pack_propagate(False)

        # Profile dropdown with help icon
        left_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=10, pady=6)

        self.profile_var = ctk.StringVar(value="Profile")
        self.profile_menu = ctk.CTkOptionMenu(
            left_frame,
            variable=self.profile_var,
            values=["Profile"] + self.profile_manager.get_profile_names(),
            width=130,
            height=32,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            button_color=COLORS['accent_blue'],
            button_hover_color=COLORS['accent_cyan'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_hover_color=COLORS['accent_blue'],
            text_color=COLORS['text_primary'],
            font=("Segoe UI", 10)
        )
        self.profile_menu.pack(side="left")

        # Help icon
        profile_help = ctk.CTkLabel(
            left_frame,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        profile_help.pack(side="left", padx=(4, 0))
        ToolTip(profile_help, "Guarda y carga configuraciones")

        # Mini buttons
        btn_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)

        for text, cmd, color in [("Load", self.load_selected_profile, COLORS['accent_blue']),
                                  ("Save", self.save_profile, COLORS['accent_green']),
                                  ("Del", self.delete_profile, COLORS['accent_red'])]:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                width=55,
                height=30,
                corner_radius=8,
                fg_color=color,
                hover_color=color,
                font=("Segoe UI", 10, "bold"),
                command=cmd
            )
            btn.pack(side="left", padx=3)

    def create_collapsible_sliders(self, parent):
        """Collapsible sliders section (closed by default)"""
        # Main container
        self.sliders_section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        self.sliders_section.pack(fill="x", pady=(0, 8))

        # Header with toggle button
        header_frame = ctk.CTkFrame(self.sliders_section, fg_color="transparent", height=36)
        header_frame.pack(fill="x", padx=12, pady=8)
        header_frame.pack_propagate(False)

        # Title
        ctk.CTkLabel(
            header_frame,
            text="BASIC SETTINGS",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Help icon
        help_label = ctk.CTkLabel(
            header_frame,
            text="?",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim'],
            width=16,
            height=16
        )
        help_label.pack(side="left", padx=(4, 0))
        ToolTip(help_label, "Clicks, Speed, Duration y Delay del autoclicker")

        # Toggle button
        self.sliders_toggle_btn = ctk.CTkButton(
            header_frame,
            text="▼",
            width=30,
            height=24,
            font=("Segoe UI", 12),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['bg_primary'],
            text_color=COLORS['text_secondary'],
            corner_radius=6,
            command=self.toggle_sliders_section
        )
        self.sliders_toggle_btn.pack(side="right")

        # Content frame (hidden by default)
        self.sliders_content = ctk.CTkFrame(self.sliders_section, fg_color="transparent")
        # Don't pack it - it's hidden by default

        # Create sliders inside content frame
        self.clicks_slider, self.clicks_label = self.create_aero_slider(
            self.sliders_content, "Clicks", 1, 100, 24,
            lambda v: setattr(self.clicker.config, 'clicks', int(v))
        )
        self.interval_slider, self.interval_label = self.create_aero_slider(
            self.sliders_content, "Speed", 1, 200, 10,
            lambda v: setattr(self.clicker.config, 'interval', int(v))
        )
        self.duration_slider, self.duration_label = self.create_aero_slider(
            self.sliders_content, "Duration", 0.01, 2.0, 0.30,
            lambda v: setattr(self.clicker.config, 'duration', float(v))
        )
        self.delay_slider, self.delay_label = self.create_aero_slider(
            self.sliders_content, "Delay", 0.0, 1.0, 0.0,
            lambda v: setattr(self.clicker.config, 'auto_burst_delay', float(v))
        )

        # Track state
        self.sliders_section_open = False

    def resize_window(self):
        """Dynamically resize window based on open sections"""
        base_height = 670  # Base height with all sections closed

        # Add height for each open section
        if self.sliders_section_open:
            base_height += 200  # Basic settings section height

        if hasattr(self, 'latency_expanded') and self.latency_expanded:
            base_height += 190  # Latency section height

        self.geometry(f"400x{base_height}")

    def toggle_sliders_section(self):
        """Toggle sliders section visibility and resize window"""
        if self.sliders_section_open:
            # Close section
            self.sliders_content.pack_forget()
            self.sliders_toggle_btn.configure(text="▼")
            self.sliders_section_open = False
            # Shrink window
            self.resize_window()
        else:
            # Open section
            self.sliders_content.pack(fill="x", padx=0, pady=(0, 8))
            self.sliders_toggle_btn.configure(text="▲")
            self.sliders_section_open = True
            # Expand window
            self.resize_window()

    def create_aero_slider(self, parent, label, from_, to, initial, command):
        """Frutiger Aero styled compact slider"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=12)

        # Label row
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            label_frame,
            text=label,
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        ).pack(side="left")

        value_label = ctk.CTkLabel(
            label_frame,
            text=str(initial),
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['accent_cyan']
        )
        value_label.pack(side="right")

        # Slider with glow effect
        slider = ctk.CTkSlider(
            frame,
            from_=from_,
            to=to,
            number_of_steps=(to - from_) * (100 if from_ < 1 else 1),
            height=16,
            button_color=COLORS['accent_cyan'],
            button_hover_color=COLORS['glow'],
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['bg_primary'],
            command=lambda v: self.update_aero_slider(value_label, v, command, from_ < 1)
        )
        slider.set(initial)
        slider.pack(fill="x", pady=(0, 0))
        return slider, value_label
    
    def update_aero_slider(self, label, value, command, is_decimal):
        """Update slider value display"""
        if is_decimal:
            val = round(float(value), 2)
            label.configure(text=f"{val:.2f}s" if val else "0")
        else:
            val = int(value)
            label.configure(text=str(val))
        if command:
            command(val)

    def create_quick_settings(self, parent):
        """Compact quick settings with toggle buttons"""
        settings_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        settings_frame.pack(fill="x", pady=(0, 8))

        # Type and Button in one row
        row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(10, 8))

        # Click type
        type_frame = ctk.CTkFrame(row, fg_color="transparent")
        type_frame.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Type label with help
        type_label_frame = ctk.CTkFrame(type_frame, fg_color="transparent")
        type_label_frame.pack(anchor="w", pady=(0, 4), fill="x")

        ctk.CTkLabel(
            type_label_frame,
            text="Type",
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        ).pack(side="left")

        type_help = ctk.CTkLabel(
            type_label_frame,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        type_help.pack(side="left", padx=(4, 0))
        ToolTip(type_help, "Single, Double o Triple click")

        self.type_selector = ctk.CTkSegmentedButton(
            type_frame,
            values=["Single", "Double", "Triple"],
            command=lambda v: setattr(self.clicker.config, 'click_type', v.lower()),
            font=("Segoe UI", 10, "bold"),
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            selected_color=COLORS['accent_blue'],
            selected_hover_color=COLORS['accent_cyan'],
            unselected_color=COLORS['bg_primary'],
            unselected_hover_color=COLORS['border'],
            height=32
        )
        self.type_selector.pack(fill="x")
        self.type_selector.set("Single")

        # Mouse button
        button_frame = ctk.CTkFrame(row, fg_color="transparent")
        button_frame.pack(side="right", fill="x", expand=True, padx=(6, 0))

        # Button label with help
        button_label_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_label_frame.pack(anchor="w", pady=(0, 4), fill="x")

        ctk.CTkLabel(
            button_label_frame,
            text="Button",
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        ).pack(side="left")

        button_help = ctk.CTkLabel(
            button_label_frame,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        button_help.pack(side="left", padx=(4, 0))
        ToolTip(button_help, "Botón del mouse a clickear")

        self.button_selector = ctk.CTkSegmentedButton(
            button_frame,
            values=["Left", "Right", "Mid"],
            command=lambda v: setattr(self.clicker.config, 'mouse_button', {'Left': 'left', 'Right': 'right', 'Mid': 'middle'}[v]),
            font=("Segoe UI", 10, "bold"),
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            selected_color=COLORS['accent_blue'],
            selected_hover_color=COLORS['accent_cyan'],
            unselected_color=COLORS['bg_primary'],
            unselected_hover_color=COLORS['border'],
            height=32
        )
        self.button_selector.pack(fill="x")
        self.button_selector.set("Left")

        # Options row
        options_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        options_row.pack(fill="x", padx=12, pady=(0, 10))

        # Humanize with help
        humanize_frame = ctk.CTkFrame(options_row, fg_color="transparent")
        humanize_frame.pack(side="left", padx=(0, 8))

        self.humanize_checkbox = ctk.CTkCheckBox(
            humanize_frame,
            text="Humanize",
            font=("Segoe UI", 10),
            command=self.toggle_humanization,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan']
        )
        self.humanize_checkbox.pack(side="left")

        humanize_help = ctk.CTkLabel(
            humanize_frame,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        humanize_help.pack(side="left", padx=(4, 0))
        ToolTip(humanize_help, "Agrega delays aleatorios para parecer humano")

        # Burst Var with help
        burst_frame = ctk.CTkFrame(options_row, fg_color="transparent")
        burst_frame.pack(side="right", padx=(8, 0))

        self.advanced_checkbox = ctk.CTkCheckBox(
            burst_frame,
            text="Burst Var",
            font=("Segoe UI", 10),
            command=self.toggle_advanced_timing,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_green'],
            hover_color=COLORS['accent_green']
        )
        self.advanced_checkbox.pack(side="left")

        burst_help = ctk.CTkLabel(
            burst_frame,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        burst_help.pack(side="left", padx=(4, 0))
        ToolTip(burst_help, "Varía la cantidad de clicks por burst")

    def create_action_buttons(self, parent):
        """Action button - auto-burst"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=12, pady=(0, 4))

        # Single auto-burst button with fire red accent
        self.autoburst_button = ctk.CTkButton(
            buttons_frame,
            text="AUTO-BURST",
            height=42,
            corner_radius=12,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['accent_blue'],
            border_width=2,
            border_color=COLORS['accent_blue'],
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text_primary'],
            command=self.toggle_auto_burst
        )
        self.autoburst_button.pack(fill="x")

    def create_footer(self, parent):
        """Footer with version and license info"""
        footer = ctk.CTkFrame(parent, fg_color="transparent", height=65)
        footer.pack(fill="x", padx=12, pady=(0, 10))
        footer.pack_propagate(False)

        # License info label
        self.license_label = ctk.CTkLabel(
            footer,
            text="",
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        )
        self.license_label.pack(side="bottom", pady=(4, 0))

        # Version and update button
        version_frame = ctk.CTkFrame(footer, fg_color="transparent")
        version_frame.pack(side="bottom", pady=(0, 4))

        self.version_label = ctk.CTkLabel(
            version_frame,
            text=f"v{self.updater.current_version}",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['text_primary']
        )
        self.version_label.pack(side="left", padx=(0, 10))

        self.update_btn = ctk.CTkButton(
            version_frame,
            text="Check Updates",
            width=120,
            height=28,
            font=("Segoe UI", 10),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['accent_blue'],
            text_color=COLORS['text_primary'],
            border_width=2,
            border_color=COLORS['accent_blue'],
            corner_radius=8,
            command=self.check_for_updates
        )
        self.update_btn.pack(side="left")

        # Update license info
        self.update_license_display()

    def toggle_humanization(self):
        self.clicker.config.humanize_enabled = bool(self.humanize_checkbox.get())



    def toggle_auto_burst(self):
        self.clicker.config.auto_burst_enabled = not self.clicker.config.auto_burst_enabled
        self.sync_auto_burst_state()

    def toggle_advanced_timing(self):
        """Toggle burst variations mode - simplified auto-selection"""
        try:
            # Get the desired state from checkbox
            desired_state = bool(self.advanced_checkbox.get())

            # Update config
            self.clicker.config.advanced_timing_enabled = desired_state

            # Auto-select the best profile when enabled
            if desired_state:
                # Automatically select "Timing Critical" as the best profile
                self.clicker.config.advanced_profile = self.clicker.advanced_profiles['timing_critical']
            else:
                # Clear profile when disabled
                self.clicker.config.advanced_profile = None

        except Exception as e:
            print(f"Error in toggle_advanced_timing: {e}")
            # Reset to safe state
            self.clicker.config.advanced_timing_enabled = False
            self.clicker.config.advanced_profile = None
            if hasattr(self, 'advanced_checkbox'):
                self.advanced_checkbox.deselect()

    # load_advanced_profile method removed - no longer needed with simplified UI

    # update_burst_variations_ui method removed - no longer needed with simplified UI

    def toggle_markov_chain(self):
        """Toggle Markov Chain timing system"""
        self.clicker.config.markov_chain_enabled = bool(self.markov_checkbox.get())

    def toggle_gaussian(self):
        """Toggle Gaussian delay system"""
        self.clicker.config.gaussian_delay_enabled = bool(self.gaussian_checkbox.get())

    def toggle_acceleration(self):
        """Toggle acceleration profile system"""
        self.clicker.config.acceleration_enabled = bool(self.accel_checkbox.get())
        # Reset acceleration profile when enabled
        if self.clicker.config.acceleration_enabled:
            self.clicker.acceleration_profile.reset()

    def toggle_latency_section(self):
        """Expande/colapsa la sección de latency"""
        if self.latency_expanded:
            # Colapsar
            self.latency_content.pack_forget()
            self.latency_expand_label.configure(text="▶")
            self.latency_expanded = False
            # Reducir ventana
            self.resize_window()
        else:
            # Expandir
            self.latency_content.pack(fill="x", padx=12, pady=(0, 10))
            self.latency_expand_label.configure(text="▼")
            self.latency_expanded = True
            # Aumentar ventana para mostrar contenido
            self.resize_window()

    def auto_detect_game(self):
        """Auto-detecta el juego y el puerto"""
        self.latency_auto_btn.configure(text="...", state="disabled")
        self.latency_status_label.configure(text="🟡 Lanzando juego...", text_color="#FFA502")

        def detect_thread():
            port = self.clicker.latency_compensator.auto_detect_game()
            if port:
                self._safe_after(0, self._on_port_detected, port)
            else:
                self._safe_after(0, self._on_detect_failed)

        threading.Thread(target=detect_thread, daemon=True).start()

    def _on_port_detected(self, port):
        """Callback cuando se detecta el puerto"""
        self.latency_port_entry.delete(0, 'end')
        self.latency_port_entry.insert(0, str(port))
        self.latency_auto_btn.configure(text="Auto", state="normal")
        self.latency_status_label.configure(text=f"🟢 Puerto {port} detectado", text_color=COLORS['accent_green'])

        # Auto-conectar
        self.connect_latency_system()

    def _on_detect_failed(self):
        """Callback cuando falla la detección"""
        self.latency_auto_btn.configure(text="Auto", state="normal")
        self.latency_status_label.configure(text="🔴 No se detectó el puerto", text_color="#FF4757")
        messagebox.showerror("Error", "No se pudo detectar el puerto DevTools.\nAsegúrate de que el launcher esté configurado correctamente.")

    def toggle_latency_compensation(self):
        """Toggle latency compensation"""
        enabled = self.latency_enabled_var.get()
        self.clicker.config.latency_compensation_enabled = enabled
        self.clicker.latency_compensator.enable_compensation(enabled)

        if enabled:
            self.latency_active_label.configure(text="✓ COMPENSATING", text_color=COLORS['accent_green'])
        else:
            self.latency_active_label.configure(text="")

    def connect_latency_system(self):
        """Conecta al sistema de latencia del juego"""
        try:
            port = int(self.latency_port_entry.get())
            self.clicker.config.latency_devtools_port = port

            success = self.clicker.latency_compensator.connect_to_game(port)

            if success:
                self.latency_connect_btn.configure(text="Connected", fg_color=COLORS['accent_green'])
                self.latency_calibrate_btn.configure(state="normal")
                self.latency_status_label.configure(text="🟢 Connected", text_color=COLORS['accent_green'])
                messagebox.showinfo("Success", f"Conectado al puerto {port}\n\nAhora haz click en 'Calibrate' para medir la latencia.")
            else:
                self.latency_status_label.configure(text="🔴 Connection Failed", text_color="#FF4757")
                messagebox.showerror("Error", "No se pudo conectar. Asegúrate de que el juego esté abierto con DevTools.")
        except ValueError:
            messagebox.showerror("Error", "Puerto inválido")

    def start_latency_calibration(self):
        """Inicia calibración automática"""
        self.clicker.latency_compensator.start_calibration(duration_seconds=10)
        self.latency_calibrate_btn.configure(text="Calibrating...", state="disabled")
        messagebox.showinfo("Calibration", "Calibrando durante 10 segundos...\nRealiza acciones en el juego.")

    def update_latency_stats(self, stats):
        """Actualiza display de estadísticas de latencia"""
        current = stats.get('current_rtt_ms', stats.get('current', 0))
        avg = stats.get('avg_rtt_ms', stats.get('avg', 0))
        offset = stats.get('optimal_offset_ms', 0)
        text = f"RTT: {current:.1f}ms | Avg: {avg:.1f}ms | Offset: {offset:.1f}ms"
        self.latency_stats_label.configure(text=text)

    def _handle_latency_event(self, event_data):
        """Maneja eventos del sistema de latencia"""
        if not event_data:
            return

        event_type = event_data.get('type')
        data = event_data.get('data')

        if event_type == 'ping_update':
            self._safe_after(0, self.update_latency_stats, data)
        elif event_type == 'calibration_complete':
            self._safe_after(0, self._on_calibration_complete, data)
        elif event_type == 'calibration_failed':
            self._safe_after(0, self._on_calibration_failed, data)
        elif event_type == 'connected':
            self._safe_after(0, self._on_latency_connected)
        elif event_type == 'port_detected':
            self._safe_after(0, self._on_port_detected, data)
        elif event_type == 'status':
            self._safe_after(0, lambda: self.latency_status_label.configure(text=f"🟡 {data}", text_color="#FFA502"))
        elif event_type == 'error':
            self._safe_after(0, lambda: messagebox.showerror("Latency Error", str(data)))

    def _on_calibration_complete(self, data):
        """Callback cuando termina la calibración"""
        self.latency_calibrate_btn.configure(text="Calibrate", state="normal")
        messagebox.showinfo("Calibration Complete",
            f"Calibración completa!\n"
            f"Muestras: {data['samples']}\n"
            f"Offset óptimo: {data['optimal_offset_ms']:.2f}ms\n"
            f"RTT promedio: {data['avg_rtt']:.2f}ms")

    def _on_calibration_failed(self, reason):
        """Callback cuando falla la calibración"""
        self.latency_calibrate_btn.configure(text="Calibrate", state="normal")
        messagebox.showerror("Calibration Failed",
            f"Calibración fallida: {reason}\n\n"
            f"Asegúrate de estar jugando activamente durante la calibración\n"
            f"para generar tráfico de red.")

    def _on_latency_connected(self):
        """Callback cuando se conecta al sistema de latencia"""
        pass

    def open_advanced_timing_dialog(self):
        """Open dialog for advanced timing configuration"""
        dialog = AdvancedTimingDialog(self, self.clicker.config)
        dialog.grab_set()  # Make dialog modal
        self.wait_window(dialog)  # Wait for dialog to close

    def handle_callback(self, event, data=None):
        # Don't schedule callbacks if window is closing
        if self._is_closing:
            return

        if event == 'burst_started':
            self._safe_after(0, self.set_burst_state, True)
        elif event == 'burst_stopped':
            self._safe_after(0, self.set_burst_state, False)
        elif event == 'latency_event':
            self._handle_latency_event(data)
        elif event == 'coords_captured':
            self._safe_after(0, self.update_coords)
        elif event == 'connection_changed':
            self._safe_after(0, self.update_connection_status)
        elif event == 'stats_update':
            self._safe_after(0, self.update_stats)
        elif event == 'auto_burst_toggled':
            self._safe_after(0, self.sync_auto_burst_state)

    def _safe_after(self, delay, callback, *args):
        """Schedule a callback and track it for cleanup"""
        if not self._is_closing:
            try:
                after_id = self.after(delay, callback, *args)
                self._after_ids.append(after_id)
                return after_id
            except:
                pass
        return None

    def set_burst_state(self, bursting):
        if bursting:
            # Reset burst clicks counter when starting a new burst
            self.clicker.current_burst_clicks = 0
        else:
            # Save last burst count before resetting
            self.clicker.last_burst_clicks = self.clicker.current_burst_clicks
            # Reset current burst counter after delay
            self._safe_after(3000, lambda: setattr(self.clicker, 'current_burst_clicks', 0))
        # Update stats immediately
        self.update_stats()

    def update_coords(self):
        x, y = self.clicker.target_x, self.clicker.target_y
        self.coords_label.configure(
            text=f"{x},{y}",
            text_color=COLORS['accent_green']
        )

    def update_connection_status(self):
        if self.clicker.is_connected:
            self.conn_indicator.configure(
                text="⬤ ONLINE",
                text_color=COLORS['accent_green']
            )
        else:
            self.conn_indicator.configure(
                text="⬤ OFFLINE",
                text_color="#FF4757"
            )
            
    def update_stats(self):
        # Update the stats label with total clicks
        total_clicks = self.clicker.total_clicks_sent
        # Glow effect during burst
        if self.clicker.active_bursts > 0:
            self.stats_label.configure(
                text=str(total_clicks),
                text_color=COLORS['glow']
            )
        else:
            self.stats_label.configure(
                text=str(total_clicks),
                text_color=COLORS['accent_cyan']
            )

        # Update timing monitor
        self.update_timing_monitor()

    def update_timing_monitor(self):
        """Update the timing monitor with real-time values"""
        if self.clicker.active_bursts == 0:
            self.timing_monitor_label.configure(text="Monitor: Ready")
            return

        # Build monitor string
        parts = []

        # Show current delay
        parts.append(f"Delay:{self.clicker.last_delay_ms:.1f}ms")

        # Show latency compensation if enabled
        if self.clicker.config.latency_compensation_enabled and self.clicker.latency_compensator.compensation_enabled:
            rtt = self.clicker.latency_compensator.current_rtt_ms
            if rtt > 0:
                parts.append(f"🌐-{rtt/2:.0f}ms")

        # Show Markov state if enabled
        if self.clicker.config.markov_chain_enabled:
            state_colors = {'fast': '🟢', 'medium': '🟡', 'slow': '🔴'}
            icon = state_colors.get(self.clicker.last_markov_state, '⚪')
            parts.append(f"M:{icon}")

        # Show Gaussian if enabled
        if self.clicker.config.gaussian_delay_enabled:
            parts.append(f"G:±{abs(self.clicker.last_gaussian_value*1000):.1f}")

        # Show Acceleration progress if enabled
        if self.clicker.config.acceleration_enabled:
            progress_pct = int(self.clicker.last_accel_progress * 100)
            parts.append(f"A:{progress_pct}%")

        monitor_text = " | ".join(parts)
        self.timing_monitor_label.configure(text=monitor_text)
        
    def sync_auto_burst_state(self):
        if self.clicker.config.auto_burst_enabled:
            self.autoburst_button.configure(
                text="AUTO-BURST: ON",
                fg_color=COLORS['accent_blue'],
                border_color=COLORS['accent_blue'],
                text_color=COLORS['bg_primary']
            )
        else:
            self.autoburst_button.configure(
                text="AUTO-BURST",
                fg_color=COLORS['bg_card'],
                border_color=COLORS['accent_blue'],
                text_color=COLORS['text_primary']
            )

    def load_last_profile(self):
        current = self.profile_manager.get_current_profile()
        if current:
            success, config_data = self.profile_manager.load_profile(current)
            if success:
                self.clicker.config.from_dict(config_data)
                self.sync_ui_with_config()
                self.profile_var.set(current)

    def save_profile(self):
        dialog = ctk.CTkInputDialog(text="Enter profile name:", title="Save Profile")
        profile_name = dialog.get_input()
        if profile_name:
            success, message = self.profile_manager.save_profile(profile_name, self.clicker.config)
            if success:
                self.update_profile_menu()
                self.profile_var.set(profile_name)
            else:
                messagebox.showerror("Error", message)

    def load_selected_profile(self):
        profile_name = self.profile_var.get()
        if profile_name and profile_name != "Profile":
            success, config_data = self.profile_manager.load_profile(profile_name)
            if success:
                self.clicker.config.from_dict(config_data)
                self.sync_ui_with_config()

    def delete_profile(self):
        profile_name = self.profile_var.get()
        if profile_name and profile_name != "Profile":
            if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{profile_name}'?"):
                success, message = self.profile_manager.delete_profile(profile_name)
                if success:
                    self.update_profile_menu()
                    self.profile_var.set("Profile")

    def update_profile_menu(self):
        self.profile_menu.configure(values=["Profile"] + self.profile_manager.get_profile_names())

    def sync_ui_with_config(self):
        """Sync UI elements with current config"""
        self.clicks_slider.set(self.clicker.config.clicks)
        self.interval_slider.set(self.clicker.config.interval)
        self.duration_slider.set(self.clicker.config.duration)
        self.delay_slider.set(self.clicker.config.auto_burst_delay)
        
        self.update_aero_slider(self.clicks_label, self.clicker.config.clicks, lambda v: setattr(self.clicker.config, 'clicks', int(v)), False)
        self.update_aero_slider(self.interval_label, self.clicker.config.interval, lambda v: setattr(self.clicker.config, 'interval', int(v)), False)
        self.update_aero_slider(self.duration_label, self.clicker.config.duration, lambda v: setattr(self.clicker.config, 'duration', float(v)), True)
        self.update_aero_slider(self.delay_label, self.clicker.config.auto_burst_delay, lambda v: setattr(self.clicker.config, 'auto_burst_delay', float(v)), True)
        
        self.type_selector.set(self.clicker.config.click_type.capitalize())
        btn_map = {'left': 'Left', 'right': 'Right', 'middle': 'Mid'}
        self.button_selector.set(btn_map.get(self.clicker.config.mouse_button, 'Left'))
        
        if self.clicker.config.humanize_enabled:
            self.humanize_checkbox.select()
        else:
            self.humanize_checkbox.deselect()

        # Sync new advanced timing checkboxes
        if self.clicker.config.markov_chain_enabled:
            self.markov_checkbox.select()
        else:
            self.markov_checkbox.deselect()

        if self.clicker.config.gaussian_delay_enabled:
            self.gaussian_checkbox.select()
        else:
            self.gaussian_checkbox.deselect()

        if self.clicker.config.acceleration_enabled:
            self.accel_checkbox.select()
        else:
            self.accel_checkbox.deselect()

        self.sync_auto_burst_state()

    def save_current_config_on_exit(self):
        pass
        
    def update_license_info(self):
        pass
        
    def start_license_monitor(self):
        pass

    def update_license_display(self):
        """Update the license information display"""
        if not self.license_label:
            return

        try:
            time_remaining = self.key_manager.get_time_remaining()
            license_info = self.key_manager.get_license_info()
            license_type = license_info.get('type', 'Unknown')

            # Format the display text
            if time_remaining == "Lifetime":
                text = f"License: {license_type} • Lifetime"
            elif time_remaining == "Expired":
                text = "License: EXPIRED"
                self.license_label.configure(text_color=COLORS['accent_red'])
            elif time_remaining == "Unknown":
                text = f"License: {license_type}"
            else:
                text = f"License: {license_type} • {time_remaining} remaining"

            self.license_label.configure(text=text)
        except Exception as e:
            print(f"Error updating license display: {e}")

    def start_license_validation(self):
        """Start periodic license validation in background"""
        if self._is_closing:
            return

        try:
            # Update display first (don't validate, just show info)
            self.update_license_display()

            # Schedule periodic validations
            # Check every 10 minutes (600000 ms) - not too aggressive
            after_id = self.after(600000, self.periodic_license_check)
            self._after_ids.append(after_id)

            # Also do a network validation every 30 minutes
            after_id = self.after(1800000, self.validate_license_online)
            self._after_ids.append(after_id)

        except Exception as e:
            print(f"Error in license validation: {e}")

    def periodic_license_check(self):
        """Periodic license check (called every 10 minutes)"""
        if self._is_closing:
            return

        try:
            # Validate license (skip network to avoid blocking UI)
            valid, message = self.key_manager.validate(skip_network=True)

            if not valid:
                # License expired or invalid - close the app
                print(f"License validation failed: {message}")
                self.show_license_expired_dialog()
                return

            # Update display
            self.update_license_display()

            # Schedule next check in 10 minutes
            after_id = self.after(600000, self.periodic_license_check)
            self._after_ids.append(after_id)

        except Exception as e:
            print(f"Error in periodic license check: {e}")
            # Don't close on error, just log it
            # Schedule next check anyway
            after_id = self.after(600000, self.periodic_license_check)
            self._after_ids.append(after_id)

    def validate_license_online(self):
        """Perform online license validation"""
        if self._is_closing:
            return

        try:
            valid, message = self.key_manager.validate(skip_network=False)

            if not valid:
                self.show_license_expired_dialog()
                return

            # Update display
            self.update_license_display()
        except Exception as e:
            print(f"Error in online validation: {e}")

    def show_license_expired_dialog(self):
        """Show dialog when license expires and close app"""
        try:
            import tkinter.messagebox as messagebox
            self._is_closing = True
            self._cancel_all_callbacks()
            messagebox.showerror(
                "License Expired",
                "Your license has expired. The application will now close.\n\nPlease contact support to renew your license."
            )
        except:
            pass
        finally:
            try:
                self.clicker.stop()
            except:
                pass
            try:
                self.destroy()
            except:
                pass
            sys.exit(0)

    def check_for_updates(self):
        """Check for updates in background thread"""
        if self._is_closing:
            return

        self.update_btn.configure(text="Checking...", state="disabled")

        def check_thread():
            try:
                has_update, version, url, notes = self.updater.is_update_available()
                self._safe_after(0, self._on_update_check_complete, has_update, version, url, notes)
            except Exception as e:
                print(f"Error checking updates: {e}")
                self._safe_after(0, self._on_update_check_failed)

        threading.Thread(target=check_thread, daemon=True).start()

    def _on_update_check_complete(self, has_update, version, url, notes):
        """Handle update check completion"""
        if self._is_closing:
            return

        self.update_btn.configure(text="Check Updates", state="normal")

        if has_update:
            self.show_update_dialog(version, url, notes)
        else:
            messagebox.showinfo(
                "No Updates",
                f"You're running the latest version (v{self.updater.current_version})"
            )

    def _on_update_check_failed(self):
        """Handle update check failure"""
        if self._is_closing:
            return

        self.update_btn.configure(text="Check Updates", state="normal")
        messagebox.showerror(
            "Update Check Failed",
            "Could not check for updates. Please try again later."
        )

    def show_update_dialog(self, version, url, notes):
        """Show update available dialog"""
        if self._is_closing:
            return

        # Create custom dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Available")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS['bg_primary'])

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')

        # Make modal
        dialog.transient(self)
        dialog.grab_set()

        # Header
        header = ctk.CTkLabel(
            dialog,
            text=f"🎉 New Version Available: v{version}",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS['accent_cyan']
        )
        header.pack(pady=(20, 10))

        # Current version
        current = ctk.CTkLabel(
            dialog,
            text=f"Current: v{self.updater.current_version}",
            font=("Segoe UI", 11),
            text_color=COLORS['text_secondary']
        )
        current.pack(pady=(0, 15))

        # Release notes
        notes_label = ctk.CTkLabel(
            dialog,
            text="What's New:",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['text_primary']
        )
        notes_label.pack(pady=(0, 5))

        notes_frame = ctk.CTkFrame(
            dialog,
            fg_color=COLORS['bg_card'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        notes_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        notes_text = ctk.CTkTextbox(
            notes_frame,
            font=("Segoe UI", 10),
            fg_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
            wrap="word",
            activate_scrollbars=True
        )
        notes_text.pack(fill="both", expand=True, padx=5, pady=5)
        notes_text.insert("1.0", notes)
        notes_text.configure(state="disabled")

        # Progress bar (hidden initially)
        self.update_progress = ctk.CTkProgressBar(
            dialog,
            width=400,
            height=8,
            fg_color=COLORS['bg_card'],
            progress_color=COLORS['accent_cyan']
        )
        self.update_progress.set(0)

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))

        def start_update():
            update_btn.configure(state="disabled", text="Downloading...")
            later_btn.configure(state="disabled")
            self.update_progress.pack(padx=20, pady=(0, 10))
            self.download_and_install_update(url, dialog)

        update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Now",
            width=140,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan'],
            command=start_update
        )
        update_btn.pack(side="left", padx=5)

        later_btn = ctk.CTkButton(
            btn_frame,
            text="Later",
            width=140,
            height=35,
            font=("Segoe UI", 12),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['border'],
            border_width=1,
            border_color=COLORS['border'],
            command=dialog.destroy
        )
        later_btn.pack(side="left", padx=5)

    def download_and_install_update(self, url, dialog):
        """Download and install update"""
        def progress_callback(downloaded, total):
            if total > 0:
                progress = downloaded / total
                self._safe_after(0, lambda: self.update_progress.set(progress))

        def download_thread():
            try:
                # Download
                update_file = self.updater.download_update(url, progress_callback)

                if update_file:
                    # Apply update
                    if self.updater.apply_update(update_file):
                        self._safe_after(0, lambda: messagebox.showinfo(
                            "Update Complete",
                            "Update downloaded! The application will now restart."
                        ))
                        self._safe_after(100, self.quit)
                    else:
                        self._safe_after(0, lambda: messagebox.showerror(
                            "Update Failed",
                            "Failed to apply update. Please try again."
                        ))
                        self._safe_after(0, dialog.destroy)
                else:
                    self._safe_after(0, lambda: messagebox.showerror(
                        "Download Failed",
                        "Failed to download update. Please try again."
                    ))
                    self._safe_after(0, dialog.destroy)
            except Exception as e:
                print(f"Update error: {e}")
                self._safe_after(0, lambda: messagebox.showerror(
                    "Update Error",
                    f"An error occurred: {str(e)}"
                ))
                self._safe_after(0, dialog.destroy)

        threading.Thread(target=download_thread, daemon=True).start()

    def on_close(self):
        self._is_closing = True
        self._cancel_all_callbacks()
        self.clicker.stop()
        self.destroy()

    def _cancel_all_callbacks(self):
        """Cancel all scheduled after callbacks"""
        for after_id in self._after_ids:
            try:
                self.after_cancel(after_id)
            except:
                pass
        self._after_ids.clear()

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    key_manager = KeyManager()
    
    # Check if already activated
    if not key_manager.is_activated():
        # Show activation window
        activation_window = ActivationWindow()
        activation_success = activation_window.run()
        
        # If activation failed or user closed window, exit
        if not activation_success:
            sys.exit(0)
    
    # If activated, show main GUI
    app = AntarcticGUI(key_manager=key_manager)
    app.run()
