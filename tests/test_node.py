import pytest
from backend.blockchain.node import Node
from backend.blockchain.core import NETWORK_ID
from backend.blockchain.exceptions import EconomyError

@pytest.fixture
def node():
    return Node(node_id="Alice")

def test_node_mining_reward(node):
    node.mine(miner="Alice")
    assert node.blockchain.get_balance("Alice") == 50

def test_node_transaction_cycle(node):
    node.mine(miner="Alice") # Alice gets 50
    node.add_transaction("Alice", "Bob", 20)
    assert len(node.pending_transactions) == 1
    
    node.mine(miner="Alice") # Alice gets another 50, -20 sent to Bob = 80 total
    assert node.blockchain.get_balance("Alice") == 80
    assert node.blockchain.get_balance("Bob") == 20
    assert len(node.pending_transactions) == 0

def test_node_invalid_transaction(node):
    with pytest.raises(EconomyError):
        node.add_transaction("Alice", "Bob", 100)
