import time
from typing import List
import json

from bitcoin.blockchain.utils.proof_of_work import ZerosPOW
from bitcoin.blockchain.utils.hashing import Sha256Hasher


class Transaction:
    def __init__(self, sender: str, receiver: str, amount: int, timestamp: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp

    def to_tuple(self) -> tuple:
        return (self.sender, self.receiver, self.amount, self.timestamp)

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }


class Block:
    def __init__(
        self,
        index: int,
        transactions: List[Transaction],
        prev_hash: str,
        timestamp: float = None,
    ):
        self.index = index
        self.transactions = sorted(transactions, key=lambda x: x.timestamp)
        self.prev_hash = prev_hash
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = self.get_hash()

    def get_hash(self) -> str:
        content = str(self)
        return Sha256Hasher.hash(content)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash
        }

    def mine(self):
        while not ZerosPOW.is_valid_hash(self.hash):
            self.nonce += 1
            self.hash = self.get_hash()
        return self.hash

    def __str__(self):
        tx_dicts = [tx.to_tuple() for tx in self.transactions]
        content = json.dumps(
            {
                "index": self.index,
                "prev_hash": self.prev_hash,
                "timestamp": self.timestamp,
                "transactions": tx_dicts,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return content
