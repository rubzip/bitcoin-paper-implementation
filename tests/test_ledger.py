import pytest
from bitcoin.blockchain.core import Ledger, NETWORK_ID
from bitcoin.blockchain.models import Transaction

@pytest.fixture
def ledger():
    return Ledger()

def test_ledger_initial_balance(ledger):
    assert ledger.get_balance("Alice") == 0

def test_ledger_apply_transaction(ledger):
    # Network gives to Alice
    tx1 = Transaction(NETWORK_ID, "Alice", 50, 1.0)
    ledger.apply_transaction(tx1)
    assert ledger.get_balance("Alice") == 50
    
    # Alice sends to Bob
    tx2 = Transaction("Alice", "Bob", 20, 2.0)
    ledger.apply_transaction(tx2)
    assert ledger.get_balance("Alice") == 30
    assert ledger.get_balance("Bob") == 20

def test_ledger_copy(ledger):
    ledger.apply_transaction(Transaction(NETWORK_ID, "Alice", 50, 1.0))
    ledger_copy = ledger.copy()
    
    # Modify copy
    ledger_copy.apply_transaction(Transaction("Alice", "Bob", 10, 2.0))
    
    assert ledger.get_balance("Alice") == 50
    assert ledger_copy.get_balance("Alice") == 40
    assert ledger.get_balance("Bob") == 0
    assert ledger_copy.get_balance("Bob") == 10
