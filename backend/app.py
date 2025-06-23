from flask import Flask, request, jsonify
from flask_cors import CORS  # To handle cross-origin requests
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can communicate with backend

import routes

if __name__ == '__main__':
    app.run(debug=True)  # Runs on http://127.0.0.1:5000 by default
