from pydantic import BaseModel


class Hello(BaseModel):
    peer_url: str


class AvailablePeers(BaseModel):
    peers: list[str]


class TransactionSchema(BaseModel):
    sender: str
    receiver: str
    amount: int
    timestamp: float


class BlockSchema(BaseModel):
    index: int
    transactions: list[TransactionSchema]
    prev_hash: str
    timestamp: float
    nonce: int
    hash: str
