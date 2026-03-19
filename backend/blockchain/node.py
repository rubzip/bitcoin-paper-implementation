from typing import List
import time

from backend.blockchain.core import Blockchain, NETWORK_ID
from backend.blockchain.models import Block, Transaction
from backend.blockchain.exceptions import MiningError, EconomyError
from backend.blockchain.constants import MINING_REWARD, NETWORK_ID


class Node:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.blockchain = Blockchain()
        self.pending_transactions: List[Transaction] = []

    def add_transaction(self, sender: str, receiver: str, amount: int):
        tx = Transaction(sender, receiver, amount, time.time())
        self.blockchain.validate_transaction(tx)
        self.pending_transactions.append(tx)

    def mine(self, miner: str):
        reward = Transaction(NETWORK_ID, miner, MINING_REWARD, time.time())
        transactions = self.pending_transactions + [reward]
        
        new_block = Block(self.blockchain.length, transactions, self.blockchain.last_hash)
        new_block.mine()
        
        try:
            self.blockchain.add_block(new_block)
            self.pending_transactions = []
        except Exception as e:
            raise MiningError(f"Mining failed: {str(e)}")

    def update(self, other_blockchain: Blockchain):
        self.blockchain.overwrite(other_blockchain)
