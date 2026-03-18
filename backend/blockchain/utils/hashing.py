import hashlib


class Hasher:
    @classmethod
    def hash(cls, x: str) -> str: ...

    @classmethod
    def default_hash(cls) -> str: ...

class Sha256Hasher(Hasher):
    @classmethod
    def hash(cls, x: str) -> str:
        return hashlib.sha256(x.encode()).hexdigest()

    @classmethod
    def default_hash(cls) -> str:
        return '0' * 64
