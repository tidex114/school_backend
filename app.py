from flask import Flask
from gets.get_barcode import get_barcode
from gets.get_profile_image import get_profile_image
from gets.get_transactions_new import get_transactions
from gets.get_balance import get_balance

app = Flask(__name__)

# Register route for getting barcode
app.add_url_rule('/get_barcode', 'get_barcode', get_barcode, methods=['POST'])
app.add_url_rule('/get_profile_image', 'get_profile_image', get_profile_image, methods=['POST'])
app.add_url_rule('/get_transactions', 'get_transactions', get_transactions, methods=['POST'])
app.add_url_rule('/get_balance', 'get_balance', get_balance, methods=['POST'])


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5002)
