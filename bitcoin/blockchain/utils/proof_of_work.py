from abc import ABC, abstractmethod


class ProofOfWork(ABC):
    @classmethod
    @abstractmethod
    def is_valid_hash(cls, block_hash: str) -> bool: ...


class ZerosPOW(ProofOfWork):
    @classmethod
    def is_valid_hash(cls, block_hash: str) -> bool:
        return block_hash[:4] == 4 * "0"
