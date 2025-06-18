
// Windows System Monitoring Software dengan Anti-Debug, Anti-VM, dan Obfuskasi
// Dibuat untuk keperluan UAS - Monitoring Aktivitas Perangkat

#include <windows.h>
#include <pdh.h>
#include <psapi.h>
#include <wbemidl.h>
#include <comdef.h>
#include <iostream>
#include <vector>
#include <string>
#include <tlhelp32.h>

#pragma comment(lib, "pdh.lib")
#pragma comment(lib, "psapi.lib")
#pragma comment(lib, "wbemuuid.lib")

// === ANTI-DEBUG TECHNIQUES ===
class AntiDebug {
public:
    // 1. IsDebuggerPresent API Check
    static bool IsDebuggerPresentCheck() {
        return IsDebuggerPresent();
    }

    // 2. PEB NtGlobalFlag Check
    static bool PEB_NtGlobalFlagCheck() {
        BOOL is_debugged = FALSE;

        __asm {
            mov eax, fs:[30h]        // Get PEB
            movzx eax, byte ptr[eax + 68h]  // NtGlobalFlag offset
            and eax, 70h             // Check FLG_HEAP_ENABLE_TAIL_CHECK | 
                                     // FLG_HEAP_ENABLE_FREE_CHECK | 
                                     // FLG_HEAP_VALIDATE_PARAMETERS
            mov is_debugged, eax
        }

        return is_debugged != 0;
    }

    // 3. Heap Flags Check
    static bool HeapFlagsCheck() {
        BOOL is_debugged = FALSE;
        DWORD heap_flags = 0;

        __asm {
            mov eax, fs:[30h]        // Get PEB
            mov eax, [eax + 18h]     // Get default heap
            mov ebx, [eax + 0Ch]     // Heap flags
            mov heap_flags, ebx
        }

        return (heap_flags & 0x50000062) != 0;
    }

    // 4. Timing-based Detection
    static bool TimingCheck() {
        LARGE_INTEGER start, end, freq;
        QueryPerformanceCounter(&start);

        // Dummy operation
        volatile int dummy = 0;
        for (int i = 0; i < 1000; i++) {
            dummy += i;
        }

        QueryPerformanceCounter(&end);
        QueryPerformanceFrequency(&freq);

        double elapsed = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;
        return elapsed > 0.001; // If too slow, debugger might be present
    }
};

// === ANTI-VM TECHNIQUES ===
class AntiVM {
public:
    // 1. Check for VM Registry Keys
    static bool CheckVMRegistryKeys() {
        const wchar_t* vm_keys[] = {
            L"SOFTWARE\\VMware, Inc.\\VMware Tools",
            L"SOFTWARE\\Oracle\\VirtualBox Guest Additions",
            L"SYSTEM\\ControlSet001\\Services\\vmmouse",
            L"SYSTEM\\ControlSet001\\Services\\vmtools"
        };

        HKEY hKey;
        for (const auto& key : vm_keys) {
            if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, key, 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
                RegCloseKey(hKey);
                return true;
            }
        }
        return false;
    }

    // 2. Check VM Files
    static bool CheckVMFiles() {
        const wchar_t* vm_files[] = {
            L"C:\\windows\\system32\\drivers\\vmmouse.sys",
            L"C:\\windows\\system32\\drivers\\vmhgfs.sys",
            L"C:\\windows\\system32\\vboxdisp.dll",
            L"C:\\windows\\system32\\vboxhook.dll"
        };

        for (const auto& file : vm_files) {
            if (GetFileAttributesW(file) != INVALID_FILE_ATTRIBUTES) {
                return true;
            }
        }
        return false;
    }

    // 3. Check VM Processes
    static bool CheckVMProcesses() {
        const wchar_t* vm_processes[] = {
            L"vmware.exe", L"vmtoolsd.exe", L"vboxservice.exe", 
            L"vboxtray.exe", L"xenservice.exe"
        };

        HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (hSnapshot == INVALID_HANDLE_VALUE) return false;

        PROCESSENTRY32W pe32;
        pe32.dwSize = sizeof(PROCESSENTRY32W);

        bool vm_found = false;
        if (Process32FirstW(hSnapshot, &pe32)) {
            do {
                for (const auto& vm_proc : vm_processes) {
                    if (wcsstr(pe32.szExeFile, vm_proc)) {
                        vm_found = true;
                        break;
                    }
                }
            } while (Process32NextW(hSnapshot, &pe32) && !vm_found);
        }

        CloseHandle(hSnapshot);
        return vm_found;
    }

    // 4. CPUID Check
    static bool CPUIDCheck() {
        int cpuInfo[4] = {0};
        __cpuid(cpuInfo, 1);

        // Check for hypervisor bit
        return (cpuInfo[2] & (1 << 31)) != 0;
    }
};

// === OBFUSCATION CLASS ===
class Obfuscator {
private:
    static constexpr char key = 0xAA;

public:
    // Simple XOR string encryption
    static std::string DecryptString(const char* encrypted, size_t length) {
        std::string result;
        for (size_t i = 0; i < length; i++) {
            result += encrypted[i] ^ key;
        }
        return result;
    }

    static void EncryptString(const std::string& str, char* output) {
        for (size_t i = 0; i < str.length(); i++) {
            output[i] = str[i] ^ key;
        }
        output[str.length()] = '\0';
    }

    // Anti-disassembly tricks
    static void JunkCode() {
        __asm {
            nop
            nop
            mov eax, eax
            add eax, 0
            sub eax, 0
            nop
        }
    }

    // Control flow obfuscation
    static int ObfuscatedCalculation(int value) {
        JunkCode();
        int result = value;

        // Add unnecessary operations
        result = (result * 2 + 10) - 10;
        result = result / 2;
        result = result ^ 0xFF;
        result = result ^ 0xFF;

        JunkCode();
        return result;
    }
};

// === SYSTEM MONITORING CLASS ===
class SystemMonitor {
private:
    PDH_HQUERY hQuery;
    PDH_HCOUNTER hCounterCPU;
    PDH_HCOUNTER hCounterMemory;
    bool monitoring_active;

public:
    SystemMonitor() : monitoring_active(false) {
        // Initialize PDH
        PdhOpenQuery(NULL, 0, &hQuery);

        // Obfuscated strings for counter paths
        char encrypted_cpu[] = {0xF2, 0xF7, 0xFE, 0xF9, 0xFA, 0xF1, 0xF1, 0xFE, 0xF7, 0xCA, 0x8A, 0xCA, 0xF4, 0xFA, 0xF7, 0xF9, 0xFA, 0xF1, 0xF1, 0xFE, 0xF7, 0xCA, 0xD6, 0xF6, 0xF8, 0xFA, 0x00};
        char encrypted_mem[] = {0xF2, 0xF7, 0xFE, 0xF9, 0xFA, 0xF1, 0xF1, 0xFE, 0xF7, 0xCA, 0x8A, 0xCA, 0xC1, 0xF7, 0xF6, 0xFB, 0xFE, 0xF7, 0xFE, 0xC5, 0xCA, 0xC1, 0xC5, 0xF5, 0xFA, 0xF1, 0x00};

        std::string cpu_counter = Obfuscator::DecryptString(encrypted_cpu, 26);
        std::string mem_counter = Obfuscator::DecryptString(encrypted_mem, 26);

        // Add counters
        PdhAddCounterA(hQuery, cpu_counter.c_str(), 0, &hCounterCPU);
        PdhAddCounterA(hQuery, mem_counter.c_str(), 0, &hCounterMemory);

        PdhCollectQueryData(hQuery);
    }

    ~SystemMonitor() {
        if (hQuery) {
            PdhCloseQuery(hQuery);
        }
    }

    bool InitializeMonitoring() {
        // Anti-analysis checks before starting
        if (AntiDebug::IsDebuggerPresentCheck()) {
            std::wcout << L"Debug environment detected!" << std::endl;
            return false;
        }

        if (AntiDebug::PEB_NtGlobalFlagCheck()) {
            std::wcout << L"PEB analysis detected debugging!" << std::endl;
            return false;
        }

        if (AntiVM::CheckVMRegistryKeys() || AntiVM::CheckVMFiles() || AntiVM::CheckVMProcesses()) {
            std::wcout << L"Virtual machine detected!" << std::endl;
            return false;
        }

        monitoring_active = true;
        return true;
    }

    void GetSystemInfo() {
        if (!monitoring_active) return;

        Obfuscator::JunkCode();

        // Collect performance data
        PdhCollectQueryData(hQuery);
        Sleep(1000); // Wait for next measurement
        PdhCollectQueryData(hQuery);

        PDH_FMT_COUNTERVALUE counterVal;

        // Get CPU usage
        if (PdhGetFormattedCounterValue(hCounterCPU, PDH_FMT_DOUBLE, NULL, &counterVal) == ERROR_SUCCESS) {
            std::wcout << L"CPU Usage: " << counterVal.doubleValue << L"%" << std::endl;
        }

        // Get memory usage
        MEMORYSTATUSEX memInfo;
        memInfo.dwLength = sizeof(MEMORYSTATUSEX);
        GlobalMemoryStatusEx(&memInfo);

        DWORDLONG totalVirtualMem = memInfo.ullTotalPageFile;
        DWORDLONG virtualMemUsed = memInfo.ullTotalPageFile - memInfo.ullAvailPageFile;

        std::wcout << L"Memory Usage: " << (virtualMemUsed * 100 / totalVirtualMem) << L"%" << std::endl;

        Obfuscator::JunkCode();
    }

    void MonitorProcesses() {
        if (!monitoring_active) return;

        HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (hSnapshot == INVALID_HANDLE_VALUE) return;

        PROCESSENTRY32W pe32;
        pe32.dwSize = sizeof(PROCESSENTRY32W);

        std::wcout << L"\n=== ACTIVE PROCESSES ===" << std::endl;

        if (Process32FirstW(hSnapshot, &pe32)) {
            do {
                // Obfuscated output
                int obfuscated_pid = Obfuscator::ObfuscatedCalculation(pe32.th32ProcessID);
                std::wcout << L"Process: " << pe32.szExeFile 
                          << L" | PID: " << obfuscated_pid << std::endl;

                Obfuscator::JunkCode();

            } while (Process32NextW(hSnapshot, &pe32));
        }

        CloseHandle(hSnapshot);
    }

    void MonitorNetwork() {
        if (!monitoring_active) return;

        // Basic network monitoring using WMI would go here
        // For brevity, showing concept only
        std::wcout << L"\nNetwork monitoring active..." << std::endl;
        Obfuscator::JunkCode();
    }
};

// === MAIN PROGRAM ===
int main() {
    std::wcout << L"=== SISTEM MONITORING SOFTWARE UAS ===" << std::endl;
    std::wcout << L"Anti-Debug, Anti-VM, dan Obfuskasi Aktif" << std::endl;

    SystemMonitor monitor;

    if (!monitor.InitializeMonitoring()) {
        std::wcout << L"Monitoring tidak dapat dijalankan - Lingkungan tidak aman!" << std::endl;
        return -1;
    }

    std::wcout << L"\nMemulai monitoring sistem..." << std::endl;

    // Main monitoring loop
    for (int i = 0; i < 10; i++) {  // Run for 10 iterations
        std::wcout << L"\n--- Iterasi " << (i + 1) << L" ---" << std::endl;

        monitor.GetSystemInfo();
        monitor.MonitorProcesses();
        monitor.MonitorNetwork();

        Sleep(5000);  // Wait 5 seconds between iterations
    }

    std::wcout << L"\nMonitoring selesai." << std::endl;
    return 0;
}

/*
KOMPILASI:
cl /EHsc WindowsMonitor.cpp pdh.lib psapi.lib wbemuuid.lib

FITUR YANG DIIMPLEMENTASIKAN:

1. ANTI-DEBUG:
   - IsDebuggerPresent() API check
   - PEB NtGlobalFlag analysis
   - Heap flags detection
   - Timing-based detection

2. ANTI-VM:
   - Registry key detection
   - VM file detection
   - VM process detection
   - CPUID hypervisor bit check

3. OBFUSKASI:
   - String encryption (XOR)
   - Junk code insertion
   - Control flow obfuscation
   - Anti-disassembly tricks

4. MONITORING:
   - CPU usage monitoring
   - Memory usage monitoring
   - Process enumeration
   - Network monitoring (basic framework)

CATATAN KEAMANAN:
- Kode ini hanya untuk tujuan edukasi dan UAS
- Jangan digunakan untuk aktivitas ilegal
- Perhatikan aspek legal dan etika dalam penggunaan
*/
