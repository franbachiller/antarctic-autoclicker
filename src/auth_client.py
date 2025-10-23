"""
Antarctic License Authentication Client
Handles online license validation with the auth server
"""

import requests
import hashlib
import platform
import uuid
import json
import os
import base64
from datetime import datetime, timedelta
try:
    from cryptography.fernet import Fernet
    HAS_FERNET = True
except ImportError:
    HAS_FERNET = False

class AuthClient:
    def __init__(self, server_url="https://antarctic-autoclicker.vercel.app"):
        """
        Initialize the authentication client

        Args:
            server_url: URL of your Vercel deployment (production URL)
        """
        self.server_url = server_url.rstrip('/')
        # Store session file in AppData folder
        app_dir = self._get_app_data_dir()
        self.session_file = os.path.join(app_dir, 'antarctic_session.dat')
        self.session_token = None
        self.expires_at = None
        self.license_type = None
        self.license_expires = None
    
    def _get_app_data_dir(self):
        """Get or create the application data directory in AppData/Local"""
        try:
            import sys
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

    def get_hwid(self):
        """Generate unique hardware ID for this machine"""
        # Combine multiple hardware identifiers
        machine_id = platform.node()
        processor = platform.processor()
        system = platform.system()
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0, 2*6, 2)][::-1])

        # Create unique HWID (64 hex characters as required by server)
        hwid_string = f"{machine_id}-{processor}-{system}-{mac}"
        hwid = hashlib.sha256(hwid_string.encode()).hexdigest()
        return hwid

    def save_session(self):
        """Save session to encrypted file"""
        if not self.session_token:
            return False

        try:
            data = {
                'token': self.session_token,
                'expires': self.expires_at.isoformat() if self.expires_at else None,
                'license_type': self.license_type,
                'license_expires': self.license_expires.isoformat() if self.license_expires else None
            }

            json_data = json.dumps(data)
            hwid = self.get_hwid()

            if HAS_FERNET:
                # Use Fernet (AES-128) encryption
                key = base64.urlsafe_b64encode(hashlib.sha256(hwid.encode()).digest())
                cipher = Fernet(key)
                encrypted = cipher.encrypt(json_data.encode())
            else:
                # Fallback to XOR
                encrypted = ''.join(chr(ord(c) ^ ord(hwid[i % len(hwid)]))
                                  for i, c in enumerate(json_data)).encode('latin1')

            with open(self.session_file, 'wb') as f:
                f.write(encrypted)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def load_session(self):
        """Load session from encrypted file"""
        try:
            if not os.path.exists(self.session_file):
                return False

            with open(self.session_file, 'rb') as f:
                encrypted = f.read()

            hwid = self.get_hwid()

            if HAS_FERNET:
                # Decrypt with Fernet
                key = base64.urlsafe_b64encode(hashlib.sha256(hwid.encode()).digest())
                cipher = Fernet(key)
                json_data = cipher.decrypt(encrypted).decode()
            else:
                # Fallback XOR decrypt
                encrypted_str = encrypted.decode('latin1')
                json_data = ''.join(chr(ord(c) ^ ord(hwid[i % len(hwid)]))
                                  for i, c in enumerate(encrypted_str))

            data = json.loads(json_data)
            self.session_token = data.get('token')
            self.license_type = data.get('license_type')

            if data.get('expires'):
                self.expires_at = datetime.fromisoformat(data['expires'])
                if self.expires_at < datetime.now():
                    self.clear_session()
                    return False

            if data.get('license_expires'):
                self.license_expires = datetime.fromisoformat(data['license_expires'])

            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            self.clear_session()
            return False

    def clear_session(self):
        """Clear session data"""
        self.session_token = None
        self.expires_at = None
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except:
                pass

    def activate(self, license_key):
        """
        Activate license with the server

        Args:
            license_key: The license key to activate

        Returns:
            (success: bool, message: str, data: dict)
        """
        try:
            hwid = self.get_hwid()

            response = requests.post(
                f"{self.server_url}/api/activate",
                json={
                    'licenseKey': license_key,
                    'hwid': hwid
                },
                timeout=10,
                verify=True
            )

            # Check if response is valid
            if response.status_code != 200:
                # Try to get error message from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'Server error (code {response.status_code})')
                    return False, error_msg, None
                except:
                    return False, f"Server error (code {response.status_code})", None

            # Try to parse JSON
            try:
                result = response.json()
            except ValueError as e:
                return False, f"Invalid server response: {response.text[:100]}", None

            if result.get('success'):
                # Save session
                self.session_token = result.get('sessionToken')
                self.license_type = result.get('licenseType', 'Unknown')

                if result.get('expiresAt'):
                    self.expires_at = datetime.fromisoformat(
                        result['expiresAt'].replace('Z', '+00:00')
                    )
                    # License expires at the same time as session for now
                    self.license_expires = self.expires_at

                self.save_session()
                return True, result.get('message', 'Activation successful'), result
            else:
                return False, result.get('error', 'Activation failed'), None

        except requests.exceptions.SSLError as e:
            return False, f"SSL Certificate error. Please check your internet connection.", None
        except requests.exceptions.ConnectionError as e:
            return False, f"Cannot connect to server. Check your internet.", None
        except requests.exceptions.Timeout as e:
            return False, f"Connection timeout. Server is slow or down.", None
        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None

    def validate(self):
        """
        Validate current session with server

        Returns:
            (valid: bool, message: str)
        """
        try:
            # Try to load saved session
            if not self.session_token:
                if not self.load_session():
                    return False, "No active session"

            hwid = self.get_hwid()

            response = requests.post(
                f"{self.server_url}/api/validate",
                json={
                    'sessionToken': self.session_token,
                    'hwid': hwid
                },
                timeout=10,
                verify=True
            )

            # Check if response is valid
            if response.status_code != 200:
                # Session invalid, clear it
                self.clear_session()
                return False, f"Server error (code {response.status_code})"

            # Try to parse JSON
            try:
                result = response.json()
            except ValueError as e:
                # Network issue, use grace period
                if self.session_token and self.expires_at:
                    grace_period = self.expires_at - timedelta(hours=1)
                    if datetime.now() < grace_period:
                        return True, "Offline mode (grace period)"
                return False, f"Invalid server response"

            if result.get('success'):
                return True, result.get('message', 'Session valid')
            else:
                # Session invalid, clear it
                self.clear_session()
                return False, result.get('error', 'Session invalid')

        except requests.exceptions.SSLError as e:
            # SSL error - use grace period
            if self.session_token and self.expires_at:
                grace_period = self.expires_at - timedelta(hours=1)
                if datetime.now() < grace_period:
                    return True, "Offline mode (SSL issue, grace period)"
            return False, "SSL Certificate error"
        except requests.exceptions.ConnectionError as e:
            # Network error - allow offline grace period
            if self.session_token and self.expires_at:
                grace_period = self.expires_at - timedelta(hours=1)
                if datetime.now() < grace_period:
                    return True, "Offline mode (grace period)"
            return False, "Cannot connect to server"
        except requests.exceptions.Timeout as e:
            # Timeout - use grace period
            if self.session_token and self.expires_at:
                grace_period = self.expires_at - timedelta(hours=1)
                if datetime.now() < grace_period:
                    return True, "Offline mode (timeout, grace period)"
            return False, "Connection timeout"
        except requests.RequestException as e:
            # Network error - allow offline grace period
            if self.session_token and self.expires_at:
                grace_period = self.expires_at - timedelta(hours=1)
                if datetime.now() < grace_period:
                    return True, "Offline mode (grace period)"
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def is_activated(self):
        """
        Check if currently activated (with network validation)

        Returns:
            bool: True if activated and valid
        """
        valid, _ = self.validate()
        return valid

    def deactivate(self):
        """Deactivate by clearing local session"""
        self.clear_session()
        return True

    def get_time_remaining(self):
        """
        Get time remaining on license

        Returns:
            str: Human-readable time remaining or error message
        """
        try:
            if not self.license_expires:
                return "Unknown"

            now = datetime.now()
            if self.license_expires.tzinfo:
                # Make now timezone aware if license_expires is
                from datetime import timezone
                now = datetime.now(timezone.utc)

            remaining = self.license_expires - now

            if remaining.total_seconds() <= 0:
                return "Expired"

            days = remaining.days
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            if days > 365:
                return "Lifetime"
            elif days > 30:
                months = days // 30
                return f"{months} month{'s' if months > 1 else ''}"
            elif days > 0:
                return f"{days} day{'s' if days > 1 else ''}"
            elif hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{minutes} minute{'s' if minutes > 1 else ''}"

        except Exception as e:
            return "Unknown"

    def get_license_info(self):
        """
        Get complete license information

        Returns:
            dict: License information including type, expiry, time remaining
        """
        return {
            'type': self.license_type or 'Unknown',
            'expires_at': self.license_expires.strftime('%Y-%m-%d %H:%M') if self.license_expires else 'Unknown',
            'time_remaining': self.get_time_remaining()
        }


# Example usage
if __name__ == "__main__":
    # Initialize client with your Vercel URL
    auth = AuthClient(server_url="https://antarctic-autoclicker.vercel.app")

    # Test activation
    print("Testing activation...")
    license_key = input("Enter license key: ")

    success, message, data = auth.activate(license_key)
    print(f"Activation: {message}")

    if success:
        print(f"License type: {data['licenseType']}")
        print(f"Expires at: {data['expiresAt']}")

        # Test validation
        print("\nTesting validation...")
        valid, msg = auth.validate()
        print(f"Validation: {msg}")
        print(f"Is activated: {auth.is_activated()}")
