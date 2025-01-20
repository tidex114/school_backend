from flask import request, jsonify
from sqlalchemy import func, desc, literal_column
from database import get_mks_db
from models import NewTransaction
from calls import call_check_public_key
from validators.jwt_validator import validate_jwt_token
import requests
from cryptography.hazmat.primitives import serialization
from encryption_service import hybrid_encrypt_data
import json
from datetime import datetime
from sqlalchemy import cast, DateTime

def get_transactions():
    try:
        print("[DEBUG] Starting get_transactions function")

        data = request.get_json()
        print(f"[DEBUG] Received data: {data}")

        uid = data.get('uid')
        student_id = data.get("student_id")
        timestamp_str = data.get("timestamp")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        public_key_pem = data.get("public_key")

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

        try:
            # Handle microseconds if present in timestamp
            if "." in timestamp_str:
                timestamp_str = timestamp_str.split(".")[0]
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            print(f"[DEBUG] Converted timestamp to datetime: {timestamp}")
        except ValueError as e:
            print(f"[DEBUG] Invalid timestamp format: {e}")
            return jsonify({"message": "Invalid timestamp format"}), 400

        if not first_name or not last_name or not public_key_pem:
            print("[DEBUG] Missing first name, last name, or public key")
            return jsonify({"message": "First name, last name, and public key are required"}), 400

        try:
            print(f"[DEBUG] Verifying public key for {first_name} {last_name}")
            response_code = call_check_public_key.call_check_public_key(first_name, last_name, public_key_pem)
            print(f"[DEBUG] Public key verification response code: {response_code}")
        except requests.exceptions.Timeout:
            print("[DEBUG] Timeout during public key verification")
            return jsonify({"message": "Timeout occurred while verifying public key"}), 504
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] RequestException during public key verification: {e}")
            return jsonify({"message": f"Error during public key verification: {str(e)}"}), 500

        if response_code != 200:
            print(f"[DEBUG] Public key verification failed with code: {response_code}")
            return jsonify({"message": "Verification failed"}), response_code

        if not student_id or not timestamp:
            print("[DEBUG] Missing student_id or timestamp")
            return jsonify({"message": "Student ID and timestamp are required"}), 400

        print(f"[DEBUG] Using student_id: {student_id}, timestamp: {timestamp}")

        try:
            print("[DEBUG] Establishing database connection")
            db = next(get_mks_db())
            print("[DEBUG] Database connection established successfully")
        except Exception as e:
            print(f"[DEBUG] Error establishing database connection: {e}")
            return jsonify({"message": "Database connection failed"}), 500

        try:
            print("[DEBUG] Running database query to retrieve transactions")
            transactions = (
                db.query(
                    func.concat(NewTransaction.qdate, ' ', NewTransaction.time).label("transaction_id"),
                    NewTransaction.qdate,
                    NewTransaction.time,
                    NewTransaction.location,
                    func.group_concat(NewTransaction.item).label("items"),
                    func.group_concat(NewTransaction.qty).label("quantities"),
                    func.group_concat(NewTransaction.amount).label("prices"),
                )
                .filter(
                    NewTransaction.id_number == student_id,
                    cast(func.concat(NewTransaction.qdate, ' ', NewTransaction.time), DateTime) < timestamp
                )
                .group_by(NewTransaction.qdate, NewTransaction.time, NewTransaction.location)
                .order_by(desc(NewTransaction.qdate),
                          desc(literal_column("STR_TO_DATE(pomfret_transact.time, '%H:%i:%s')")))
                .limit(10)
                .all()
            )

            print(f"[DEBUG] Retrieved transactions: {transactions}")
        except Exception as e:
            print(f"[DEBUG] Error during database query: {e}")
            return jsonify({"message": "Error retrieving transactions"}), 500

        if not transactions:
            print("[DEBUG] No transactions found")
            return jsonify({"message": "No transactions found"}), 404

        try:
            print("[DEBUG] Formatting transactions for response")
            transactions_list = [
                {
                    "transaction_id": transaction.transaction_id,
                    "qdate": transaction.qdate,
                    "time": transaction.time,
                    "location": transaction.location,
                    "items": transaction.items,
                    "quantities": transaction.quantities,
                    "prices": transaction.prices,
                }
                for transaction in transactions
            ]
            print(f"[DEBUG] Formatted transactions: {transactions_list}")
        except Exception as e:
            print(f"[DEBUG] Error during transaction formatting: {e}")
            return jsonify({"message": "Error formatting transactions"}), 500

        has_more = len(transactions_list) == 10
        print(f"[DEBUG] has_more: {has_more}")

        latest_timestamp = transactions[-1].transaction_id if transactions else None
        print(f"[DEBUG] latest_timestamp: {latest_timestamp}")

        response_dict = {
            "transactions": transactions_list,
            "has_more": has_more,
            "latest_timestamp": latest_timestamp,
        }
        print("TIMESTAMP    "+response_dict["latest_timestamp"])
        try:

            if isinstance(public_key_pem, str):
                public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            else:
                public_key = serialization.load_pem_public_key(public_key_pem)
            for transaction in response_dict['transactions']:
                transaction['qdate'] = str(transaction['qdate'])
                transaction['time'] = str(transaction['time'])
            json_string = json.dumps(response_dict)
            json_bytes = json_string.encode("utf-8")
            encrypted_result = hybrid_encrypt_data(public_key, json_bytes)
            print("[DEBUG] Response encrypted successfully")
        except Exception as e:
            print(f"[DEBUG] Error during response encryption: {e}")
            return jsonify({"message": "Error encrypting response"}), 500

        return jsonify(
            {
                "encrypted_data": encrypted_result["encrypted_data"],
                "encrypted_key": encrypted_result["encrypted_key"],
            }
        ), 200

    except Exception as e:
        print(f"[DEBUG] Error during transaction retrieval: {e}")
        return jsonify({"message": f"An error occurred while retrieving the transactions: {str(e)}"}), 500