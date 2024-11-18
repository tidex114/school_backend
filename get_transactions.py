from flask import request, jsonify
from sqlalchemy import desc
from database import get_db
from models import Transaction
from calls import call_check_public_key
import requests
from cryptography.hazmat.primitives import serialization
from encryption_service import hybrid_encrypt_data
import json
def get_transactions():
    try:
        # Get the request data
        data = request.get_json()
        student_id = data.get('student_id')
        timestamp = data.get('timestamp')
        public_key_pem = data.get('public_key')
        email = data.get('email')


        if not email or not public_key_pem:
            return jsonify({'message': 'Email and public key are required'}), 400

        try:
            response_code = call_check_public_key.call_check_public_key(email, public_key_pem)
        except requests.exceptions.Timeout:
            return jsonify({'message': 'Timeout occurred while verifying public key'}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({'message': f'Error during public key verification: {str(e)}'}), 500

        if response_code != 200:
            return jsonify({'message': 'Verification failed'}), response_code



        print(f"Got ts: {timestamp}")
        # Ensure student_id and timestamp are provided
        if not student_id or not timestamp:
            return jsonify({'message': 'Student ID and timestamp are required'}), 400

        # Establish a connection to the database
        db = next(get_db())

        # Look up the user's transactions in the database using SQLAlchemy
        transactions = (
            db.query(Transaction)
            .filter(Transaction.student_id == student_id, Transaction.transaction_date < timestamp)
            .order_by(desc(Transaction.transaction_date))
            .limit(10)
            .all()
        )

        if not transactions:
            return jsonify({'message': 'No transactions found'}), 404

        # Check if there are more transactions beyond the retrieved ones
        if len(transactions) == 10:
            last_transaction_date = transactions[-1].transaction_date
            more_transactions = (
                db.query(Transaction)
                .filter(Transaction.student_id == student_id, Transaction.transaction_date < last_transaction_date)
                .order_by(desc(Transaction.transaction_date))
                .first()
            )
            has_more = more_transactions is not None
        else:
            has_more = False

        # Create a response containing the transactions
        transactions_list = [
            {
                'id': transaction.id,
                'student_id': transaction.student_id,
                'transaction_place': transaction.transaction_place,
                'transaction_sum': transaction.transaction_sum,
                'items': transaction.items,
                'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            for transaction in transactions
        ]

        # Get the latest transaction timestamp
        latest_timestamp = transactions[-1].transaction_date.strftime('%Y-%m-%d %H:%M:%S') if transactions else None
        response_dict = {
            'transactions': transactions_list,
            'has_more': has_more,
            'latest_timestamp': latest_timestamp
        }
        if isinstance(public_key_pem, str):
            public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
        else:
            public_key = serialization.load_pem_public_key(public_key_pem)

        json_string = json.dumps(response_dict)
        json_bytes = json_string.encode('utf-8')
        encrypted_result = hybrid_encrypt_data(public_key, json_bytes)

        return jsonify({'encrypted_data': encrypted_result['encrypted_data'],
                        'encrypted_key': encrypted_result['encrypted_key']}), 200


    except Exception as e:
        print(f"Error during transaction retrieval: {e}")
        return jsonify({'message': 'An error occurred while retrieving the transactions'}), 500
