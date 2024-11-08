from flask import request, jsonify
from sqlalchemy.orm import Session
from database import get_db
from encryption_service import encrypt_data
from cryptography.hazmat.primitives import serialization
import base64
import json
from models import User


def get_barcode():
    try:
        # Get the request data
        data = request.get_json()
        email = data.get('email')
        public_key_pem = data.get('public_key')

        # Ensure the public key is in the correct PEM format
        if not email or not public_key_pem:
            return jsonify({'message': 'Email and public key are required'}), 400

        # Deserialize the public key
        if isinstance(public_key_pem, str):
            public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        else:
            public_key = serialization.load_pem_public_key(public_key_pem)

        # Establish a connection to the database
        db = next(get_db())

        # Look up the user's barcode in the database using SQLAlchemy
        user = db.query(User).filter_by(email=email).first()

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        # Prepare the JSON data to be encrypted
        json_data = {
            'email': user.email,
            'barcode': user.barcode
        }
        json_string = json.dumps(json_data)
        print(json_string)
        # Encrypt the JSON string with the provided public key
        encrypted_json = encrypt_data(public_key, json_string)

        # Encode the encrypted data in base64 for easy transmission
        encrypted_json_base64 = base64.b64encode(encrypted_json).decode('utf-8')

        return jsonify({'encrypted_json': encrypted_json_base64}), 200

    except Exception as e:
        print(f"Error during barcode retrieval: {e}")
        return jsonify({'message': 'An error occurred while retrieving the barcode'}), 500
