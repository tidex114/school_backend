from flask import Flask
from get_barcode import get_barcode

app = Flask(__name__)

# Register route for getting barcode
app.add_url_rule('/get_barcode', 'get_barcode', get_barcode, methods=['POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5002)
