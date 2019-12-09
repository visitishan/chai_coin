import functools
import hashlib
import json
#from collections import OrderedDict

import hash_util
from block import Block
from transaction import Transaction
from verification import Verification


# Adding mining reward for miners
MINING_REWARD = 10  #hardcoding the value to 10 for now


class Blockchain:
    def __init__(self, hosting_node_id):
        # Initializing our (empty) blockchain list
        genesis_block = Block(0,'', [], 100, 0)    
        # Initializing our (empty) blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id


        #owner = 'Ishan'
        #participants = {'Ishan'}    #adding users to a set to avoid duplicates


    def load_data(self):
        try:
            with open('blockchain.txt', mode = 'r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    #converted_tx = [OrderedDict([('sender',tx['sender']), ('recipient',tx['recipient']), ('amount',tx['amount'])]) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    #updated_block = {
                    #    'previous_hash':block['previous_hash'],
                    #    'index':block['index'],
                    #    'proof':block['proof'],
                    #    'transactions': [OrderedDict([('sender',tx['sender']), ('recipient',tx['recipient']), ('amount',tx['amount'])]) for tx in block['transactions']]
                    #}
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    #updated_transaction = OrderedDict([('sender',tx['sender']), ('recipient',tx['recipient']), ('amount',tx['amount'])])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        except (IOError, IndexError):
            print("Handled Exception!!")
        finally :
            print('clean kar diya!')




    def save_data(self):
        try:
            with open('blockchain.txt', mode = 'w') as f:
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.chain]]
                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(savable_tx))
        except IOError:
            print('Saving Failed')


    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        verifier = Verification()
        while not verifier.valid_proof(self.open_transactions,last_hash,proof):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender==participant] for block in self.chain]
        open_tx_sender = [tx.amount for tx in self.open_transactions if tx.sender ==participant]
        tx_sender.append(open_tx_sender)
        #amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        amount_sent = 0
        #fetches the total amount of coins sent
        for tx in tx_sender:
            if len(tx)>0:
                amount_sent += tx[0]
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient==participant] for block in self.chain]
        #amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)    
        amount_received = 0
        for tx in tx_recipient:
            if len(tx)>0:
                amount_received += tx[0]
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.chain) < 1:
            return None
        return self.chain[-1]


    # This function accepts two arguments.
    # One required one (transaction_amount) and one optional one (last_transaction)
    # The optional one is optional because it has a default value => [1]


    def add_transaction(self, recipient, sender, amount=1.0):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        #transaction = {
        #    'sender': sender,
        #    'recipient': recipient,
        #    'amount': amount
        #}
        transaction = Transaction(sender, recipient, amount)
        verifier = Verification()
        #transaction = OrderedDict([('sender',sender), ('recipient',recipient), ('amount',amount)])
        if verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            #participants.add(sender)
            #participants.add(recipient)
            self.save_data()
            return True
        else:
            return False


    def mine_block(self):
        last_block = self.chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        #reward_transaction = {
        #    'sender':"MINING",
        #    'recipient':owner,
        #    'amount':MINING_REWARD
        #}
        reward_transaction = Transaction("MINING", self.hosting_node, MINING_REWARD)
        #reward_transaction = OrderedDict([('sender','MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(len(self.chain), hashed_block, copied_transactions, proof)
        #block = {
        #    'previous_hash':hashed_block,
        #    'index':len(blockchain),
        #    'transactions':copied_transactions,
        #    'proof':proof
        #}
        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return True

