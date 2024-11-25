from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from functools import wraps

app = Flask(__name__)

# Firebase Admin SDK initialization
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

# Pyrebase configuration for client-side auth
firebase_config = {
    "apiKey": "AIzaSyBUR_OsSCIZHwJNL4ihbFhIAzmh9-xdpNQ",
    "authDomain": "hashscope-c62cf.firebaseapp.com",
    "projectId": "hashscope-c62cf",
    "storageBucket": "hashscope-c62cf.firebasestorage.app",
    "messagingSenderId": "126504332452",
    "appId": "1:126504332452:web:9c8c84a0a010d2e3954a31",
    "measurementId": "G-76YG7CDJHM",
    "databaseURL": "https://hashscope-c62cf-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(firebase_config)
auth_client = firebase.auth()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        # Create user using Firebase Admin SDK
        user = auth.create_user(
            email=email,
            password=password
        )
        return jsonify({"message": "User created successfully", "uid": user.uid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        # Authenticate user using Pyrebase
        user = auth_client.sign_in_with_email_and_password(email, password)
        id_token = user['idToken']
        return jsonify({"message": "Login successful", "id_token": id_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401
    
@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    id_token = data.get('id_token')

    try:
        # Verify ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        return jsonify({"message": "Token is valid", "uid": decoded_token['uid']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 403
    

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_token = request.headers.get('Authorization')
        if not id_token:
            return jsonify({"error": "Token is missing"}), 403
        
        try:
            auth.verify_id_token(id_token)
        except Exception:
            return jsonify({"error": "Invalid token"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({"message": "Access granted to protected route"})