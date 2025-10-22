"""
Antarctic Security Module
Anti-debugging, anti-tampering, and security checks
"""

import ctypes
import sys
import os
import threading
import time
import hashlib

class SecurityGuard:
    def __init__(self):
        self.is_running = True
        self.violations = 0

    def check_debugger(self):
        """Detect if running under a debugger"""
        try:
            # Windows API check
            if sys.platform == 'win32':
                kernel32 = ctypes.windll.kernel32
                if kernel32.IsDebuggerPresent():
                    return True

                # NtQueryInformationProcess check
                try:
                    ntdll = ctypes.windll.ntdll
                    process_debug_port = 0x7
                    debug_port = ctypes.c_ulong()
                    result = ntdll.NtQueryInformationProcess(
                        kernel32.GetCurrentProcess(),
                        process_debug_port,
                        ctypes.byref(debug_port),
                        ctypes.sizeof(debug_port),
                        None
                    )
                    if result == 0 and debug_port.value != 0:
                        return True
                except:
                    pass
        except:
            pass
        return False

    def check_vm(self):
        """Detect if running in a virtual machine (basic check)"""
        try:
            # Check for common VM artifacts
            if sys.platform == 'win32':
                import subprocess
                # Check BIOS
                result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=5)
                output = result.stdout.lower()

                vm_indicators = ['vmware', 'virtualbox', 'qemu', 'virtual', 'hyper-v']
                for indicator in vm_indicators:
                    if indicator in output:
                        return True
        except:
            pass
        return False

    def check_tools(self):
        """Detect common reverse engineering tools"""
        try:
            import psutil
            suspicious_processes = [
                'ida.exe', 'ida64.exe', 'ollydbg.exe', 'x64dbg.exe', 'x32dbg.exe',
                'windbg.exe', 'processhacker.exe', 'procmon.exe', 'procmon64.exe',
                'wireshark.exe', 'fiddler.exe', 'pestudio.exe', 'dnspy.exe'
            ]

            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in suspicious_processes:
                        return True
                except:
                    pass
        except:
            pass
        return False

    def check_integrity(self):
        """Check if the executable has been modified"""
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                # Simple size check (can be enhanced)
                size = os.path.getsize(exe_path)
                # Check if size is suspiciously small (tampered)
                if size < 1000000:  # Less than 1MB is suspicious for packed PyInstaller
                    return False
        except:
            pass
        return True

    def monitor_continuous(self, exit_callback=None):
        """Continuously monitor for security violations"""
        while self.is_running:
            try:
                # Check every 30 seconds
                time.sleep(30)

                if not self.is_running:
                    break

                # Run security checks
                if self.check_debugger():
                    self.violations += 1
                    if self.violations >= 2 and exit_callback:
                        exit_callback()
                        break

                if self.check_tools():
                    self.violations += 1
                    if self.violations >= 2 and exit_callback:
                        exit_callback()
                        break

            except:
                pass

    def start_monitoring(self, exit_callback=None):
        """Start background security monitoring"""
        monitor_thread = threading.Thread(
            target=self.monitor_continuous,
            args=(exit_callback,),
            daemon=True
        )
        monitor_thread.start()

    def stop_monitoring(self):
        """Stop security monitoring"""
        self.is_running = False

    def perform_initial_checks(self):
        """Perform all security checks at startup"""
        # Check debugger
        if self.check_debugger():
            return False, "Security violation detected (001)"

        # Check VM (warning only, don't block)
        if self.check_vm():
            # VM detection - allow but log
            pass

        # Check integrity
        if not self.check_integrity():
            return False, "Security violation detected (002)"

        # Check for RE tools
        if self.check_tools():
            return False, "Security violation detected (003)"

        return True, "Security checks passed"


def obfuscate_string(s):
    """Simple string obfuscation for URLs and sensitive data"""
    # XOR with a key
    key = "SALT_REMOVED"
    result = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(s))
    return result.encode('latin1')


def deobfuscate_string(b):
    """Deobfuscate string"""
    key = "SALT_REMOVED"
    s = b.decode('latin1')
    result = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(s))
    return result
