import ctypes
import os
import sys
import time
import winreg
import psutil

# === OBFUSCATION CLASS ===
class Obfuscator:
    """Kelas untuk teknik obfuskasi."""
    _key = 0xAA

    @staticmethod
    def decrypt_string(encrypted_bytes):
        """Mendekripsi byte string menggunakan XOR sederhana."""
        return "".join(chr(byte ^ Obfuscator._key) for byte in encrypted_bytes)

    @staticmethod
    def junk_code():
        """
        Menyisipkan operasi tidak berguna untuk mengganggu analisis.
        Di Python, ini tidak berfungsi sebagai anti-disassembly seperti di C++,
        tetapi dapat membuat alur program lebih sulit diikuti.
        """
        a = 12345
        b = 54321
        c = (a * b) // 100
        c = c + a - b
        _ = str(c) * 2

    @staticmethod
    def obfuscated_calculation(value):
        """Melakukan kalkulasi yang diobfuskasi."""
        Obfuscator.junk_code()
        result = value
        
        # Operasi yang tidak perlu
        result = (result * 2 + 10) - 10
        result //= 2
        result ^= 0xFF
        result ^= 0xFF
        
        Obfuscator.junk_code()
        return result

# === ANTI-DEBUG TECHNIQUES ===
class AntiDebug:
    """Kelas untuk teknik anti-debugging."""

    @staticmethod
    def is_debugger_present_check():
        """1. Pemeriksaan menggunakan API IsDebuggerPresent."""
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0

    @staticmethod
    def peb_ntglobalflag_check():
        """
        2. Pemeriksaan PEB NtGlobalFlag.
        CATATAN: Implementasi ini spesifik untuk proses 32-bit yang berjalan di Windows.
        Offset mungkin berbeda pada arsitektur 64-bit.
        """
        if sys.maxsize > 2**32: # Melewatkan pada Python 64-bit
            return False
            
        try:
            # Dapatkan PEB (Process Environment Block)
            peb_addr = ctypes.c_ulong()
            # __asm { mov eax, fs:[30h] }
            ctypes.windll.kernel32.Wow64GetThreadContext if hasattr(ctypes.windll.kernel32, 'Wow64GetThreadContext') else None
            # This part is complex to achieve cleanly without assembly.
            # A common approach is to use NtQueryInformationProcess, but for simplicity
            # we will skip the direct implementation and focus on other checks.
            # For educational purposes, a conceptual placeholder:
            # A more advanced implementation would parse PEB structure via ctypes.
            return False # Placeholder - direct PEB access is highly complex and unstable in pure Python
        except:
            return False
            
    @staticmethod
    def timing_check(delay_threshold=0.01):
        """3. Deteksi berbasis waktu."""
        start = time.perf_counter()

        # Operasi dummy
        dummy = sum(i for i in range(1000))

        end = time.perf_counter()
        elapsed = end - start
        return elapsed > delay_threshold

# === ANTI-VM TECHNIQUES ===
class AntiVM:
    """Kelas untuk teknik anti-VM."""

    @staticmethod
    def check_vm_registry_keys():
        """1. Periksa registry keys yang terkait dengan VM."""
        vm_keys = [
            r"SOFTWARE\VMware, Inc.\VMware Tools",
            r"SOFTWARE\Oracle\VirtualBox Guest Additions",
            r"SYSTEM\ControlSet001\Services\vmmouse",
            r"SYSTEM\ControlSet001\Services\vmtools"
        ]
        for key_path in vm_keys:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path):
                    return True # Kunci ditemukan, kemungkinan ini VM
            except FileNotFoundError:
                continue
        return False

    @staticmethod
    def check_vm_files():
        """2. Periksa file yang terkait dengan VM."""
        vm_files = [
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32\\drivers\\vmmouse.sys"),
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32\\drivers\\vmhgfs.sys"),
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32\\vboxdisp.dll"),
        ]
        for file_path in vm_files:
            if os.path.exists(file_path):
                return True # File ditemukan, kemungkinan ini VM
        return False

    @staticmethod
    def check_vm_processes():
        """3. Periksa proses yang terkait dengan VM."""
        vm_processes = [
            "vmware.exe", "vmtoolsd.exe", "vboxservice.exe",
            "vboxtray.exe", "xenservice.exe"
        ]
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in vm_processes:
                return True # Proses VM ditemukan
        return False
        
    @staticmethod
    def check_mac_address():
        """4. Periksa MAC address yang umum digunakan oleh VM."""
        vm_mac_prefixes = ("00:05:69", "00:0c:29", "00:1c:14", "00:50:56", "08:00:27")
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        if addr.address.lower().startswith(vm_mac_prefixes):
                            return True # MAC address VM ditemukan
        except Exception:
            pass
        return False


# === SYSTEM MONITORING CLASS ===
class SystemMonitor:
    """Kelas utama untuk monitoring sistem."""

    def __init__(self):
        self.monitoring_active = False

    def initialize_monitoring(self):
        """Memeriksa lingkungan sebelum memulai monitoring."""
        print("Melakukan pemeriksaan keamanan lingkungan...")
        if AntiDebug.is_debugger_present_check():
            print("❌ Lingkungan debug terdeteksi!")
            return False
        
        if AntiDebug.timing_check():
            print("❌ Analisis waktu menunjukkan adanya debugger!")
            return False

        if AntiVM.check_vm_registry_keys() or AntiVM.check_vm_files() or AntiVM.check_vm_processes() or AntiVM.check_mac_address():
            print("❌ Mesin virtual terdeteksi!")
            return False
        
        print("✅ Lingkungan aman. Monitoring dapat dimulai.")
        self.monitoring_active = True
        return True

    def get_system_info(self):
        """Mengambil informasi CPU dan Memory."""
        if not self.monitoring_active: return

        Obfuscator.junk_code()

        # Menggunakan psutil untuk mendapatkan penggunaan CPU dan Memori
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()

        print(f"Penggunaan CPU: {cpu_usage}%")
        print(f"Penggunaan Memori: {memory_info.percent}% ({memory_info.used / (1024**3):.2f} GB / {memory_info.total / (1024**3):.2f} GB)")

        Obfuscator.junk_code()

    def monitor_processes(self):
        """Memantau proses yang sedang berjalan."""
        if not self.monitoring_active: return

        print("\n=== PROSES AKTIF ===")
        
        # psutil.process_iter untuk enumerasi proses
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Obfuscated output
                obfuscated_pid = Obfuscator.obfuscated_calculation(proc.info['pid'])
                print(f"Proses: {proc.info['name']:<30} | PID (diobfuskasi): {obfuscated_pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
        Obfuscator.junk_code()

    def monitor_network(self):
        """Memantau aktivitas jaringan dasar."""
        if not self.monitoring_active: return
        
        print("\nMemantau aktivitas jaringan...")
        try:
            net_io = psutil.net_io_counters()
            print(f"Data Terkirim: {net_io.bytes_sent / (1024**2):.2f} MB")
            print(f"Data Diterima: {net_io.bytes_recv / (1024**2):.2f} MB")
        except Exception as e:
            print(f"Tidak dapat memantau jaringan: {e}")

        Obfuscator.junk_code()

# === MAIN PROGRAM ===
def main():
    """Fungsi utama untuk menjalankan program."""
    print("=== SISTEM MONITORING SOFTWARE UAS ===")
    print("Anti-Debug, Anti-VM, dan Obfuskasi Aktif")
    print("-" * 40)

    monitor = SystemMonitor()

    if not monitor.initialize_monitoring():
        print("\n⚠️ Monitoring tidak dapat dijalankan - Lingkungan tidak aman!")
        return -1

    print("\nMemulai monitoring sistem...")

    # Loop monitoring utama
    try:
        for i in range(5):  # Jalankan selama 5 iterasi untuk demonstrasi
            print(f"\n--- Iterasi {i + 1} ---")
            
            monitor.get_system_info()
            monitor.monitor_processes()
            monitor.monitor_network()

            print("\nMenunggu 5 detik sebelum iterasi berikutnya...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nMonitoring dihentikan oleh pengguna.")

    print("\n✅ Monitoring selesai.")
    return 0

if __name__ == "__main__":
    sys.exit(main())