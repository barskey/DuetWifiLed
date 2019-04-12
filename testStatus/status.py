from flask import Flask, jsonify
import json
app = Flask(__name__)

@app.route("/rr_status", methods=['GET', 'POST'])
def test_ping():
	print('ping received')
	status = json.load(open('data.json'))
	return jsonify(status)