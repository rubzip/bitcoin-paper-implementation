import pytest
from bitcoin.blockchain.core import Blockchain, NETWORK_ID
from bitcoin.blockchain.node import Node
from bitcoin.blockchain.models import Block, Transaction
from bitcoin.blockchain.exceptions import EconomyError

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

def test_blockchain_overwrite():
    bc1 = Blockchain()
    bc2 = Blockchain()
    
    # Alice mines 2 blocks in bc2
    node_alice = Node(node_id="Alice")
    node_alice.blockchain = bc2
    node_alice.mine(miner="Alice")
    node_alice.mine(miner="Alice")
    
    # bc1 is shorter (length 1), it should be overwritten by bc2 (length 3 = genesis + 2)
    assert bc1.length == 1
    assert bc2.length == 3
    
    bc1.overwrite(bc2.chain)
    assert bc1.length == 3
    assert bc1.get_balance("Alice") == 100

def test_blockchain_no_overwrite_shorter():
    bc1 = Blockchain()
    bc2 = Blockchain()
    
    # bc1 mines 1 block
    node_alice = Node(node_id="Alice")
    node_alice.blockchain = bc1
    node_alice.mine(miner="Alice")
    
    # bc2 is genesis only (length 1)
    # bc1 (length 2) should NOT be overwritten by bc2 (length 1)
    initial_hash = bc1.last_hash
    bc1.overwrite(bc2.chain)
    assert bc1.length == 2
    assert bc1.last_hash == initial_hash
