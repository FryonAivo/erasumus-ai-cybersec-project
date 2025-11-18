import json
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def server_status():
    return jsonify({
        'status': 'online',
        'message': 'Phishing Detection API is running',
        'endpoints': {
            'predict': '/predict (POST)',
            'status': '/ (GET)'
        }
    })

@app.route('/predict', methods=['POST'])
def predict()