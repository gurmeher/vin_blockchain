import time
import hashlib
import json

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
        self.pending_transactions.append(transaction)
        return self.get_previous_block()["index"] + 1
    
    #hash a block
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    #makes it so mining requires work to get a new block that works
    def proof_of_work(self, previous_nonce, previous_hash):
        """
        Simple Proof of Work:
        - Find a nonce such that hash(previous_nonce, previous_hash, nonce) starts with '0000'
        - This makes mining require real computational work
        """
        nonce = 0
        while True:
            guess = f"{previous_nonce}{previous_hash}{nonce}".encode()
            if hashlib.sha256(guess).hexdigest()[:4] == "0000":
                return nonce
            nonce += 1

    #retrieve ownership history for a specific VIN
    def get_vin_history(self, vin):
        history = [
            txn
            for block in self.chain
            for txn in block["transactions"]
            if txn.get("vin") == vin
        ]

        history.extend([txn for txn in self.pending_transactions if txn.get("vin") == vin])
        return history

    
    #get the latest state of a VIN
    def get_latest_vin_state(self, vin):
        history = self.get_vin_history(vin)
        if not history:
            return {"exists": False}

        owner = None
        last_mileage = None
        registered = False

        for txn in history:
            ttype = txn.get("type")
            if ttype == "register_vehicle":
                registered = True
                owner = txn["owner"]
                last_mileage = 0
            elif registered and ttype == "transfer_ownership":
                owner = txn["to"]
            elif registered and ttype == "odometer_update":
                last_mileage = txn["mileage"]

        return {
            "exists": registered,
            "owner": owner if registered else None,
            "last_mileage": last_mileage if registered else None
        }