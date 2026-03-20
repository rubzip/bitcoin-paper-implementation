import pytest
from bitcoin.blockchain.core import Ledger, Validator, NETWORK_ID
from bitcoin.blockchain.models import Transaction, Block
from bitcoin.blockchain.exceptions import EconomyError
from bitcoin.blockchain.utils.hashing import Sha256Hasher

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

def test_validate_full_chain_invalid_index():
    b1 = Block(0, [], Sha256Hasher.default_hash(), 1.0)
    b1.mine()
    b2 = Block(2, [], b1.hash, 2.0) # Wrong index (should be 1)
    b2.mine()
    with pytest.raises(ValueError) as excinfo:
        Validator.validate_full_chain([b1, b2])
    assert "index mismatch" in str(excinfo.value)

def test_validate_transaction_network_id(ledger):
    # Network ID bypasses balance check
    tx = Transaction(NETWORK_ID, "Alice", 1000000, 1.0)
    # Should NOT raise EconomyError
    Validator.validate_transaction(ledger, tx)
