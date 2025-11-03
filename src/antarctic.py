import ctypes
import time
import threading
import random
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
        # Configuracion principal del autoclicker
        self.clicks = 1  # Limitador: Clics a realizar
        self.interval = 1  # Intervalo: Tiempo entre cada clic (en ms)
        self.multiplier = 1  # Multiplicador: Cantidad de clics por grupo
        self.delay = 0  # Delay: Retraso inicial (en ms)
        self.click_pattern = ""  # Patron de clics (ej: "3,2,1") - opcional
        
        # Configuraciones internas necesarias
        self.mouse_button = 'left'
        self.input_method = 'postmessage'
        self.auto_burst_enabled = False

    def to_dict(self):
        data = {}
        for k, v in self.__dict__.items():
            data[k] = v
        return data

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                # Type conversion for boolean fields
                boolean_fields = ['auto_burst_enabled']
                if key in boolean_fields:
                    value = bool(value)
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

    def validate(self, skip_network=False):
        return self.auth_client.validate(skip_network=skip_network)

    def get_license_info(self):
        """Get license information for display"""
        return self.auth_client.get_license_info()

    def get_time_remaining(self):
        """Get time remaining on license"""
        return self.auth_client.get_time_remaining()

    def get_expiration_date(self):
        """Get expiration date"""
        return self.auth_client.get_expiration_date()

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
        self.f1_continuous_active = False
        self.f1_continuous_thread = None

        # Timing monitoring
        self.last_delay_ms = 0.0

        # Advanced timing system components
        self.threading_optimizer = ThreadingOptimizer()

        # Latency compensation system
        self.latency_compensator = LatencyCompensator(callback=self._latency_callback)

    def _latency_callback(self, event_type, data):
        """Callback para eventos del compensador de latencia"""
        if self.gui_callback:
            self.gui_callback('latency_event', {'type': event_type, 'data': data})

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
        # Intervalo: Tiempo entre cada clic (en ms, convertir a segundos)
        base_delay = self.config.interval / 1000.0

        # Asegurar delay minimo y almacenar para monitoreo
        final_delay = max(0.0001, base_delay)  # Minimo 0.1ms
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

    def execute_burst(self, initial_delay=None):
        if not self.is_connected or not self.target_hwnd or not self.target_x or not self.target_y:
            return

        # Aplicar delay inicial si se especifica
        if initial_delay is not None and initial_delay > 0:
            time.sleep(initial_delay / 1000.0)  # Convertir ms a segundos

        with self.burst_lock:
            self.active_bursts += 1
            if self.active_bursts == 1 and self.gui_callback:
                self.gui_callback('burst_started')

        # Optimizacion de threading
        current_thread = kernel32.GetCurrentThread()
        priority = THREAD_PRIORITY_ABOVE_NORMAL
        kernel32.SetThreadPriority(current_thread, priority)

        try:
            # === MINIMIZAR SYSTEM CALLS: Pre-cachear todo antes del loop ===
            
            # Cachear posiciones y ventana
            client_x, client_y = self.screen_to_client(self.target_hwnd, self.target_x, self.target_y)
            self._precalculate_click_params(client_x, client_y)
            
            # Cachear configuracion en variables locales (evita acceso a atributos)
            hwnd = self.target_hwnd
            total_clicks_limit = self.config.clicks
            
            # Verificar ventana UNA SOLA VEZ (no en cada iteracion)
            if not self.check_window_valid(hwnd):
                return

            # Pre-cachear mensajes de Windows (evita lookups repetidos)
            msg_down = self._msg_down
            msg_up = self._msg_up
            wparam = self._wparam
            lparam = self._lparam
            lparam_up = self._lparam_up
            
            # Cachear funciones (evita lookups de metodos)
            send_message = user32.SendMessageW
            sleep = time.sleep
            get_delay = self.get_timing_delay
            
            # Configuracion de burst
            clicks_sent = 0
            stats_update_interval = 10
            
            # Determinar patron de clics y pre-cachearlo
            click_pattern = []
            if self.config.click_pattern and self.config.click_pattern.strip():
                try:
                    click_pattern = [int(x.strip()) for x in self.config.click_pattern.split(',') if x.strip()]
                except:
                    click_pattern = []
            
            if not click_pattern:
                click_pattern = [self.config.multiplier]
            
            pattern_len = len(click_pattern)
            pattern_index = 0

            # === LOOP OPTIMIZADO: Solo llamadas estrictamente necesarias ===
            while clicks_sent < total_clicks_limit and self.running:
                # Determinar cuantos clics enviar en este grupo
                clicks_in_group = click_pattern[pattern_index % pattern_len]
                clicks_in_group = min(clicks_in_group, total_clicks_limit - clicks_sent)
                
                # Enviar el grupo de clics (minimas system calls)
                for i in range(clicks_in_group):
                    if not self.running:
                        break

                    # System calls minimas: solo enviar mensajes
                    send_message(hwnd, msg_down, wparam, lparam)
                    send_message(hwnd, msg_up, 0, lparam_up)

                    # Actualizar contadores (sin system calls)
                    self.total_clicks_sent += 1
                    self.current_burst_clicks += 1
                    clicks_sent += 1

                pattern_index += 1

                # Delay entre grupos (solo si es necesario)
                if clicks_sent < total_clicks_limit:
                    delay = get_delay()
                    if delay > 0:
                        sleep(delay)

                # Stats update (reducido, evita spam de callbacks)
                if clicks_sent % stats_update_interval == 0 and self.gui_callback:
                    self.gui_callback('stats_update')

            # Stats final
            if self.gui_callback:
                self.gui_callback('stats_update')
        finally:
            # Restaurar prioridad normal
            current_thread = kernel32.GetCurrentThread()
            kernel32.SetThreadPriority(current_thread, THREAD_PRIORITY_NORMAL)

            with self.burst_lock:
                self.active_bursts -= 1
                if self.active_bursts == 0 and self.gui_callback:
                    self.gui_callback('burst_stopped')

    def execute_continuous_burst(self):
        """
        Ejecuta clicks continuamente mientras F1 esté presionado.
        Ignora el límite de clicks configurado.
        """
        if not self.is_connected or not self.target_hwnd or not self.target_x or not self.target_y:
            return

        with self.burst_lock:
            self.active_bursts += 1
            if self.active_bursts == 1 and self.gui_callback:
                self.gui_callback('burst_started')

        # Optimización de threading
        current_thread = kernel32.GetCurrentThread()
        priority = THREAD_PRIORITY_ABOVE_NORMAL
        kernel32.SetThreadPriority(current_thread, priority)

        try:
            # === MINIMIZAR SYSTEM CALLS: Pre-cachear todo antes del loop ===
            
            # Cachear posiciones y ventana
            client_x, client_y = self.screen_to_client(self.target_hwnd, self.target_x, self.target_y)
            self._precalculate_click_params(client_x, client_y)
            
            # Cachear configuración en variables locales (evita acceso a atributos)
            hwnd = self.target_hwnd
            
            # Verificar ventana UNA SOLA VEZ (no en cada iteración)
            if not self.check_window_valid(hwnd):
                return

            # Pre-cachear mensajes de Windows (evita lookups repetidos)
            msg_down = self._msg_down
            msg_up = self._msg_up
            wparam = self._wparam
            lparam = self._lparam
            lparam_up = self._lparam_up
            
            # Cachear funciones (evita lookups de métodos)
            send_message = user32.SendMessageW
            sleep = time.sleep
            get_delay = self.get_timing_delay
            
            # Configuración de burst
            clicks_sent = 0
            stats_update_interval = 10
            
            # Determinar patrón de clics y pre-cachearlo
            click_pattern = []
            if self.config.click_pattern and self.config.click_pattern.strip():
                try:
                    click_pattern = [int(x.strip()) for x in self.config.click_pattern.split(',') if x.strip()]
                except:
                    click_pattern = []
            
            if not click_pattern:
                click_pattern = [self.config.multiplier]
            
            pattern_len = len(click_pattern)
            pattern_index = 0

            # === LOOP CONTINUO: Sin límite de clicks, solo se detiene cuando F1 se suelta ===
            while self.f1_continuous_active and self.running:
                # Determinar cuantos clics enviar en este grupo
                clicks_in_group = click_pattern[pattern_index % pattern_len]
                
                # Enviar el grupo de clics (mínimas system calls)
                for i in range(clicks_in_group):
                    if not self.f1_continuous_active or not self.running:
                        break

                    # System calls mínimas: solo enviar mensajes
                    send_message(hwnd, msg_down, wparam, lparam)
                    send_message(hwnd, msg_up, 0, lparam_up)

                    # Actualizar contadores (sin system calls)
                    self.total_clicks_sent += 1
                    self.current_burst_clicks += 1
                    clicks_sent += 1
                    
                    # Delay después de cada clic individual (respetar interval)
                    if i < clicks_in_group - 1 or self.f1_continuous_active:
                        delay = get_delay()
                        if delay > 0:
                            sleep(delay)

                pattern_index += 1

                # Stats update (reducido, evita spam de callbacks)
                if clicks_sent % stats_update_interval == 0 and self.gui_callback:
                    self.gui_callback('stats_update')

            # Stats final
            if self.gui_callback:
                self.gui_callback('stats_update')
        finally:
            # Restaurar prioridad normal
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
        f1_pressed = False
        f2_pressed = False
        f3_pressed = False
        f5_pressed = False
        lbutton_pressed = False
        while self.running:
            # F1: Modo continuo (mantener presionado = autoclick infinito)
            if self.is_key_pressed(VK_F1):
                if not f1_pressed:
                    # Activar modo continuo
                    self.f1_continuous_active = True
                    # Iniciar thread de burst continuo
                    self.f1_continuous_thread = threading.Thread(
                        target=self.execute_continuous_burst, 
                        daemon=True
                    )
                    self.f1_continuous_thread.start()
                    f1_pressed = True
            else:
                # Cuando se suelta F1, desactivar modo continuo
                if f1_pressed:
                    self.f1_continuous_active = False
                    f1_pressed = False
            
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
                            args=(self.config.delay,),
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
        self.geometry("400x620")  # Tamaño optimizado
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

        self.setup_ui()
        self.clicker.start()
        self.load_last_profile()

        # Start background license validation (every 5 minutes)
        self.start_license_validation()

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

        # Profile management (always visible)
        self.create_profile_section(controls_frame)

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
        """Settings section with numeric inputs"""
        # Main container
        self.sliders_section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        self.sliders_section.pack(fill="x", pady=(0, 8))

        # Header
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
        ToolTip(help_label, "Limitador, Intervalo, Multiplicador y Delay del autoclicker")

        # Content frame
        self.sliders_content = ctk.CTkFrame(self.sliders_section, fg_color="transparent")
        self.sliders_content.pack(fill="x", padx=12, pady=(0, 12))

        # Create numeric inputs
        self.clicks_entry = self.create_numeric_input(
            self.sliders_content, "Limitador (Clics)", 1, 1, 1000,
            lambda v: self.update_config('clicks', v, int)
        )
        self.interval_entry = self.create_numeric_input(
            self.sliders_content, "Intervalo (ms)", 1, 0.1, 1000,
            lambda v: self.update_config('interval', v, float)
        )
        self.multiplier_entry = self.create_numeric_input(
            self.sliders_content, "Multiplicador", 1, 1, 100,
            lambda v: self.update_config('multiplier', v, int)
        )
        self.delay_entry = self.create_numeric_input(
            self.sliders_content, "Delay (ms)", 0, 0, 300,
            lambda v: self.update_config('delay', v, int)
        )
        
        # Patron de clics (opcional)
        self.pattern_entry = self.create_pattern_input(
            self.sliders_content, "Patrón (opcional)", ""
        )

    def create_numeric_input(self, parent, label_text, default_value, min_val, max_val, callback):
        """Create a numeric input with +/- buttons"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=6)
        
        # Label
        label_frame = ctk.CTkFrame(container, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        ).pack(side="left")
        
        # Control frame (entry + buttons)
        control_frame = ctk.CTkFrame(container, fg_color="transparent")
        control_frame.pack(side="right")
        
        # Decrease button
        decrease_btn = ctk.CTkButton(
            control_frame,
            text="-",
            width=32,
            height=32,
            font=("Segoe UI", 16, "bold"),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent_blue'],
            text_color=COLORS['text_primary'],
            corner_radius=8,
            command=lambda: self.adjust_numeric_value(entry, -1, min_val, max_val, callback, isinstance(default_value, float))
        )
        decrease_btn.pack(side="left", padx=(0, 4))
        
        # Entry field
        entry = ctk.CTkEntry(
            control_frame,
            width=80,
            height=32,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['accent_blue'],
            border_width=2,
            text_color=COLORS['text_primary'],
            justify="center"
        )
        entry.pack(side="left", padx=4)
        entry.insert(0, str(default_value))
        
        # Bind events
        entry.bind("<Return>", lambda e: self.validate_numeric_input(entry, min_val, max_val, callback, isinstance(default_value, float)))
        entry.bind("<FocusOut>", lambda e: self.validate_numeric_input(entry, min_val, max_val, callback, isinstance(default_value, float)))
        
        # Increase button
        increase_btn = ctk.CTkButton(
            control_frame,
            text="+",
            width=32,
            height=32,
            font=("Segoe UI", 16, "bold"),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent_blue'],
            text_color=COLORS['text_primary'],
            corner_radius=8,
            command=lambda: self.adjust_numeric_value(entry, 1, min_val, max_val, callback, isinstance(default_value, float))
        )
        increase_btn.pack(side="left", padx=(4, 0))
        
        return entry
    
    def adjust_numeric_value(self, entry, delta, min_val, max_val, callback, is_float):
        """Adjust numeric value by delta"""
        try:
            current = float(entry.get()) if is_float else int(entry.get())
            
            # Determine step size
            if is_float:
                step = 0.1 if current < 10 else 1.0
            else:
                step = 1
            
            new_value = current + (delta * step)
            new_value = max(min_val, min(max_val, new_value))
            
            if is_float:
                entry.delete(0, "end")
                entry.insert(0, f"{new_value:.1f}")
            else:
                entry.delete(0, "end")
                entry.insert(0, str(int(new_value)))
            
            callback(new_value)
        except ValueError:
            pass
    
    def validate_numeric_input(self, entry, min_val, max_val, callback, is_float):
        """Validate and apply numeric input"""
        try:
            value = float(entry.get()) if is_float else int(entry.get())
            value = max(min_val, min(max_val, value))
            
            if is_float:
                entry.delete(0, "end")
                entry.insert(0, f"{value:.1f}")
            else:
                entry.delete(0, "end")
                entry.insert(0, str(int(value)))
            
            callback(value)
        except ValueError:
            # Reset to current config value
            if is_float:
                entry.delete(0, "end")
                entry.insert(0, f"{min_val:.1f}")
            else:
                entry.delete(0, "end")
                entry.insert(0, str(int(min_val)))
    
    def create_pattern_input(self, parent, label_text, default_value):
        """Create a text input for click pattern"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=6)
        
        # Label with help icon
        label_frame = ctk.CTkFrame(container, fg_color="transparent")
        label_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        ).pack(side="left")
        
        # Help icon
        help_icon = ctk.CTkLabel(
            label_frame,
            text="?",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim'],
            width=14
        )
        help_icon.pack(side="left", padx=(4, 0))
        ToolTip(help_icon, "Patrón de clics: ej. '3,2,1' = 3 clics, pausa, 2 clics, pausa, 1 clic.\nSi está vacío, usa el Multiplicador normal.")
        
        # Right side frame for entry and button
        right_frame = ctk.CTkFrame(container, fg_color="transparent")
        right_frame.pack(side="right")
        
        # Random pattern button
        random_btn = ctk.CTkButton(
            right_frame,
            text="🎲",
            width=32,
            height=32,
            font=("Segoe UI", 14),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent_blue'],
            text_color=COLORS['text_primary'],
            corner_radius=8,
            command=lambda: self.generate_random_pattern(entry)
        )
        random_btn.pack(side="left", padx=(0, 4))
        ToolTip(random_btn, "Generar patrón aleatorio eficaz")
        
        # Entry field
        entry = ctk.CTkEntry(
            right_frame,
            width=150,
            height=32,
            font=("Segoe UI", 11),
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['accent_blue'],
            border_width=2,
            text_color=COLORS['text_primary'],
            placeholder_text="ej: 3,2,1",
            justify="center"
        )
        entry.pack(side="left")
        entry.insert(0, default_value)
        
        # Bind events
        entry.bind("<Return>", lambda e: self.validate_pattern_input(entry))
        entry.bind("<FocusOut>", lambda e: self.validate_pattern_input(entry))
        
        return entry
    
    def generate_random_pattern(self, entry):
        """Generate a random but effective click pattern"""
        # Pattern length: 6-10 groups (balanced)
        pattern_length = random.randint(6, 10)
        
        # Click values pool with weighted distribution
        # More 1s and 2s (70%), fewer 3s and 4s (30%)
        click_values = [1, 1, 1, 2, 2, 2, 3, 4]
        
        pattern = []
        last_value = None
        consecutive_count = 0
        
        for i in range(pattern_length):
            # Get a random value
            value = random.choice(click_values)
            
            # Avoid more than 2 consecutive identical values (more natural)
            if value == last_value:
                consecutive_count += 1
                if consecutive_count >= 2:
                    # Force different value
                    available = [v for v in click_values if v != last_value]
                    value = random.choice(available)
                    consecutive_count = 0
            else:
                consecutive_count = 0
            
            pattern.append(value)
            last_value = value
        
        # Convert to string format
        pattern_str = ','.join(map(str, pattern))
        
        # Update entry field
        entry.delete(0, "end")
        entry.insert(0, pattern_str)
        
        # Validate and apply
        self.validate_pattern_input(entry)
        
        # Show brief feedback
        if hasattr(self, 'status_label'):
            original_text = self.status_label.cget("text")
            self.status_label.configure(text=f"Patrón generado: {pattern_str}")
            # Restore original text after 2 seconds
            self.after(2000, lambda: self.status_label.configure(text=original_text))
    
    def validate_pattern_input(self, entry):
        """Validate and apply pattern input"""
        pattern = entry.get().strip()
        
        # Empty is valid (uses multiplier instead)
        if not pattern:
            self.clicker.config.click_pattern = ""
            return
        
        # Validate format: only numbers and commas
        import re
        if not re.match(r'^[\d,\s]+$', pattern):
            entry.delete(0, "end")
            entry.insert(0, "")
            self.clicker.config.click_pattern = ""
            return
        
        # Parse and validate numbers
        try:
            numbers = [int(x.strip()) for x in pattern.split(',') if x.strip()]
            if not numbers or any(n <= 0 for n in numbers):
                entry.delete(0, "end")
                entry.insert(0, "")
                self.clicker.config.click_pattern = ""
                return
            
            # Valid pattern
            clean_pattern = ','.join(map(str, numbers))
            entry.delete(0, "end")
            entry.insert(0, clean_pattern)
            self.clicker.config.click_pattern = clean_pattern
        except:
            entry.delete(0, "end")
            entry.insert(0, "")
            self.clicker.config.click_pattern = ""
    
    def update_config(self, attr, value, type_conv):
        """Update config attribute with type conversion"""
        setattr(self.clicker.config, attr, type_conv(value))

    def resize_window(self):
        """Dynamically resize window based on open sections"""
        base_height = 620
        self.geometry(f"400x{base_height}")

    def toggle_sliders_section(self):
        pass

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
        """Footer with license info"""
        footer = ctk.CTkFrame(parent, fg_color="transparent", height=40)
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

        # Update license info
        self.update_license_display()

    def toggle_humanization(self):
        pass



    def toggle_auto_burst(self):
        self.clicker.config.auto_burst_enabled = not self.clicker.config.auto_burst_enabled
        self.sync_auto_burst_state()

    def toggle_advanced_timing(self):
        pass

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
        pass

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
        # Skip if timing monitor doesn't exist
        if not hasattr(self, 'timing_monitor_label'):
            return
            
        if self.clicker.active_bursts == 0:
            self.timing_monitor_label.configure(text="Monitor: Ready")
            return

        # Build monitor string
        parts = []

        # Show current delay
        parts.append(f"Delay:{self.clicker.last_delay_ms:.1f}ms")

        # Mostrar informacion basica del timing

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
        # Update numeric inputs
        self.clicks_entry.delete(0, "end")
        self.clicks_entry.insert(0, str(self.clicker.config.clicks))
        
        self.interval_entry.delete(0, "end")
        self.interval_entry.insert(0, f"{self.clicker.config.interval:.1f}")
        
        self.multiplier_entry.delete(0, "end")
        self.multiplier_entry.insert(0, str(self.clicker.config.multiplier))
        
        self.delay_entry.delete(0, "end")
        self.delay_entry.insert(0, str(self.clicker.config.delay))
        
        # Update pattern input
        self.pattern_entry.delete(0, "end")
        self.pattern_entry.insert(0, self.clicker.config.click_pattern)

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
            expiration_date = self.key_manager.get_expiration_date()

            # Format the display text
            if expiration_date == "Lifetime":
                text = "License: Lifetime"
                self.license_label.configure(text_color=COLORS['text_secondary'])
            elif expiration_date == "Expired":
                text = "License: EXPIRED"
                self.license_label.configure(text_color=COLORS['accent_red'])
            elif expiration_date == "Unknown":
                text = "License: Unknown"
                self.license_label.configure(text_color=COLORS['text_secondary'])
            else:
                text = f"License expires: {expiration_date}"
                self.license_label.configure(text_color=COLORS['text_secondary'])

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
