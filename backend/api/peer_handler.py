from typing import List
from fastapi import FastAPI
import requests
from app.api.constant import PEER_PORTS


peer_handler = FastAPI()
avaliable_peers = set()


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

@peer_handler.