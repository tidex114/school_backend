import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

VALIDATE_JWT_URL = os.getenv('POMCARD_BACKEND_HOST') + '/validate_jwt'  # Ensure this is set in your .env file


def validate_jwt_token(token, uid, full_name):
    """
    Validates a JWT token by calling the /validate_jwt route.

    Args:
        token (str): The JWT token to validate.
        uid (str): The user ID (subject) to validate against.
        full_name (str): The full name to validate against.

    Returns:
        bool: True if the token is valid, False otherwise.
        dict: The response data from the validation route.
    """
    try:
        if not VALIDATE_JWT_URL:
            raise ValueError("VALIDATE_JWT_URL is not configured in the environment variables")

        # Make a POST request to the validation endpoint
        response = requests.post(
            VALIDATE_JWT_URL,
            json={
                'token': token,
                'uid': uid,
                'full_name': full_name
            }
        )

        # If the validation is successful, return True
        if response.status_code == 200:
            return True, response.json()

        # Otherwise, return False with the error message
        return False, response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error during token validation: {e}")
        return False, {'message': 'An error occurred while validating the token'}
