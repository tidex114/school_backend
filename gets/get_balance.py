from flask import request, jsonify
from sqlalchemy.orm import Session
from database import get_mks_db
from encryption_service import encrypt_data
from cryptography.hazmat.primitives import serialization
import base64
import json
from models import PomfretStudent
from calls import call_check_public_key
from validators.jwt_validator import validate_jwt_token
import requests

def get_balance():
    try:
        # Get the request data
        data = request.get_json()
        uid = data.get('uid')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        public_key_pem = data.get('public_key')

        # Get the Authorization header
        access_token = request.headers.get('Authorization')
        if not access_token or not access_token.startswith("Bearer "):
            print(f"Authorization header: {access_token}")
            return jsonify({'message': 'Authorization header is missing or invalid'}), 401

        # Extract the token value from the Authorization header
        token = access_token.split(" ")[1]
        print(token)
        # Validate the token using the separate validator module
        is_valid, validation_response = validate_jwt_token(token, uid, f"{first_name} {last_name}")

        # Check if the token validation failed
        if not is_valid:
            print(f"Token validation failed: {validation_response}")
            return jsonify(validation_response), 401

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

        # Look up the user's balance in the pomfret_student table using SQLAlchemy
        student = db.query(PomfretStudent).filter_by(student=first_name, last_name=last_name).first()

        if student is None:
            return jsonify({'message': 'Student not found'}), 404

        # Prepare the JSON data to be encrypted
        json_data = {
            'first_name': first_name,
            'last_name': last_name,
            'remaining_balance': float(student.present)
        }
        json_string = json.dumps(json_data)
        print(json_string)
        # Encrypt the JSON string with the provided public key
        encrypted_json = encrypt_data(public_key, json_string)

        # Encode the encrypted data in base64 for easy transmission
        encrypted_json_base64 = base64.b64encode(encrypted_json).decode('utf-8')

        return jsonify({'encrypted_json': encrypted_json_base64}), 200

    except Exception as e:
        print(f"Error during balance retrieval: {e}")
        return jsonify({'message': 'An error occurred while retrieving the balance'}), 500