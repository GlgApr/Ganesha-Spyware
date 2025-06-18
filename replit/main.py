# main.py - Relay server dengan logging diagnostik yang sangat detail

from flask import Flask, request, jsonify
import requests
import base64
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)

# --- Ambil kunci dan kredensial dari environment secrets ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
AES_KEY = os.environ.get('AES_KEY', '').encode('utf-8')


def decrypt_payload(encrypted_payload_b64, aes_key_bytes):
    """Mendekripsi payload terenkripsi AES menggunakan kunci yang diberikan."""
    try:
        if not aes_key_bytes or len(aes_key_bytes) != 32:
            print(f"--> [DEBUG] DECRYPTION FAILED: Kunci AES tidak valid atau panjangnya bukan 32 byte. Panjang saat ini: {len(aes_key_bytes)}")
            return None

        encrypted_data = base64.b64decode(encrypted_payload_b64)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        cipher = AES.new(aes_key_bytes, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        decrypted_data = unpad(decrypted_padded, AES.block_size)

        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"--> [DEBUG] Decryption failed with exception: {e}")
        return None

@app.route('/notify', methods=['POST'])
def notify():
    """Endpoint yang menerima payload terenkripsi."""
    print("\n--- Menerima Request Baru di /notify ---")

    encrypted_payload = request.json.get('data')
    if not encrypted_payload:
        print("--> [ERROR] Request tidak berisi 'data'. Mengembalikan 400.")
        return jsonify({"status": "error", "message": "No data received"}), 400

    print(f"--> [INFO] Menerima payload terenkripsi: {encrypted_payload[:30]}...")

    # Langsung gunakan kunci AES yang diambil dari secrets.
    decrypted_json_string = decrypt_payload(encrypted_payload, AES_KEY)

    if not decrypted_json_string:
        print("--> [ERROR] Dekripsi gagal. Mengembalikan 500.")
        return jsonify({"status": "error", "message": "Decryption failed. Pastikan AES_KEY di Replit sama dengan di agent.py dan panjangnya 32 byte."}), 500

    print(f"--> [SUCCESS] Payload berhasil di-dekripsi menjadi: {decrypted_json_string}")

    try:
        # Ekstrak data yang relevan dari payload yang sudah di-dekripsi
        payload_data = json.loads(decrypted_json_string)
        url_from_agent = payload_data.get('url')
        hostname = payload_data.get('hostname', 'Unknown Host')
        print(f"--> [INFO] Data yang diparsing: URL='{url_from_agent}', Hostname='{hostname}'")

        if not all([url_from_agent, BOT_TOKEN, CHAT_ID]):
             print("--> [ERROR] Data tidak lengkap (URL, BOT_TOKEN, atau CHAT_ID kosong). Mengembalikan 400.")
             return jsonify({"status": "error", "message": "Incomplete data or server misconfiguration (BOT_TOKEN/CHAT_ID missing in secrets)"}), 400

    except (json.JSONDecodeError, KeyError) as e:
        print(f"--> [ERROR] Gagal memproses JSON yang sudah di-dekripsi: {e}")
        return jsonify({"status": "error", "message": "Failed to process decrypted payload"}), 400

    # Kirim ke Telegram
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    formatted_message = f"💻 *Monitoring Aktif*\n\n*Perangkat:* `{hostname}`\n*URL Dashboard:*\n{url_from_agent}"
    params = {'chat_id': CHAT_ID, 'text': formatted_message, 'parse_mode':'Markdown'}

    try:
        print("--> [INFO] Mengirim notifikasi ke Telegram...")
        requests.get(api_url, params=params, timeout=10)
        print("--> [SUCCESS] Notifikasi Telegram berhasil dikirim.")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"--> [ERROR] Gagal mengirim ke Telegram: {e}")
        return jsonify({"status": "error", "message": "Failed to send to Telegram"}), 500

@app.route('/')
def index():
    return "Encrypted Webhook Relay is active."

def run():
  app.run(host='0.0.0.0', port=8080)

run()
