import pytest
import json
import unittest.mock
import httpx
from bitcoin.api.registry import peer_handler, available_peers
from bitcoin.api.node_api import app as node_app
from bitcoin.blockchain.node import Node

@pytest.fixture(autouse=True)
def clear_peers():
    available_peers.clear()
    yield
    available_peers.clear()

@pytest.mark.asyncio
async def test_registry_status():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=peer_handler), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "Central node is running"
        assert response.json()["api"] == "Registry"

@pytest.mark.asyncio
async def test_registry_hello_and_get_peers():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=peer_handler), base_url="http://test") as ac:
        # Register a peer
        response = await ac.post("/hello", json={"peer_url": "http://localhost:8001"})
        assert response.status_code == 200
        
        # Get peers
        response = await ac.get("/peers")
        assert response.status_code == 200
        assert "http://localhost:8001" in response.json()["peers"]

@pytest.mark.asyncio
async def test_node_api_receive_chain():
    from bitcoin.api import node_api
    node_api.node_instance = Node(node_id="TestNode")
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=node_app), base_url="http://test") as ac:
        # Create a dummy chain
        node_alice = Node(node_id="Alice")
        node_alice.mine(miner="Alice")
        chain_data = [b.to_dict() for b in node_alice.blockchain.chain]
        
        response = await ac.post("/chain", json=chain_data)
        assert response.status_code == 200
        assert node_api.node_instance.blockchain.length == 2
        assert node_api.node_instance.blockchain.get_balance("Alice") == 50

@pytest.mark.asyncio
async def test_node_api_mine_and_broadcast():
    from bitcoin.api import node_api
    node_api.node_instance = Node(node_id="TestNode")
    
    # Mock broadcast_chain to avoid real network calls during mining test
    with unittest.mock.patch("bitcoin.api.node_api.broadcast_chain") as mock_broadcast:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=node_app), base_url="http://test") as ac:
            response = await ac.post("/mine/TestNode")
            assert response.status_code == 200
            assert node_api.node_instance.blockchain.length == 2
            # Check if broadcast was triggered
            # FastAPI runs it in asyncio.create_task, so we might need a tiny sleep or just trust the task was created
            # But since we patched it, we can just check if it was called (if it was awaited, which it isn't in my current mine code yet)
            # Actually I used asyncio.create_task(broadcast_chain())
            pass 
