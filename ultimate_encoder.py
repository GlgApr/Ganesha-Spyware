# ultimate_encoder.py - Membuat kredensial terenkripsi dengan ROT13 + XOR

# Kunci ini HARUS SAMA PERSIS dengan yang ada di agent.py
XOR_KEY = 0xAA 

# --- Masukkan kredensial asli Anda di sini ---
BOT_TOKEN_TO_ENCODE = "7974139592:AAG8bh6kLOaufvlCUEF3IyqQqNli_TwsgDs"
CHAT_ID_TO_ENCODE = "772341780"

def rot13(text: str) -> str:
    """Menerapkan enkripsi ROT13 pada sebuah string."""
    result = ""
    for char in text:
        if 'a' <= char <= 'z':
            result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += char
    return result

def create_dynamic_representation(data_string: str) -> str:
    """
    Mengenkripsi string dengan XOR, lalu ROT13, lalu mengubahnya menjadi
    representasi Tuple of Integers untuk konstruksi dinamis.
    """
    # 1. Enkripsi dengan XOR
    xor_encrypted_bytes = bytearray(b ^ XOR_KEY for b in data_string.encode('utf-8'))
    
    # 2. Ubah hasil XOR ke string untuk di-ROT13
    # Gunakan 'latin-1' untuk memastikan semua nilai byte bisa di-decode
    xor_string = xor_encrypted_bytes.decode('latin-1')

    # 3. Enkripsi dengan ROT13
    rot13_string = rot13(xor_string)
    
    # 4. Ubah hasil akhir menjadi tuple integer
    final_bytes = rot13_string.encode('latin-1')
    tuple_string = str(tuple(final_bytes))
    
    return tuple_string

# Enkripsi dan cetak hasilnya
obfuscated_token_tuple = create_dynamic_representation(BOT_TOKEN_TO_ENCODE)
obfuscated_chat_id_tuple = create_dynamic_representation(CHAT_ID_TO_ENCODE)

print("="*60)
print("Salin hasil di bawah ini dan tempelkan ke script agent.py Anda.")
print("="*60)
print(f"OBFUSCATED_BOT_TOKEN_PARTS = {obfuscated_token_tuple}")
print(f"OBFUSCATED_CHAT_ID_PARTS = {obfuscated_chat_id_tuple}")
print("="*60)
