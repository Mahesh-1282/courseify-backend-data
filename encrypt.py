import sys
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom

# The exact key expected by your Flutter app
SECRET_KEY = "courseify_super_secret_key_12345"

def embed_images(data):
    """Recursively search for 'note_image_path' and embed it as Base64."""
    if isinstance(data, dict):
        if "note_image_path" in data:
            path = data["note_image_path"]
            if os.path.exists(path):
                with open(path, "rb") as img_f:
                    encoded = base64.b64encode(img_f.read()).decode("utf-8")
                    data["note_image_base64"] = encoded
            else:
                print(f"Warning: Image {path} not found.")
            del data["note_image_path"]
            
        for key, value in data.items():
            embed_images(value)
    elif isinstance(data, list):
        for item in data:
            embed_images(item)

def encrypt_data(input_file, output_file):
    # Ensure key is 32 bytes for AES-256
    key = SECRET_KEY.encode('utf-8').ljust(32, b'\0')[:32]
    
    # Load JSON and embed images
    with open(input_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    embed_images(json_data)
    
    # Convert back to bytes
    data = json.dumps(json_data).encode('utf-8')
    
    # Pad data to multiple of 16 bytes for AES CBC
    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length] * padding_length)
    
    iv = urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Store IV followed by encrypted data
    with open(output_file, 'wb') as f:
        f.write(iv + encrypted_data)
        
    print(f"✅ Success! Encrypted {input_file} -> {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python encrypt.py <input.json> <output.enc>")
        sys.exit(1)
        
    encrypt_data(sys.argv[1], sys.argv[2])
