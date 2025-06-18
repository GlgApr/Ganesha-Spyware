# advanced_encoder.py - Membuat kredensial terenkripsi yang dipecah-pecah.

# Pastikan kunci ini SAMA PERSIS dengan yang ada di agent.py
XOR_KEY = 0xAA 

# --- Masukkan kredensial asli Anda di sini ---
BOT_TOKEN_TO_ENCODE = "7974139592:AAG8bh6kLOaufvlCUEF3IyqQqNli_TwsgDs"
CHAT_ID_TO_ENCODE = "772341780"

def create_dynamic_representation(data_string: str) -> str:
    """
    Mengenkripsi string dengan XOR, lalu mengubahnya menjadi representasi
    Tuple of Integers untuk konstruksi dinamis.
    """
    # 1. Ubah string ke bytes
    original_bytes = data_string.encode('utf-8')
    
    # 2. Enkripsi setiap byte dengan XOR
    encrypted_bytes = bytearray(b ^ XOR_KEY for b in original_bytes)
    
    # 3. Ubah setiap byte menjadi nilai integer dan format sebagai tuple string
    # Contoh: b'\x01\x02\x03' -> "(1, 2, 3)"
    tuple_string = str(tuple(encrypted_bytes))
    
    return tuple_string

# Enkripsi dan cetak hasilnya
obfuscated_token_tuple = create_dynamic_representation(BOT_TOKEN_TO_ENCODE)
obfuscated_chat_id_tuple = create_dynamic_representation(CHAT_ID_TO_ENCODE)

print("="*60)
print("Salin hasil di bawah ini dan tempelkan ke script agent.py Anda.")
print("Gantikan seluruh baris variabel yang ada.")
print("="*60)
print(f"OBFUSCATED_BOT_TOKEN_PARTS = {obfuscated_token_tuple}")
print(f"OBFUSCATED_CHAT_ID_PARTS = {obfuscated_chat_id_tuple}")
print("\nContoh hasil akan terlihat seperti: (196, 217, 207, ...)")
print("="*60)
