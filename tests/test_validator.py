import pytest
from backend.blockchain.core import Ledger, Validator, NETWORK_ID
from backend.blockchain.models import Transaction, Block
from backend.blockchain.exceptions import EconomyError
from backend.blockchain.utils.hashing import Sha256Hasher

@pytest.fixture
def ledger():
    l = Ledger()
    l.apply_transaction(Transaction(NETWORK_ID, "Alice", 100, 1.0))
    return l

def test_validate_transaction_success(ledger):
    tx = Transaction("Alice", "Bob", 50, 2.0)
    # Should not raise exception
    Validator.validate_transaction(ledger, tx)

def test_validate_transaction_insufficient_funds(ledger):
    tx = Transaction("Alice", "Bob", 150, 2.0)
    with pytest.raises(EconomyError):
        Validator.validate_transaction(ledger, tx)

def test_validate_consecutive_blocks_success():
    b1 = Block(0, [], Sha256Hasher.default_hash(), 1.0)
    b1.mine()
    b2 = Block(1, [], b1.hash, 2.0)
    b2.mine()
    # Should not raise exception
    Validator.validate_consecutive_blocks(b2, b1)

def test_validate_consecutive_blocks_hash_mismatch():
    b1 = Block(0, [], Sha256Hasher.default_hash(), 1.0)
    b1.mine()
    b2 = Block(1, [], "wrong_prev_hash", 2.0)
    b2.mine()
    with pytest.raises(ValueError):
        Validator.validate_consecutive_blocks(b2, b1)
