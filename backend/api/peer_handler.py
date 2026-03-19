from typing import List, Set
from fastapi import FastAPI
import requests
from app.api.constant import PEER_PORTS


peer_handler = FastAPI()
avaliable_peers: Set[str] = set()


@peer_handler.get("/")
def get_status():
    return {"status": "Central node is running"}

@peer_handler.post("/hello")
def say_hello(port: str):
    avaliable_peers.add(port)
    return {"message": f"Hello from central node! Received hello from port {port}"}

@peer_handler.get("/peers")
def get_peers():
    return {"peers": list(avaliable_peers)}

def check_peers():
    for peer_url in list(avaliable_peers):
        try:
            response = requests.get(peer_url)
            if response.status_code != 200:
                avaliable_peers.remove(peer_url)
        except requests.exceptions.RequestException:
            avaliable_peers.remove(peer_url)


# Add chron job to ping peers every 30 seconds