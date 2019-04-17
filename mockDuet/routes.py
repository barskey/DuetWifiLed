import json
from mockDuet import app
from flask import jsonify

@app.route("/rr_status", methods=['GET', 'POST'])
def test_ping():
	print('ping received')
	s = json.load(open('mockDuet/data.json'))
	return jsonify(s)