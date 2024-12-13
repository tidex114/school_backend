from flask import request, jsonify
from sqlalchemy.orm import Session
from database import get_mks_db
from encryption_service import encrypt_data
from cryptography.hazmat.primitives import serialization
import base64
import json
from models import PomfretStudent
from calls import call_check_public_key
import requests


def get_barcode():
    try:
        # Get the request data
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        public_key_pem = data.get('public_key')

        # Ensure the public key is in the correct PEM format
        if not first_name or not last_name or not public_key_pem:
            return jsonify({'message': 'First name, last name, and public key are required'}), 400

        try:
            response_code = call_check_public_key.call_check_public_key(first_name, last_name, public_key_pem)
        except requests.exceptions.Timeout:
            return jsonify({'message': 'Timeout occurred while verifying public key'}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({'message': f'Error during public key verification: {str(e)}'}), 500

        # Stop further processing if no valid response from call_check_public_key
        if response_code != 200:
            return jsonify({'message': 'Verification failed'}), response_code

        # Deserialize the public key
        if isinstance(public_key_pem, str):
            public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        else:
            public_key = serialization.load_pem_public_key(public_key_pem)

        # Establish a connection to the database
        db = next(get_mks_db())

        # Look up the user's id_number in the pomfret_student table using SQLAlchemy
        student = db.query(PomfretStudent).filter_by(student=first_name, last_name=last_name).first()

        if student is None:
            return jsonify({'message': 'Student not found'}), 404

        # Prepare the JSON data to be encrypted
        json_data = {
            'first_name': first_name,
            'last_name': last_name,
            'barcode': int(student.id_number)
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