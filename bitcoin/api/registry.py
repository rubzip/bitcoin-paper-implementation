from typing import Set
import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from bitcoin.api.schemas import AvailablePeers, Hello

available_peers: Set[str] = set()

async def check_peers(validation_time: float = 60.0):
    """Periodic task to ping peers and remove unresponsive ones"""
    while True:
        await asyncio.sleep(validation_time)
        async with httpx.AsyncClient() as client:
            peers_to_remove = []
            for peer_url in list(available_peers):
                try:
                    response = await client.get(peer_url, timeout=5.0)
                    if response.status_code != 200:
                        peers_to_remove.append(peer_url)
                except httpx.RequestError:
                    peers_to_remove.append(peer_url)
            
            for peer_url in peers_to_remove:
                available_peers.discard(peer_url)

@asynccontextmanager
async def lifespan(app: FastAPI):
    bg_task = asyncio.create_task(check_peers())
    yield
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

peer_handler = FastAPI(lifespan=lifespan)

peer_handler.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@peer_handler.get("/")
async def get_status():
    return {"status": "Central node is running", "api": "Registry"}

@peer_handler.post("/hello")
async def say_hello(payload: Hello) -> dict[str, str]:
    peer_url = payload.peer_url
    available_peers.add(peer_url)
    return {"message": f"Hello from central node! Received hello from {peer_url}"}

@peer_handler.get("/peers", response_model=AvailablePeers)
async def get_peers() -> AvailablePeers:
    return AvailablePeers(peers=list(available_peers))
