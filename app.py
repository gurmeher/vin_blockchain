from flask import Flask, jsonify, request
from blockchain import Blockchain
import hashlib
import time
import json

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "CarChain API is running"}), 200

blockchain = Blockchain()

#---------------------- API Endpoints ---------------------#
#sends back the entire blockchain as a JSON response
@app.route("/chain", methods=["GET"])
def get_chain():
    response = {
        "length": len(blockchain.chain),
        "chain": blockchain.chain
    }
    return jsonify(response), 200


#turn pending transactions into a block
@app.route("/mine", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = blockchain.hash(previous_block)
    nonce = blockchain.proof_of_work(previous_block["nonce"], previous_hash)

    block = blockchain.create_block(nonce, previous_hash)

    response = {
        "message": "Block mined successfully!",
        "index": block["index"],
        "transactions": block["transactions"],
        "nonce": block["nonce"],
        "previous_hash": block["previous_hash"]
    }
    return jsonify(response), 200


#retrieve the ownership history of a specific VIN
@app.route("/vin/<vin>", methods=["GET"])
def get_vin_history_endpoint(vin):
    history = blockchain.get_vin_history(vin)
    return jsonify({
        "vin": vin,
        "history": history,
        "records_found": len(history)
    }), 200


#register a new vehicle VIN
@app.route("/vin/register", methods=["POST"])
def register_vin():
    data = request.get_json()

    required = ["vin", "owner"]
    if not data or not all(field in data for field in required):
        return jsonify({"error": "Missing fields"}), 400

    state = blockchain.get_latest_vin_state(data["vin"])

    if state["exists"]:
        return jsonify({"error": "VIN already registered"}), 400
    
    transaction = {
        "type": "register_vehicle",
        "vin": data["vin"],
        "owner": data["owner"],
        "timestamp": time.time()
    }

    index = blockchain.add_transaction(transaction)
    return jsonify({
        "message": "VIN registration added to pending transactions",
        "will_be_added_to_block": index
    }), 201

#transfer ownership of a vehicle VIN
@app.route("/vin/transfer", methods=["POST"])
def transfer_vin():
    data = request.get_json()

    required = ["vin", "from_owner", "to_owner"]
    if not data or not all(field in data for field in required):
        return jsonify({"error": "Missing fields"}), 400

    state = blockchain.get_latest_vin_state(data["vin"])

    if not state["exists"]:
        return jsonify({"error": "VIN not registered"}), 400

    if state["owner"] != data["from_owner"]:
        return jsonify({"error": "Transfer denied: incorrect owner"}), 403

    transaction = {
        "type": "transfer_ownership",
        "vin": data["vin"],
        "from": data["from_owner"],
        "to": data["to_owner"],
        "timestamp": time.time()
    }

    index = blockchain.add_transaction(transaction)

    return jsonify({
        "message": "Ownership transfer added to pending transactions",
        "will_be_added_to_block": index
    }), 201


#update odometer reading for a vehicle VIN
@app.route("/vin/odometer", methods=["POST"])
def odometer_update():
    data = request.get_json()

    required = ["vin", "mileage"]
    if not data or not all(field in data for field in required):
        return jsonify({"error": "Missing fields"}), 400

    state = blockchain.get_latest_vin_state(data["vin"])

    if not state["exists"]:
        return jsonify({"error": "VIN not registered"}), 400

    # Odometer must increase
    if state["last_mileage"] is not None and data["mileage"] < state["last_mileage"]:
        return jsonify({"error": "Invalid mileage: cannot decrease"}), 400

    transaction = {
        "type": "odometer_update",
        "vin": data["vin"],
        "mileage": data["mileage"],
        "timestamp": time.time()
    }

    index = blockchain.add_transaction(transaction)

    return jsonify({
        "message": "Odometer update added to pending transactions",
        "will_be_added_to_block": index
    }), 201


#---------------------- Run the app ---------------------#
if __name__ == "__main__": #if file run, name becomes main and this will run
    app.run(host="0.0.0.0", port=3000)
