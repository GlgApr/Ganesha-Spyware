# Educational Spyware/RAT with Advanced Evasion Techniques

> **Juga tersedia dalam [Bahasa Indonesia](README_ID.md).**

> **⚠️ Ethical Use Warning**
>
> This software was developed strictly for **academic and educational purposes** as part of a postgraduate study in malware analysis. Its goal is to demonstrate and understand the mechanisms and evasion techniques employed by malicious software.
>
> It is **STRICTLY FORBIDDEN** to use this tool for any illegal, unauthorized, or malicious activities. The author assumes no liability for any misuse of this software. Please use it responsibly within a controlled environment (such as your own virtual machine).

---

## 1. Project Overview

This project is a case study in implementing an **advanced Spyware with an architecture extensible into a RAT (Remote Administration Tool)**. Developed in Python, this tool is designed to mimic the behavior and sophistication of modern malware. Its focus extends beyond standard monitoring functionalities to include a multi-layered implementation of **evasion techniques** aimed at bypassing detection by security software and automated analysis platforms.

The primary objective is to serve as a practical learning tool for understanding how malware operates, conceals itself, and communicates, as well as how different compilation methods (`PyInstaller` vs. `Nuitka`) can affect its detection rates.

## 2. System Architecture

The system employs a distributed client-server architecture designed to maximize stealth and operational efficiency.


* **Agent (`.exe`)**: The core component that runs on the target machine. It collects system data and runs a lightweight local HTTP server (`http.server`).
* **Dashboard (`index.html`)**: A web-based interface for the monitor, running in the browser to display data in real-time.
* **Cloudflare Tunnel**: Exposes the Agent's local server to the internet through a secure, dynamic URL.
* **Replit Webhook Relay**: **A key network evasion component**. The Agent does not communicate directly with the Telegram API. Instead, it sends an AES-encrypted payload to this webhook, which then forwards the notification. This effectively obfuscates the Command & Control (C2) traffic.

## 3. Core Features

### Monitoring Functionalities
* **System Status**: Real-time monitoring of CPU & Memory usage.
* **System Information**: Gathers details about the Operating System, Public IP, Geolocation, and ISP.
* **Process Management**: Displays a list of currently running processes.
* **Live Screenshot**: Periodically captures the target's screen.
* **Keylogger**: Logs all keyboard strokes using `pynput` hooks.

### Evasion & Stealth Techniques
* **Anti-Debugging**: Detects the presence of debuggers via WinAPI calls (`IsDebuggerPresent`) and execution timing anomalies.
* **Anti-VM**: A multi-layered approach to detect virtualized environments:
    * MAC Address prefix checking.
    * Guest Tools process name checking.
    * VM-specific Registry key checking.
    * WMI queries for virtual hardware names.
* **Anti-Sandbox**:
    * **Environment Checks**: Halts execution on systems with minimal specifications (low screen resolution, < 2 CPU cores, < 2GB RAM).
    * **Uptime Check**: Halts if system uptime is less than 15 minutes.
    * **User Interaction Trigger**: Malicious features (keylogger, screenshot) are only activated after a cumulative mouse movement of **> 5000 pixels**, evading automated sandboxes that lack natural user interaction.
* **Credential Obfuscation**:
    * Employs a multi-layered encryption scheme: **ROT13 + XOR**.
    * Stores credentials as an integer `tuple` to evade static string detection.
* **Encrypted C2 Communication**:
    * All notification payloads to the webhook relay are encrypted using **AES-256-CBC** to prevent network traffic analysis.

## 4. Tech Stack

* **Language**: Python 3.10+
* **Local Server**: `http.server` (Python Standard Library)
* **Monitoring**: `psutil`, `Pillow`, `pynput`, `wmi`
* **Cryptography**: `pycryptodome`
* **Connectivity**: `requests`, Cloudflare Tunnel
* **Compiler/Packer**: PyInstaller, Nuitka, UPX

## 5. Usage Guide

### A. Prerequisites

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/GlgApr/Ganesha-Spyware.git](https://github.com/GlgApr/Ganesha-Spyware.git)
    cd Ganesha-Spyware
    ```
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    ```
3.  **Activate the Virtual Environment**:
    * **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`
    * **Linux/macOS**: `source .venv/bin/activate`
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### B. Configuration

1.  **Setup Webhook Relay**:
    * Deploy the script provided in the `replit` folder to a service like [Replit](https://replit.com).
    * Set up the necessary Secrets in Replit: `BOT_TOKEN`, `CHAT_ID`, and `AES_KEY`.
    * Obtain the public URL for your Replit instance.
2.  **Update `agent.py`**:
    * Run `ultimate_encoder.py` to encrypt your credentials.
    * Copy the resulting tuples into `agent.py`.
    * Update the `WEBHOOK_URL` variable with your Replit URL.

### C. Compilation (Example with PyInstaller)

```powershell
pyinstaller --onefile --windowed --name "CustomName.exe" --icon="path/to/icon.ico" --add-data "cloudflared.exe;." --add-data "templates;templates" --upx-dir="path/to/upx_folder" agent.py
```

### D. Usage

Run the compiled `.exe` file on a target machine (preferably within a VM for testing). You will receive a notification on Telegram with the URL to access the monitoring dashboard once sufficient mouse interaction is detected.

## 6. License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
