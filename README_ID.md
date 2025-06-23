# Spyware/RAT Edukasional dengan Teknik Elusi Tingkat Lanjut

> **Also available in [English](README_EN.md).**

> **⚠️ Peringatan Penggunaan Etis**
>
> Perangkat lunak ini dikembangkan murni untuk **tujuan akademis dan edukasional** sebagai bagian dari studi pascasarjana dalam analisis malware. Tujuannya adalah untuk mendemonstrasikan dan memahami mekanisme kerja serta teknik elusi yang digunakan oleh perangkat lunak berbahaya.
>
> **DILARANG KERAS** menggunakan alat ini untuk aktivitas ilegal, tidak sah, atau berbahaya. Penulis tidak bertanggung jawab atas penyalahgunaan perangkat lunak ini. Gunakan secara bertanggung jawab di dalam lingkungan yang terkendali (seperti mesin virtual Anda sendiri).

---

<div align="center">
  <a href="https://youtu.be/6tfKwmIw0gQ">
    <img src="https://img.youtube.com/vi/6tfKwmIw0gQ/maxresdefault.jpg" alt="Demo Video" width="600">
  </a>
  <p><em>📺 Klik untuk menonton demo</em></p>
</div>


## 1. Tinjauan Proyek

Proyek ini adalah sebuah studi kasus implementasi **Spyware canggih dengan arsitektur yang dapat diperluas menjadi RAT (Remote Administration Tool)**. Dikembangkan dengan Python, alat ini dirancang untuk meniru perilaku dan kecanggihan malware modern. Fokusnya tidak hanya pada fungsionalitas monitoring, tetapi juga pada implementasi serangkaian **teknik elusi (evasion)** berlapis untuk menghindari deteksi oleh perangkat lunak keamanan dan platform analisis otomatis.

Tujuan utamanya adalah sebagai sarana pembelajaran praktis tentang bagaimana *malware* beroperasi, menyembunyikan diri, dan berkomunikasi, serta bagaimana berbagai metode kompilasi (`PyInstaller` vs. `Nuitka`) dapat mempengaruhi tingkat deteksinya.

## 2. Arsitektur Sistem

Sistem ini menggunakan arsitektur client-server terdistribusi yang dirancang untuk memaksimalkan *stealth* dan efisiensi operasional.


* **Agent (`.exe`)**: Komponen utama yang berjalan di target. Mengumpulkan data dan menjalankan server HTTP lokal ringan (`http.server`).
* **Dashboard (`index.html`)**: Antarmuka web untuk pemantau, berjalan di browser untuk menampilkan data secara *real-time*.
* **Cloudflare Tunnel**: Mengekspos server lokal Agent ke internet melalui URL dinamis yang aman.
* **Replit Webhook Relay**: **Komponen kunci elusi jaringan**. Agent tidak berkomunikasi langsung dengan API Telegram. Sebaliknya, ia mengirimkan *payload* terenkripsi AES ke *webhook* ini, yang kemudian meneruskan notifikasi. Ini secara efektif menyamarkan lalu lintas C2 (Command & Control).

## 3. Fitur Utama

### Fungsionalitas Monitoring
* **Status Sistem**: Monitoring penggunaan CPU & Memori secara *real-time*.
* **Informasi Sistem**: Mengumpulkan detail Sistem Operasi, IP Publik, Lokasi Geografis, dan Provider ISP.
* **Manajemen Proses**: Menampilkan daftar proses yang sedang berjalan.
* **Live Screenshot**: Mengambil gambar layar target secara periodik.
* **Keylogger**: Mencatat semua ketikan keyboard menggunakan *hook* `pynput`.

### Teknik Elusi & Siluman (Evasion & Stealth)
* **Anti-Debugging**: Mendeteksi keberadaan debugger melalui panggilan WinAPI `IsDebuggerPresent` dan anomali waktu eksekusi.
* **Anti-VM**: Menggunakan pendekatan berlapis untuk mendeteksi lingkungan virtual:
    * Pemeriksaan MAC Address.
    * Pemeriksaan nama proses *Guest Tools*.
    * Pemeriksaan kunci Registry spesifik VM.
    * Query WMI untuk nama perangkat keras virtual.
* **Anti-Sandbox**:
    * **Pemeriksaan Spesifikasi**: Program berhenti jika berjalan pada sistem dengan spesifikasi minimalis (resolusi rendah, CPU < 2 core, RAM < 2GB).
    * **Pemeriksaan Uptime**: Program berhenti jika uptime sistem kurang dari 15 menit.
    * **Aktivasi Berbasis Interaksi**: Fitur berbahaya (keylogger, screenshot) baru aktif setelah **gerakan mouse kumulatif > 5000 piksel**, mengelabui *sandbox* otomatis yang jarang mensimulasikan interaksi pengguna.
* **Obfuskasi Kredensial**:
    * Menggunakan enkripsi berlapis **ROT13 + XOR**.
    * Menyimpan kredensial sebagai *tuple* integer untuk menghindari deteksi string statis.
* **Komunikasi C2 Terenkripsi**:
    * Semua notifikasi ke *webhook relay* dienkripsi menggunakan **AES-256-CBC** untuk mencegah analisis lalu lintas jaringan.

## 4. Tumpukan Teknologi (Tech Stack)

* **Bahasa**: Python 3.10+
* **Server Lokal**: `http.server` (Pustaka Standar Python)
* **Monitoring**: `psutil`, `Pillow`, `pynput`, `wmi`
* **Kriptografi**: `pycryptodome`
* **Konektivitas**: `requests`, Cloudflare Tunnel
* **Compiler/Packer**: PyInstaller, Nuitka, UPX

## 5. Panduan Penggunaan

### A. Persiapan

1.  **Kloning Repositori**:
    ```bash
    git clone [https://github.com/GlgApr/Ganesha-Spyware.git](https://github.com/GlgApr/Ganesha-Spyware.git)
    cd Ganesha-Spyware
    ```
2.  **Buat Virtual Environment**:
    ```bash
    python -m venv .venv
    ```
3.  **Aktifkan Virtual Environment**:
    * **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`
    * **Linux/macOS**: `source .venv/bin/activate`
4.  **Instal Dependensi**:
    ```bash
    pip install -r requirements.txt
    ```

### B. Konfigurasi

1.  **Setup Webhook Relay**:
    * Deploy skrip yang ada di folder `replit` ke layanan seperti [Replit](https://replit.com).
    * Atur *Secrets* di Replit: `BOT_TOKEN`, `CHAT_ID`, dan `AES_KEY`.
    * Dapatkan URL publik dari Replit Anda.
2.  **Update `agent.py`**:
    * Jalankan `ultimate_encoder.py` untuk mengenkripsi kredensial Anda.
    * Salin hasilnya ke dalam `agent.py`.
    * Perbarui variabel `WEBHOOK_URL` dengan URL Replit Anda.

### C. Kompilasi menjadi `.exe` (Contoh dengan PyInstaller)

```powershell
pyinstaller --onefile --windowed --name "CustomName.exe" --icon="path/to/icon.ico" --add-data "cloudflared.exe;." --add-data "templates;templates" --upx-dir="path/to/upx_folder" agent.py
```

### D. Penggunaan

Jalankan file `.exe` yang sudah dikompilasi di mesin target (sebaiknya di dalam VM untuk pengujian). Anda akan menerima notifikasi di Telegram berisi URL untuk mengakses dashboard monitoring setelah ada interaksi mouse yang cukup.

## 6. Lisensi

Proyek ini dilisensikan di bawah **Lisensi MIT**. Lihat file `LICENSE` untuk detail lebih lanjut.
