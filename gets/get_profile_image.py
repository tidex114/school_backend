from flask import request, jsonify
from sqlalchemy.orm import Session
from database import get_db
from encryption_service import encrypt_data, hybrid_encrypt_data
from cryptography.hazmat.primitives import serialization
import base64
import json
from models import DirectoryPhoto
import io
from calls import call_check_public_key
from validators.jwt_validator import validate_jwt_token
import requests

def get_profile_image():
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
        db = next(get_db())

        # Look up the user's profile picture in the database using SQLAlchemy
        user = db.query(DirectoryPhoto).filter_by(first_name=first_name, last_name=last_name).first()

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        # Ensure user has a profile picture
        if not user.photo:
            return jsonify({'message': 'Profile picture not found'}), 404

        # Encrypt the binary photo data using the hybrid encryption method
        encrypted_result = hybrid_encrypt_data(public_key, user.photo)

        if encrypted_result is None:
            return jsonify({'message': 'Encryption failed'}), 500

        # Create a response containing the encrypted photo
        response_data = {
            'first_name': first_name,
            'last_name': last_name,
            'encrypted_key': encrypted_result['encrypted_key'],
            'encrypted_photo': encrypted_result['encrypted_data']
        }
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error during profile picture retrieval: {e}")
        return jsonify({'message': 'An error occurred while retrieving the profile picture'}), 500