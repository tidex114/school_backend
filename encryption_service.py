from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
import base64
from cryptography.hazmat.primitives import padding as sym_padding

def load_public_key(public_key_str):
    """Load public key from a plain string."""
    try:
        print(f"Attempting to load public key: {public_key_str}")
        # Assuming the public key is stored in PEM format
        public_key = serialization.load_pem_public_key(
            public_key_str.encode('utf-8'),
            backend=default_backend()
        )
        print("Public key loaded successfully")
        return public_key
    except ValueError as e:
        print(f"Error loading public key: {e}")
        return None

def encrypt_data(public_key, data: str):
    """Encrypt data using the public key."""
    if isinstance(public_key, rsa.RSAPublicKey):
        print(f"Encrypting data: {data}")
        encrypted = public_key.encrypt(
            data.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(f"Data encrypted successfully: {base64.b64encode(encrypted).decode()}")
        return encrypted
    else:
        print("Invalid public key type provided")
        raise ValueError("Invalid public key type provided.")


def hybrid_encrypt_data(public_key, data: bytes):
    try:
        # Generate a random symmetric key (32 bytes for AES-256)
        symmetric_key = urandom(32)

        # Pad the data to make it a multiple of the block size (16 bytes for AES)
        padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encrypt the data using the symmetric key (AES)
        iv = urandom(16)  # Initialization Vector
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Encrypt the symmetric key using the RSA public key
        encrypted_symmetric_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Return both encrypted symmetric key and encrypted data
        return {
            'encrypted_key': base64.b64encode(encrypted_symmetric_key).decode('utf-8'),
            'encrypted_data': base64.b64encode(iv + encrypted_data).decode('utf-8')  # Combine IV and data
        }

    except Exception as e:
        print(f"Error during encryption: {e}")
        return None