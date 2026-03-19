from typing import Set
import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager

from backend.api.schemas import AvailablePeers, Hello

# Set of available peer URLs
available_peers: Set[str] = set()

async def check_peers(validation_time: float = 60.0):
    """Periodic task to ping peers and remove unresponsive ones"""
    while True:
        await asyncio.sleep(validation_time)
        async with httpx.AsyncClient() as client:
            peers_to_remove = []
            for peer_url in list(available_peers):
                try:
                    # Health check: expect 200 OK from the root
                    response = await client.get(peer_url, timeout=5.0)
                    if response.status_code != 200:
                        peers_to_remove.append(peer_url)
                except httpx.RequestError:
                    peers_to_remove.append(peer_url)
            
            for peer_url in peers_to_remove:
                available_peers.discard(peer_url)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background task
    bg_task = asyncio.create_task(check_peers())
    yield
    # Cleanup: stop the background task
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

peer_handler = FastAPI(lifespan=lifespan)

@peer_handler.get("/")
async def get_status():
    """Standard response for health checks"""
    return {"status": "Central node is running"}

@peer_handler.post("/hello")
async def say_hello(payload: Hello) -> dict[str, str]:
    """Receive hello from peer and register it"""
    peer_url = payload.peer_url
    available_peers.add(peer_url)
    return {"message": f"Hello from central node! Received hello from {peer_url}"}

@peer_handler.get("/peers", response_model=AvailablePeers)
async def get_peers() -> AvailablePeers:
    """Return list of available peers"""
    return AvailablePeers(peers=list(available_peers))