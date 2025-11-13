from flask import Flask, jsonify, request
import hashlib
import time

app = Flask(__name__)

@app.route("/", methods=["GET"]) # when someone accesses the root URL with a GET request, do this
def home():
    return jsonify({"message": "CarChain API is running"}), 200

#---------------------- Blockchain Class ---------------------#
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_block(previous_hash="0", nonce=1)
    
    #makes the block and adds to chain
    def create_block(self, nonce, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.pending_transactions,
            "nonce": nonce,
            "previous_hash": previous_hash
        }

        self.pending_transactions = []

        self.chain.append(block)
        return block
    
    #return the last one in the chain
    def get_previous_block(self):
        return self.chain[-1]
    
    #record new transaction
    def add_transaction(self, transaction):
        """
        transaction = {
            "vin": "...",
            "prev_owner": "...",
            "new_owner": "...",
            "timestamp": ...
        }
        """
        self.pending_transactions.append(transaction)
        return self.get_previous_block()["index"] + 1
    
    #hash a block
    @staticmethod
    def hash(block):
        encoded = str(block).encode()
        return hashlib.sha256(encoded).hexdigest()
    
    def proof_of_work(self):
        return 1

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


#add a vin transaction, accepts data like:
'''{
  "vin": "1HGCM82633A123456",
  "prev_owner": "Alice",
  "new_owner": "Bob",
  "timestamp": 1713050000
}'''
@app.route("/transaction/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    required_fields = ["vin", "prev_owner", "new_owner", "timestamp"]
    if not all(field in values for field in required_fields):
        return jsonify({"error": "Missing transaction fields"}), 400

    index = blockchain.add_transaction(values)

    return jsonify({
        "message": f"Transaction will be added to Block {index}"
    }), 201


#turn pending transactions into a block
@app.route("/mine", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = blockchain.hash(previous_block)

    #in future we'll run real PoW here
    nonce = blockchain.proof_of_work()

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
def get_vin_history(vin):
    history = []

    for block in blockchain.chain:
        for tx in block["transactions"]:
            if tx["vin"] == vin:
                history.append(tx)

    return jsonify({
        "vin": vin,
        "history": history,
        "records_found": len(history)
    }), 200

#---------------------- Run the app ---------------------#
if __name__ == "__main__": #if file run, name becomes main and this will run
    app.run(host="0.0.0.0", port=3000)
