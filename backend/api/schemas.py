from pydantic import BaseModel

class Hello(BaseModel):
    peer_url: str

class AvailablePeers(BaseModel):
    peers: list[str]
