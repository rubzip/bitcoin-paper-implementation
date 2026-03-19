from collections import defaultdict
from typing import List
import json

from backend.blockchain.utils.hashing import Hasher, Sha256Hasher
from backend.blockchain.utils.proof_of_work import ProofOfWork, ZerosPOW
from backend.blockchain.models import Block, Transaction
from backend.blockchain.exceptions import EconomyError

NETWORK_ID = "NETWORK"


class Blockchain:
    def __init__(self):
        self.difficulty: int = 4
        self.pow = ZerosPOW(self.difficulty)
        self.hasher = Sha256Hasher
        self.__chain: List[Block] = []
        
        self.__create_genesis_block()
        self.__economy = self.compute_economy()
    
    def __create_genesis_block(self):
        genesis = Block(0, [], self.hasher.default_hash())
        genesis.mine(self.pow)
        self.__chain.append(genesis)
    
    def add_block(self, block: Block):
        self._validate_consecutive_blocks(block, self.last_block)
        new_economy = self._update_economy(block, self.__economy)

        self.__chain.append(block)
        self.__economy = new_economy

    @property
    def last_block(self) -> Block:
        return self.__chain[-1]
    
    @property
    def chain(self) -> List[Block]:
        return self.__chain
    
    @property
    def length(self) -> int:
        return len(self.__chain)
    
    @property
    def last_hash(self) -> str:
        return self.last_block.hash
    
    def compute_economy(self) -> defaultdict:
        economy = defaultdict(int)
        for block in self.__chain:
            economy = self._update_economy(block, economy)
        return economy
        
    def _update_economy(self, block: Block, prev_economy: defaultdict) -> defaultdict:
        economy = prev_economy.copy()
        for tx in block.transactions:
            economy[tx.sender] -= tx.amount
            economy[tx.receiver] += tx.amount
            if tx.sender != NETWORK_ID and economy[tx.sender] < 0:
                raise EconomyError(f"Invalid transaction: sender {tx.sender} has insufficient balance. Current balance: {economy[tx.sender]}, transaction amount: {tx.amount}")
        return economy
    
    def _validate_consecutive_blocks(self, block: Block, prev_block: Block):
        if block.hash != block.get_hash():
            raise
        if block.prev_hash != prev_block.get_hash():
            raise
        if not self.pow.is_valid_hash(block.hash):
            raise
    
    def validate_full_chain(self):
        if self.length == 0:
            raise
        if self.__chain[0].prev_hash != self.hasher.default_hash():
            raise
        n = len(self.__chain)
        for i in range(n - 1):
            block, prev_block = self.__chain[i+1], self.__chain[i]
            self._validate_consecutive_blocks(block, prev_block)
            if block.index != i:
                raise
        self.compute_economy()
    
    def get_balance(self, user: str) -> int:
        return self.__economy.get(user)
    
    def overwrite(self, other: "Blockchain"):
        if self.length >= other.length:
            raise # or return? maybe is not an error, just do nothing
        other.validate_full_chain()
        self.__chain = other.chain
        self.__economy = self.compute_economy()
