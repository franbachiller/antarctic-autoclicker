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

# GUI Configuration - Frutiger Aero Style
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Frutiger Aero Color Palette - Enhanced Depth & Contrast
COLORS = {
    'bg_primary': '#090C14',      # Deep blue-black
    'bg_secondary': '#0F1419',    # Lighter blue-black
    'bg_card': '#161B26',         # Card background
    'accent_blue': '#4A7BA7',     # Muted professional blue
    'accent_cyan': '#6B9FCC',     # Soft blue (más brillante)
    'accent_green': '#5A8AB0',    # Muted blue-green
    'text_primary': '#E0EBF5',    # Soft blue-white (más brillante)
    'text_secondary': '#7A92AB',  # Muted blue-gray
    'text_dim': '#4E6278',        # Dim blue
    'border': '#2D3F54',          # Subtle border (más visible)
    'glow': '#6BA5D8',            # Soft glow effect
    'accent_red': '#D85A5A',      # Muted red for delete (más visible)
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

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                # Type conversion for boolean fields
                if key in ['advanced_timing_enabled', 'humanize_enabled', 'humanize_advanced', 'ultra_mode', 'auto_burst_enabled']:
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

    def validate(self):
        return self.auth_client.validate()

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

        # Advanced timing system components
        self.threading_optimizer = ThreadingOptimizer()
        self.delay_engine = DelayPatternEngine()
        self.event_sequence = ClickEventSequence()

        # Predefined advanced profiles
        self.advanced_profiles = self._create_advanced_profiles()

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
            return 0
        
        # Start with the interval slider value (in milliseconds, convert to seconds)
        base_delay = self.config.interval / 1000.0
        
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
        
        # Ensure minimum delay
        return max(0.001, base_delay)

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
                
                # Send the batch of clicks
                for i in range(clicks_to_send):
                    if not self.running:
                        break
                    
                    # Send click down
                    user32.SendMessageW(hwnd, self._msg_down, self._wparam, self._lparam)
                    
                    # Apply delay if not ultra mode
                    if not ultra_mode:
                        delay = self.get_timing_delay()
                        if delay > 0:
                            time.sleep(delay)
                    
                    # Send click up
                    user32.SendMessageW(hwnd, self._msg_up, 0, self._lparam_up)
                    
                    # Update counters
                    self.total_clicks_sent += 1
                    self.current_burst_clicks += 1
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
        self.geometry("400x580")  # Ultra compact Frutiger Aero style
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

        self.setup_ui()
        self.clicker.start()
        self.load_last_profile()

    def setup_ui(self):
        self.configure(fg_color=COLORS['bg_primary'])
        self.create_header()
        self.create_main_content()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_header(self):
        """Frutiger Aero styled header with text logo"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=0, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Stylized text logo - Frutiger Aero style
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Main title - Modern professional font
        title = ctk.CTkLabel(
            logo_frame,
            text="A N T A R C T I C",
            font=("Bahnschrift SemiBold", 34, "bold"),
            text_color=COLORS['accent_cyan']
        )
        title.pack()
        
        # Subtle tagline
        tagline = ctk.CTkLabel(
            logo_frame,
            text="by bachi",
            font=("Arial", 9),
            text_color=COLORS['text_dim']
        )
        tagline.pack(pady=(3, 0))
    def create_main_content(self):
        """Create all main content in Frutiger Aero style"""
        # Main container with enhanced glass-like effect
        main_container = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=18,
            border_width=2,
            border_color=COLORS['accent_blue']
        )
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Status bar at top
        self.create_status_bar(main_container)
        
        # Controls section
        self.create_controls(main_container)
        
        # Action buttons
        self.create_action_buttons(main_container)
        
        # Footer
        self.create_footer(main_container)
    
    def create_status_bar(self, parent):
        """Frutiger Aero status bar - compact and glowing"""
        status_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            height=36,
            border_width=1,
            border_color=COLORS['border']
        )
        status_frame.pack(fill="x", padx=10, pady=(10, 6))
        status_frame.pack_propagate(False)

        # Connection status with glow
        self.conn_indicator = ctk.CTkLabel(
            status_frame,
            text="⬤ OFFLINE",
            font=("Segoe UI", 9, "bold"),
            text_color="#FF4757"
        )
        self.conn_indicator.pack(side="left", padx=12)

        # Coordinates - center
        self.coords_label = ctk.CTkLabel(
            status_frame,
            text="―――",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        )
        self.coords_label.pack(side="left", expand=True)

        # Stats - right with glow effect
        self.stats_label = ctk.CTkLabel(
            status_frame,
            text="0",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['accent_cyan']
        )
        self.stats_label.pack(side="right", padx=12)
        
    def create_controls(self, parent):
        """Frutiger Aero controls - compact sliders and settings"""
        controls_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        controls_frame.pack(fill="both", expand=True, padx=10, pady=6)
        
        # Sliders section
        self.create_compact_sliders(controls_frame)
        
        # Quick settings row
        self.create_quick_settings(controls_frame)
        
        # Profile management
        self.create_profile_section(controls_frame)
    
    def create_profile_section(self, parent):
        """Compact profile management"""
        profile_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            height=38,
            border_width=1,
            border_color=COLORS['border']
        )
        profile_frame.pack(fill="x", pady=(5, 0))
        profile_frame.pack_propagate(False)

        # Profile dropdown
        self.profile_var = ctk.StringVar(value="Profile")
        self.profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            variable=self.profile_var,
            values=["Profile"] + self.profile_manager.get_profile_names(),
            width=140,
            height=28,
            corner_radius=8,
            fg_color=COLORS['bg_primary'],
            button_color=COLORS['accent_blue'],
            button_hover_color=COLORS['accent_cyan'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_hover_color=COLORS['accent_blue'],
            text_color=COLORS['text_primary'],
            font=("Segoe UI", 9)
        )
        self.profile_menu.pack(side="left", padx=8, pady=5)

        # Mini buttons
        btn_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=8)
        
        for text, cmd, color in [("Load", self.load_selected_profile, COLORS['accent_blue']),
                                  ("Save", self.save_profile, COLORS['accent_green']),
                                  ("Del", self.delete_profile, "#FF4757")]:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                width=50,
                height=26,
                corner_radius=6,
                fg_color=color,
                hover_color=color,
                font=("Segoe UI", 9, "bold"),
                command=cmd
            )
            btn.pack(side="left", padx=2)

    def create_compact_sliders(self, parent):
        """Compact Frutiger Aero sliders"""
        sliders_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        sliders_frame.pack(fill="x", pady=(0, 5))

        self.clicks_slider, self.clicks_label = self.create_aero_slider(
            sliders_frame, "Clicks", 1, 100, 24,
            lambda v: setattr(self.clicker.config, 'clicks', int(v))
        )
        self.interval_slider, self.interval_label = self.create_aero_slider(
            sliders_frame, "Speed", 1, 200, 10,
            lambda v: setattr(self.clicker.config, 'interval', int(v))
        )
        self.duration_slider, self.duration_label = self.create_aero_slider(
            sliders_frame, "Duration", 0.01, 2.0, 0.30,
            lambda v: setattr(self.clicker.config, 'duration', float(v))
        )
        self.delay_slider, self.delay_label = self.create_aero_slider(
            sliders_frame, "Delay", 0.0, 1.0, 0.0,
            lambda v: setattr(self.clicker.config, 'auto_burst_delay', float(v))
        )

    def create_aero_slider(self, parent, label, from_, to, initial, command):
        """Frutiger Aero styled compact slider"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=2, padx=8)
        
        # Label row
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            font=("Segoe UI", 9),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        value_label = ctk.CTkLabel(
            label_frame,
            text=str(initial),
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS['accent_cyan']
        )
        value_label.pack(side="right")
        
        # Slider with glow effect
        slider = ctk.CTkSlider(
            frame,
            from_=from_,
            to=to,
            number_of_steps=(to - from_) * (100 if from_ < 1 else 1),
            height=14,
            button_color=COLORS['accent_cyan'],
            button_hover_color=COLORS['glow'],
            progress_color=COLORS['accent_blue'],
            fg_color=COLORS['bg_primary'],
            command=lambda v: self.update_aero_slider(value_label, v, command, from_ < 1)
        )
        slider.set(initial)
        slider.pack(fill="x", pady=(2, 0))
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
        settings_frame.pack(fill="x", pady=(0, 5))
        
        # Type and Button in one row
        row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=6)
        
        # Click type
        type_frame = ctk.CTkFrame(row, fg_color="transparent")
        type_frame.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkLabel(
            type_frame,
            text="Type",
            font=("Segoe UI", 9),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        self.type_selector = ctk.CTkSegmentedButton(
            type_frame,
            values=["Single", "Double", "Triple"],
            command=lambda v: setattr(self.clicker.config, 'click_type', v.lower()),
            font=("Segoe UI", 9, "bold"),
            corner_radius=6,
            fg_color=COLORS['bg_primary'],
            selected_color=COLORS['accent_blue'],
            selected_hover_color=COLORS['accent_cyan'],
            unselected_color=COLORS['bg_primary'],
            unselected_hover_color=COLORS['border']
        )
        self.type_selector.pack(fill="x", pady=(2, 0))
        self.type_selector.set("Single")
        
        # Mouse button
        button_frame = ctk.CTkFrame(row, fg_color="transparent")
        button_frame.pack(side="right", fill="x", expand=True, padx=(4, 0))
        
        ctk.CTkLabel(
            button_frame,
            text="Button",
            font=("Segoe UI", 9),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        self.button_selector = ctk.CTkSegmentedButton(
            button_frame,
            values=["Left", "Right", "Mid"],
            command=lambda v: setattr(self.clicker.config, 'mouse_button', {'Left': 'left', 'Right': 'right', 'Mid': 'middle'}[v]),
            font=("Segoe UI", 9, "bold"),
            corner_radius=6,
            fg_color=COLORS['bg_primary'],
            selected_color=COLORS['accent_blue'],
            selected_hover_color=COLORS['accent_cyan'],
            unselected_color=COLORS['bg_primary'],
            unselected_hover_color=COLORS['border']
        )
        self.button_selector.pack(fill="x", pady=(2, 0))
        self.button_selector.set("Left")
        
        # Options row
        options_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        options_row.pack(fill="x", padx=8, pady=(0, 6))
        
        self.humanize_checkbox = ctk.CTkCheckBox(
            options_row,
            text="Humanize",
            font=("Segoe UI", 9),
            command=self.toggle_humanization,
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=4,
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_blue'],
            hover_color=COLORS['accent_cyan']
        )
        self.humanize_checkbox.pack(side="left")
        
        self.advanced_checkbox = ctk.CTkCheckBox(
            options_row,
            text="Burst Var",
            font=("Segoe UI", 9),
            command=self.toggle_advanced_timing,
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=4,
            text_color=COLORS['text_secondary'],
            fg_color=COLORS['accent_green'],
            hover_color=COLORS['accent_green']
        )
        self.advanced_checkbox.pack(side="right")

    def create_action_buttons(self, parent):
        """Frutiger Aero action button - single auto-burst button"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(0, 6))
        
        # Single auto-burst button
        self.autoburst_button = ctk.CTkButton(
            buttons_frame,
            text="AUTO-BURST",
            height=44,
            corner_radius=12,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['accent_blue'],
            border_width=2,
            border_color=COLORS['border'],
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text_primary'],
            command=self.toggle_auto_burst
        )
        self.autoburst_button.pack(fill="x")

    def create_footer(self, parent):
        """Minimalist Frutiger Aero footer"""
        footer = ctk.CTkFrame(parent, fg_color="transparent", height=32)
        footer.pack(fill="x", padx=10, pady=(0, 6))
        footer.pack_propagate(False)
        
        ctk.CTkLabel(
            footer,
            text="F2: Burst  •  F3: Capture  •  F5: Auto",
            font=("Segoe UI", 10),
            text_color=COLORS['text_secondary']
        ).pack(side="bottom")

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



    def handle_callback(self, event):
        # Don't schedule callbacks if window is closing
        if self._is_closing:
            return

        if event == 'burst_started':
            self._safe_after(0, self.set_burst_state, True)
        elif event == 'burst_stopped':
            self._safe_after(0, self.set_burst_state, False)
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
        
    def sync_auto_burst_state(self):
        self.autoburst_button.configure(
            fg_color=COLORS['accent_green'] if self.clicker.config.auto_burst_enabled else COLORS['bg_card']
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
            
        self.sync_auto_burst_state()

    def save_current_config_on_exit(self):
        pass
        
    def update_license_info(self):
        pass
        
    def start_license_monitor(self):
        pass

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
