from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64

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