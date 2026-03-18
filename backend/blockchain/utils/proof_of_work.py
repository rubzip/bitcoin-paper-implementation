class ProofOfWork:
    def is_valid_hash(self, block_hash: str) -> bool: ...

class ZerosPOW(ProofOfWork):
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty

    def is_valid_hash(self, block_hash: str) -> bool:
        return block_hash[:self.difficulty] == '0' * self.difficulty
