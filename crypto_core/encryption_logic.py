from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256
import os

def generate_bio_key(hash_a, hash_b):
    """
    Fuses two node hashes using XOR to create the 256-bit Master Key.
    """
    # Convert hex strings to bytes
    bytes_a = bytes.fromhex(hash_a)
    bytes_b = bytes.fromhex(hash_b)
    
    # bitwise XOR the two nodes
    fused_seed = bytes(a ^ b for a, b in zip(bytes_a, bytes_b))
    
    # Run through SHA3 one last time to ensure a perfect 256-bit key
    return SHA3_256.new(fused_seed).digest()

def encrypt_data(plain_text, key):
    """
    Encrypts data using AES-256-GCM.
    """
    # Create a random 12-byte Nonce (standard for GCM)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))
    
    return {
        "ciphertext": ciphertext.hex(),
        "nonce": cipher.nonce.hex(),
        "tag": tag.hex() # This is the "seal" that proves it hasn't been messed with
    }

def decrypt_data(encrypted_payload, key):
    """
    Decrypts AES-256-GCM encrypted data.
    Validates the 'tag' to ensure the ciphertext hasn't been tampered with.
    """
    try:
        # Convert hex strings back to bytes
        nonce = bytes.fromhex(encrypted_payload["nonce"])
        ciphertext = bytes.fromhex(encrypted_payload["ciphertext"])
        tag = bytes.fromhex(encrypted_payload["tag"])
        
        # Initialize cipher with the same key and the nonce from the payload
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # decrypt_and_verify automatically checks the tag and throws an error if it fails
        plain_text = cipher.decrypt_and_verify(ciphertext, tag)
        return plain_text.decode('utf-8')
    except Exception as e:
        return f"Decryption Failed: {str(e)}"

# EXAMPLE USAGE
if __name__ == "__main__":
    import hashlib
    
    # Simulating 256-bit hashes derived from ambient audio (using SHA256 just for valid hex generation here)
    node_a_hash = hashlib.sha256(b"ambient_audio_sample_A_time_100").hexdigest()
    node_b_hash = hashlib.sha256(b"ambient_audio_sample_B_time_100").hexdigest()
    
    print(f"Node A Hash: {node_a_hash[:16]}...")
    print(f"Node B Hash: {node_b_hash[:16]}...")

    # 1. Generate the shared key
    master_key = generate_bio_key(node_a_hash, node_b_hash)
    print("\n--- Key Generated Successfully ---")

    # 2. Encrypt the data
    original_message = "Confidential AI Biometric Data - Level 5 Clearance"
    print(f"\nOriginal Message: '{original_message}'")
    
    payload = encrypt_data(original_message, master_key)
    print(f"Encrypted Ciphertext: {payload['ciphertext'][:32]}...")
    print(f"Authentication Tag: {payload['tag']}")

    # 3. Decrypt the data to prove the round trip works
    decrypted_message = decrypt_data(payload, master_key)
    print(f"\nDecrypted Message: '{decrypted_message}'")
    
    # 4. Demonstrate Tamper-Proofing (Optional)
    # If we alter even one character of the ciphertext, decryption will fail
    tampered_payload = payload.copy()
    tampered_payload["ciphertext"] = "00" + tampered_payload["ciphertext"][2:]
    print("\nAttempting to decrypt tampered data...")
    print(decrypt_data(tampered_payload, master_key))