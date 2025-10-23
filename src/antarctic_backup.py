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

# GUI Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Windows API handles
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Resource path helper
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
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
        self.geometry("450x280")
        self.resizable(False, False)

        try:
            icon_path = resource_path('icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass

        self.key_manager = KeyManager()
        self.activation_successful = False

        self.setup_ui()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        try:
            logo_path = resource_path('logo_compact.png')
            logo_img = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(350, 87))

            logo_label = ctk.CTkLabel(container, image=logo_ctk, text="")
            logo_label.pack(pady=(0, 25))
        except Exception as e:
            title = ctk.CTkLabel(container, text="A N T A R C T I C", font=("Consolas", 26, "bold"), text_color="#CC0000")
            title.pack(pady=(0, 2))
            subtitle = ctk.CTkLabel(container, text="━━━━━━ LICENSE ACTIVATION ━━━━━━", font=("Consolas", 9), text_color="#666666")
            subtitle.pack(pady=(0, 25))

        self.key_entry = ctk.CTkEntry(container, width=360, height=40, font=("Consolas", 11), placeholder_text="ANTARCTIC-XXXX-XXXX-XXXX", border_width=1, corner_radius=6, border_color="#CC0000")
        self.key_entry.pack(pady=(0, 8))
        self.key_entry.focus()

        self.status_label = ctk.CTkLabel(container, text="", font=("Arial", 9), text_color="#CC0000")
        self.status_label.pack(pady=8)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=15)

        activate_btn = ctk.CTkButton(btn_frame, text="ACTIVATE", width=160, height=36, font=("Arial", 11, "bold"), corner_radius=6, fg_color="#CC0000", hover_color="#990000", command=self.activate)
        activate_btn.pack(side="left", padx=5)

        exit_btn = ctk.CTkButton(btn_frame, text="EXIT", width=160, height=36, font=("Arial", 11), corner_radius=6, fg_color="#333333", hover_color="#222222", command=self.exit_app)
        exit_btn.pack(side="left", padx=5)

        self.key_entry.bind('<Return>', lambda e: self.activate())

    def activate(self):
        key = self.key_entry.get().strip()
        if not key:
            self.status_label.configure(text="Please enter a license key", text_color="#CC0000")
            return
        success, message = self.key_manager.activate(key)
        if success:
            self.status_label.configure(text="✓ Activation successful!", text_color="#00CC00")
            self.activation_successful = True
            self.after(1000, self.close_window)
        else:
            self.status_label.configure(text=f"✗ {message}", text_color="#CC0000")
            self.key_entry.delete(0, 'end')

    def close_window(self):
        self.destroy()

    def exit_app(self):
        self.destroy()

    def run(self):
        self.mainloop()
        return self.activation_successful


class AntarcticGUI(ctk.CTk):
    def __init__(self, key_manager):
        super().__init__()
        self.title("ANTARCTIC")
        self.geometry("480x780")  # Increased height to accommodate burst variations buttons
        self.resizable(False, False)

        try:
            icon_path = resource_path('icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass

        self.key_manager = key_manager
        self.clicker = AutoClicker(gui_callback=self.handle_callback)
        self.profile_manager = ProfileManager(max_profiles=5)

        self.setup_ui()
        self.clicker.start()
        self.load_last_profile()

    def setup_ui(self):
        self.configure(fg_color="#212121")
        self.create_header()
        self.create_status_bar()
        self.create_profile_bar()
        self.create_sliders()
        self.create_selectors()
        self.create_actions()
        self.create_footer()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_header(self):
        try:
            logo_path = resource_path('logo.png')
            logo_img = Image.open(logo_path)
            # Calculate aspect ratio to prevent stretching
            aspect_ratio = logo_img.width / logo_img.height
            target_width = 380  # Slightly smaller to fit better
            target_height = int(target_width / aspect_ratio)
            logo_img = logo_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(target_width, target_height))
            logo_label = ctk.CTkLabel(self, image=logo_ctk, text="")
            logo_label.pack(pady=(10, 0))
        except Exception as e:
            title = ctk.CTkLabel(self, text="A N T A R C T I C", font=("Consolas", 36, "bold"), text_color="#CC0000")
            title.pack(pady=(20, 0))
            subtitle = ctk.CTkLabel(self, text="ULTRA CLICKER", font=("Consolas", 12), text_color="#888888")
            subtitle.pack(pady=(0, 20))
    def create_status_bar(self):
        status_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8, height=45, border_width=1, border_color="#333333")
        status_frame.pack(fill="x", padx=15, pady=10)
        status_frame.pack_propagate(False)

        # Connection indicator with animated pulse effect ready
        self.conn_indicator = ctk.CTkLabel(status_frame, text="● OFFLINE", font=("Consolas", 10, "bold"), text_color="#CC0000")
        self.conn_indicator.pack(side="left", padx=(15, 10))

        # Burst indicator
        self.burst_indicator = ctk.CTkLabel(status_frame, text="▶ STANDBY", font=("Consolas", 10), text_color="#666666")
        self.burst_indicator.pack(side="left", padx=(10, 10))

        # Separator
        separator = ctk.CTkLabel(status_frame, text="│", font=("Consolas", 10), text_color="#333333")
        separator.pack(side="left", padx=(0, 10))

        # Coordinates label
        self.coords_label = ctk.CTkLabel(status_frame, text="[ --- , --- ]", font=("Consolas", 9), text_color="#666666")
        self.coords_label.pack(side="left", padx=(0, 0))

        # Stats label on right
        self.stats_label = ctk.CTkLabel(status_frame, text="T: 0  B: 0", font=("Consolas", 9, "bold"), text_color="#00CC00")
        self.stats_label.pack(side="right", padx=(10, 15))
        
    def create_profile_bar(self):
        profile_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=6, height=50)
        profile_frame.pack(fill="x", padx=15, pady=0)
        profile_frame.pack_propagate(False)

        ctk.CTkLabel(profile_frame, text="PROFILE:", font=("Consolas", 11, "bold"), text_color="#CCCCCC").pack(side="left", padx=15)

        self.profile_var = ctk.StringVar(value="Select")
        self.profile_menu = ctk.CTkOptionMenu(profile_frame, variable=self.profile_var, values=["Select"] + self.profile_manager.get_profile_names(), width=150, height=30, corner_radius=4, fg_color="#333333", button_color="#555555", button_hover_color="#777777", dropdown_fg_color="#333333", dropdown_hover_color="#444444", dropdown_text_color="#CCCCCC", font=("Consolas", 10))
        self.profile_menu.pack(side="left", padx=0)

        load_btn = ctk.CTkButton(profile_frame, text="LOAD", width=70, height=30, font=("Consolas", 10, "bold"), corner_radius=4, fg_color="#444444", hover_color="#555555", command=self.load_selected_profile)
        load_btn.pack(side="left", padx=6)

        save_btn = ctk.CTkButton(profile_frame, text="SAVE", width=70, height=30, font=("Consolas", 10, "bold"), corner_radius=4, fg_color="#CC0000", hover_color="#990000", command=self.save_profile)
        save_btn.pack(side="left", padx=0)

        del_btn = ctk.CTkButton(profile_frame, text="DEL", width=70, height=30, font=("Consolas", 10, "bold"), corner_radius=4, fg_color="#800000", hover_color="#660000", command=self.delete_profile)
        del_btn.pack(side="left", padx=6)

    def create_sliders(self):
        sliders_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=6)
        sliders_frame.pack(fill="x", padx=15, pady=10)

        self.clicks_slider, self.clicks_label = self.create_clean_slider(sliders_frame, "Clicks/Batch", 1, 100, 24, lambda v: setattr(self.clicker.config, 'clicks', int(v)))
        self.interval_slider, self.interval_label = self.create_clean_slider(sliders_frame, "Interval (ms)", 1, 200, 10, lambda v: setattr(self.clicker.config, 'interval', int(v)))
        self.duration_slider, self.duration_label = self.create_clean_slider(sliders_frame, "Duration (s)", 0.01, 2.0, 0.30, lambda v: setattr(self.clicker.config, 'duration', float(v)))
        self.delay_slider, self.delay_label = self.create_clean_slider(sliders_frame, "Auto-Burst Delay", 0.0, 1.0, 0.0, lambda v: setattr(self.clicker.config, 'auto_burst_delay', float(v)))

    def create_clean_slider(self, parent, label, from_, to, initial, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=15)
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x")
        ctk.CTkLabel(label_frame, text=label, font=("Consolas", 10), text_color="#CCCCCC").pack(side="left")
        value_label = ctk.CTkLabel(label_frame, text=str(initial), font=("Consolas", 10, "bold"), text_color="#CC0000")
        value_label.pack(side="right")
        slider = ctk.CTkSlider(frame, from_=from_, to=to, number_of_steps=(to - from_) * (100 if from_ < 1 else 1), height=12, button_color="#CC0000", button_hover_color="#990000", progress_color="#CC0000", fg_color="#444444", command=lambda v: self.update_clean_slider(value_label, v, command, from_ < 1))
        slider.set(initial)
        slider.pack(fill="x", pady=(0, 4))
        return slider, value_label

    def create_selectors(self):
        selectors_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=6)
        selectors_frame.pack(fill="x", padx=15, pady=0)

        # Type selector
        type_frame = ctk.CTkFrame(selectors_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(type_frame, text="Type", font=("Consolas", 10), text_color="#CCCCCC").pack(side="left", anchor="w")
        self.type_selector = ctk.CTkSegmentedButton(type_frame, values=["SINGLE", "DOUBLE", "TRIPLE"], command=lambda v: setattr(self.clicker.config, 'click_type', v.lower()), font=("Consolas", 10, "bold"), corner_radius=4, border_width=1, fg_color="#333333", selected_color="#CC0000", selected_hover_color="#990000", unselected_color="#333333", unselected_hover_color="#444444")
        self.type_selector.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self.type_selector.set("SINGLE")

        # Button selector
        button_frame = ctk.CTkFrame(selectors_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(5, 10))
        ctk.CTkLabel(button_frame, text="Button", font=("Consolas", 10), text_color="#CCCCCC").pack(side="left", anchor="w")
        self.button_selector = ctk.CTkSegmentedButton(button_frame, values=["LEFT", "RIGHT", "MIDDLE"], command=lambda v: setattr(self.clicker.config, 'mouse_button', v.lower()), font=("Consolas", 10, "bold"), corner_radius=4, border_width=1, fg_color="#333333", selected_color="#CC0000", selected_hover_color="#990000", unselected_color="#333333", unselected_hover_color="#444444")
        self.button_selector.pack(side="right", fill="x", expand=True, padx=(10, 0))
        self.button_selector.set("LEFT")

    def create_actions(self):
        # Store reference to actions frame for rebuilding
        if hasattr(self, 'actions_frame'):
            self.actions_frame.destroy()

        self.actions_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=6)
        self.actions_frame.pack(fill="x", padx=15, pady=10)

        humanize_frame = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        humanize_frame.pack(fill="x", padx=15, pady=(10, 5))
        self.humanize_checkbox = ctk.CTkCheckBox(humanize_frame, text="Humanization", font=("Consolas", 9), command=self.toggle_humanization, checkbox_width=18, checkbox_height=18, corner_radius=4, border_width=1, text_color="#CCCCCC", hover_color="#444444")
        self.humanize_checkbox.pack(side="left")

        # Advanced timing toggle (for burst variations) - simplified
        self.advanced_checkbox = ctk.CTkCheckBox(humanize_frame, text="Burst Variations", font=("Consolas", 9), command=self.toggle_advanced_timing, checkbox_width=18, checkbox_height=18, corner_radius=4, border_width=1, fg_color="#00CC00", hover_color="#009900", text_color="#CCCCCC")
        self.advanced_checkbox.pack(side="right")

        buttons_frame = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(5, 10))

        self.ultra_button = ctk.CTkButton(buttons_frame, text="ULTRA MODE", height=42, font=("Consolas", 11, "bold"), corner_radius=6, fg_color="#CC0000", hover_color="#AA0000", border_width=0, command=self.toggle_ultra_mode)
        self.ultra_button.pack(fill="x", pady=4)

        self.autoburst_button = ctk.CTkButton(buttons_frame, text="AUTO-BURST [F5]", height=42, font=("Consolas", 11, "bold"), corner_radius=6, fg_color="#444444", hover_color="#555555", border_width=0, command=self.toggle_auto_burst)
        self.autoburst_button.pack(fill="x", pady=4)

        self.random_button = ctk.CTkButton(buttons_frame, text="RANDOM CONFIG", height=42, font=("Consolas", 11, "bold"), corner_radius=6, fg_color="#444444", hover_color="#555555", border_width=0, command=self.randomize_config)
        self.random_button.pack(fill="x", pady=4)

        # Advanced burst variations section - REMOVED (simplified)
        # No longer needed since we auto-select the best profile

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        footer_frame.pack(side="bottom", fill="x", padx=15, pady=5)
        
        footer_label = ctk.CTkLabel(footer_frame, text="F3: CAPTURE  •  F2: BURST  •  F5: AUTO-BURST", font=("Consolas", 8), text_color="#555555")
        footer_label.pack()

    def toggle_humanization(self):
        self.clicker.config.humanize_enabled = bool(self.humanize_checkbox.get())

    def toggle_ultra_mode(self):
        self.clicker.config.ultra_mode = not self.clicker.config.ultra_mode
        self.ultra_button.configure(fg_color="#00CC00" if self.clicker.config.ultra_mode else "#CC0000")

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

    def randomize_config(self):
        self.clicks_slider.set(random.randint(10, 50))
        self.interval_slider.set(random.randint(5, 50))
        self.duration_slider.set(random.uniform(0.1, 1.0))
        self.delay_slider.set(random.uniform(0.0, 0.5))
        self.update_clean_slider(self.clicks_label, self.clicks_slider.get(), lambda v: setattr(self.clicker.config, 'clicks', int(v)), False)
        self.update_clean_slider(self.interval_label, self.interval_slider.get(), lambda v: setattr(self.clicker.config, 'interval', int(v)), False)
        self.update_clean_slider(self.duration_label, self.duration_slider.get(), lambda v: setattr(self.clicker.config, 'duration', float(v)), True)
        self.update_clean_slider(self.delay_label, self.delay_slider.get(), lambda v: setattr(self.clicker.config, 'auto_burst_delay', float(v)), True)

    def update_clean_slider(self, label, value, command, is_decimal):
        if is_decimal:
            val = round(float(value), 2)
            label.configure(text=f"{val:.2f}")
        else:
            val = int(value)
            label.configure(text=str(val))
        if command:
            command(val)

    def handle_callback(self, event):
        if event == 'burst_started':
            self.after(0, self.set_burst_state, True)
        elif event == 'burst_stopped':
            self.after(0, self.set_burst_state, False)
        elif event == 'coords_captured':
            self.after(0, self.update_coords)
        elif event == 'connection_changed':
            self.after(0, self.update_connection_status)
        elif event == 'stats_update':
            self.after(0, self.update_stats)
        elif event == 'auto_burst_toggled':
            self.after(0, self.sync_auto_burst_state)

    def set_burst_state(self, bursting):
        if bursting:
            self.burst_indicator.configure(text="▶▶ BURSTING", text_color="#FF9900")
            # Reset burst clicks counter when starting a new burst
            self.clicker.current_burst_clicks = 0
        else:
            self.burst_indicator.configure(text="▶ STANDBY", text_color="#888888")
            # Save last burst count before resetting
            self.clicker.last_burst_clicks = self.clicker.current_burst_clicks
            # Reset current burst counter after delay
            self.after(3000, lambda: setattr(self.clicker, 'current_burst_clicks', 0))
        # Update stats immediately
        self.update_stats()

    def update_coords(self):
        x, y = self.clicker.target_x, self.clicker.target_y
        self.coords_label.configure(text=f"[ {x:04d} , {y:04d} ]", text_color="#00CC00")

    def update_connection_status(self):
        if self.clicker.is_connected:
            self.conn_indicator.configure(text="● ONLINE", text_color="#00CC00")
        else:
            self.conn_indicator.configure(text="● OFFLINE", text_color="#CC0000")
            
    def update_stats(self):
        # Update the stats label with total clicks and current/last burst clicks
        total_clicks = self.clicker.total_clicks_sent
        # Show current burst if bursting, otherwise show last burst
        if self.clicker.active_bursts > 0:
            burst_clicks = self.clicker.current_burst_clicks
            # Animated color during burst
            self.stats_label.configure(text=f"T: {total_clicks}  B: {burst_clicks}", text_color="#FF9900")
        else:
            burst_clicks = self.clicker.last_burst_clicks if self.clicker.last_burst_clicks > 0 else self.clicker.current_burst_clicks
            self.stats_label.configure(text=f"T: {total_clicks}  B: {burst_clicks}", text_color="#00CC00")
        
    def sync_auto_burst_state(self):
        self.autoburst_button.configure(fg_color="#00CC00" if self.clicker.config.auto_burst_enabled else "#444444")

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
        if profile_name and profile_name != "Select":
            success, config_data = self.profile_manager.load_profile(profile_name)
            if success:
                self.clicker.config.from_dict(config_data)
                self.sync_ui_with_config()

    def delete_profile(self):
        profile_name = self.profile_var.get()
        if profile_name and profile_name != "Select":
            if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{profile_name}'?"):
                success, message = self.profile_manager.delete_profile(profile_name)
                if success:
                    self.update_profile_menu()
                    self.profile_var.set("Select")

    def update_profile_menu(self):
        self.profile_menu.configure(values=["Select"] + self.profile_manager.get_profile_names())

    def sync_ui_with_config(self):
        self.clicks_slider.set(self.clicker.config.clicks)
        self.interval_slider.set(self.clicker.config.interval)
        self.duration_slider.set(self.clicker.config.duration)
        self.delay_slider.set(self.clicker.config.auto_burst_delay)
        self.update_clean_slider(self.clicks_label, self.clicker.config.clicks, lambda v: setattr(self.clicker.config, 'clicks', int(v)), False)
        self.update_clean_slider(self.interval_label, self.clicker.config.interval, lambda v: setattr(self.clicker.config, 'interval', int(v)), False)
        self.update_clean_slider(self.duration_label, self.clicker.config.duration, lambda v: setattr(self.clicker.config, 'duration', float(v)), True)
        self.update_clean_slider(self.delay_label, self.clicker.config.auto_burst_delay, lambda v: setattr(self.clicker.config, 'auto_burst_delay', float(v)), True)
        self.type_selector.set(self.clicker.config.click_type.upper())
        self.button_selector.set(self.clicker.config.mouse_button.upper())
        self.humanize_checkbox.select() if self.clicker.config.humanize_enabled else self.humanize_checkbox.deselect()
        self.ultra_button.configure(fg_color="#00CC00" if self.clicker.config.ultra_mode else "#CC0000")
        self.sync_auto_burst_state()

    def save_current_config_on_exit(self):
        pass
        
    def update_license_info(self):
        pass
        
    def start_license_monitor(self):
        pass

    def on_close(self):
        self.destroy()
        
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
