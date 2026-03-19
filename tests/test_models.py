import pytest
import time
from backend.blockchain.models import Transaction, Block
from backend.blockchain.utils.hashing import Sha256Hasher

def test_transaction_to_tuple():
    tx = Transaction("Alice", "Bob", 10, 123.456)
    expected = ("Alice", "Bob", 10, 123.456)
    assert tx.to_tuple() == expected

def test_block_initialization():
    txs = [Transaction("Alice", "Bob", 10, time.time())]
    block = Block(1, txs, "prev_hash", 123.456)
    assert block.index == 1
    assert block.transactions == txs
    assert block.prev_hash == "prev_hash"
    assert block.timestamp == 123.456
    assert block.nonce == 0
    assert block.hash is not None

def test_block_hashing():
    block = Block(0, [], "0" * 64, 1.0)
    hash1 = block.hash
    block.nonce += 1
    hash2 = block.get_hash()
    assert hash1 != hash2

def test_block_str_representation():
    block = Block(0, [], "prev", 1.0)
    s = str(block)
    assert '"index": 0' in s
    assert '"prev_hash": "prev"' in s
    assert '"nonce": 0' in s
