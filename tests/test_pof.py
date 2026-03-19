import pytest
from backend.blockchain.utils.proof_of_work import ZerosPOW
from backend.blockchain.utils.hashing import Sha256Hasher


def test_zeros_pow():
    assert not ZerosPOW.is_valid_hash("00")
    assert not ZerosPOW.is_valid_hash("100000000")
    assert ZerosPOW.is_valid_hash("0000")
    assert ZerosPOW.is_valid_hash("00000")
    assert ZerosPOW.is_valid_hash(Sha256Hasher.default_hash())
