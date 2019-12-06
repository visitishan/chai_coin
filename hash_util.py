import hashlib
import json


def hash_string_256(string):
	return hashlib.sha256(string).hexdigest()

def hash_block(block):
    #return '-'.join(str([block[key] for key in block]))
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort = True).encode())
