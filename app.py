from flask import Flask
from get_barcode import get_barcode
from get_profile_image import get_profile_image
from get_transactions import get_transactions

app = Flask(__name__)

# Register route for getting barcode
app.add_url_rule('/get_barcode', 'get_barcode', get_barcode, methods=['POST'])
app.add_url_rule('/get_profile_image', 'get_profile_image', get_profile_image, methods=['POST'])
app.add_url_rule('/get_transactions', 'get_transactions', get_transactions, methods=['POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5002)
