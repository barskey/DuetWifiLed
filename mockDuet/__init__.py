from flask import Flask, jsonify

app = Flask(__name__)

from mockDuet import routes

if __name__ == 'test_status':
    app.run(debug=True)