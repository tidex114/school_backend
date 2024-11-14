import requests
from os import getenv

def call_check_public_key(email, public_key):
    url = f'http://{getenv("POMCARD_BACKEND_HOST")}/check_public_key'
    headers = {'Content-Type': 'application/json'}
    data = {
        'email': email,
        'public_key': public_key
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None