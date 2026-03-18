from typing import List
import time

from backend.blockchain.core import Blockchain, NETWORK_ID
from backend.blockchain.models import Block, Transaction


class Node:
    def __init__(self, node_id: str, difficulty: int = 4, mining_reward: int = 50):
        self.node_id = node_id
        self.blockchain = Blockchain(difficulty)
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = mining_reward

    def add_transaction(self, sender: str, receiver: str, amount: int):
        if sender != NETWORK_ID and self.blockchain.get_balance(sender) < amount:
            raise
        
        tx = Transaction(sender, receiver, amount, time.time())
        self.pending_transactions.append(tx)

    def mine(self, miner: str):
        reward = Transaction(NETWORK_ID, miner, self.mining_reward, time.time())
        transactions = self.pending_transactions + [reward]
        
        new_block = Block(self.blockchain.length, transactions, self.blockchain.last_hash)
        new_block.mine(self.blockchain.difficulty)
        
        try:
            self.blockchain.add_block(new_block)
            self.pending_transactions = []
        except Exception as e:
            raise

    def update(self, other_blockchain: Blockchain):
        self.blockchain.overwrite(other_blockchain)
