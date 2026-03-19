import pytest
from backend.blockchain.core import Blockchain, NETWORK_ID
from backend.blockchain.models import Block, Transaction
from backend.blockchain.exceptions import EconomyError

@pytest.fixture
def bc():
    return Blockchain()

def test_blockchain_initialization(bc):
    assert bc.length == 1
    assert bc.last_block.index == 0

def test_add_block_success(bc):
    # First give some money in a block (mined by Bob)
    reward = Transaction(NETWORK_ID, "Alice", 50, 1.0)
    b1 = Block(1, [reward], bc.last_hash, 2.0)
    b1.mine()
    bc.add_block(b1)
    
    assert bc.length == 2
    assert bc.get_balance("Alice") == 50

def test_add_block_invalid_tx(bc):
    # Alice tries to spend money she doesn't have
    tx = Transaction("Alice", "Bob", 10, 1.0)
    b1 = Block(1, [tx], bc.last_hash, 2.0)
    b1.mine()
    with pytest.raises(EconomyError):
        bc.add_block(b1)
