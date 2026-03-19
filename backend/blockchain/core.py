from collections import defaultdict
from typing import List


from backend.blockchain.utils.hashing import Sha256Hasher
from backend.blockchain.utils.proof_of_work import ZerosPOW
from backend.blockchain.models import Block, Transaction
from backend.blockchain.exceptions import EconomyError
from backend.blockchain.constants import NETWORK_ID



class Ledger:
    def __init__(self, balances: defaultdict = None):
        self.__balances = balances or defaultdict(int)

    def apply_transaction(self, tx: Transaction):
        self.__balances[tx.sender] -= tx.amount
        self.__balances[tx.receiver] += tx.amount

    def apply_block(self, block: Block):
        for tx in block.transactions:
            self.apply_transaction(tx)

    def get_balance(self, user: str) -> int:
        return self.__balances.get(user, 0)

    def copy(self) -> "Ledger":
        return Ledger(self.__balances.copy())


class Validator:
    @classmethod
    def validate_transaction(cls, ledger: Ledger, transaction: Transaction):
        balance = ledger.get_balance(transaction.sender)
        if transaction.sender != NETWORK_ID and balance < transaction.amount:
            raise EconomyError(f"Sender '{transaction.sender}' has insufficient balance.\n\tCurrent balance: {balance}\n\tTransaction amount: {transaction.amount}")
    
    @classmethod
    def validate_consecutive_blocks(cls, block: Block, prev_block: Block):
        if block.hash != block.get_hash():
            raise ValueError("Invalid block hash")
        if block.prev_hash != prev_block.hash:
            raise ValueError("Block prev_hash does not match previous block hash")
        if not ZerosPOW.is_valid_hash(block.hash):
            raise ValueError("Block hash does not satisfy Proof of Work")
    
    @classmethod
    def validate_full_chain(cls, chain: List[Block]):
        if len(chain) == 0:
            raise ValueError("Chain is empty!")
        if chain[0].prev_hash != Sha256Hasher.default_hash():
            raise ValueError("Genesis block has invalid prev_hash")
        
        n = len(chain)
        for i in range(1, n):
            block, prev_block = chain[i], chain[i-1]
            cls.validate_consecutive_blocks(block, prev_block)
            if block.index != i:
                raise ValueError(f"Block index mismatch at {i}")


class Blockchain:
    def __init__(self):
        self.__chain: List[Block] = []
        self.__ledger = Ledger()
        self.create_genesis_block()
    
    @classmethod
    def from_chain(cls, chain: List[Block]):
        blockchain = cls()
        Validator.validate_full_chain(chain)
        blockchain.__chain = chain
        blockchain.__ledger = Ledger()
        for block in chain:
            blockchain.__ledger.apply_block(block)
        return blockchain
    
    def create_genesis_block(self):
        if self.length > 0:
            raise ValueError("Genesis block already exists.")
        genesis = Block(0, [], Sha256Hasher.default_hash())
        genesis.mine()
        self.__chain.append(genesis)
        self.__ledger.apply_block(genesis)
    
    def add_block(self, block: Block):
        last_block = self.__chain[-1]
        Validator.validate_consecutive_blocks(block, last_block)
        
        new_ledger = self.__ledger.copy()
        for tx in block.transactions:
            Validator.validate_transaction(new_ledger, tx)
            new_ledger.apply_transaction(tx)

        self.__chain.append(block)
        self.__ledger = new_ledger

    def overwrite(self, chain: List[Block]):
        if self.length >= len(chain):
            return
        
        new_bc = Blockchain.from_chain(chain)
        self.__chain = new_bc.chain
        self.__ledger = new_bc.__ledger
        del new_bc

    @property
    def chain(self) -> List[Block]:
        return self.__chain.copy()
    
    @property
    def length(self) -> int:
        return len(self.__chain)
    
    @property
    def last_block(self) -> Block:
        return self.__chain[-1]
    
    @property
    def last_hash(self) -> str:
        return self.last_block.hash
    
    def get_balance(self, user: str) -> int:
        return self.__ledger.get_balance(user)

    def validate_transaction(self, tx: Transaction):
        Validator.validate_transaction(self.__ledger, tx)
