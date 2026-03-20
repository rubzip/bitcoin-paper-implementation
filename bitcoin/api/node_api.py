import os
import json
import httpx
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from typing import List, Set
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from bitcoin.blockchain.node import Node
from bitcoin.blockchain.models import Block, Transaction
from bitcoin.api.schemas import Hello, AvailablePeers, BlockSchema

app = FastAPI()

# Setup templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

node_instance: Node = None
REGISTRY_URL: str = "http://localhost:8000"
peers: Set[str] = set()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    if node_instance is None:
        return HTMLResponse(content="<h1>Node not initialized</h1>", status_code=503)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "node_id": node_instance.node_id,
        "balance": node_instance.blockchain.get_balance(node_instance.node_id)
    })

@app.get("/status")
async def get_status():
    if node_instance is None:
        return {"error": "Node not initialized"}
    return {
        "node_id": node_instance.node_id,
        "balance": node_instance.blockchain.get_balance(node_instance.node_id),
        "health": "ok"
    }

@app.get("/chain", response_model=List[BlockSchema])
async def get_chain():
    if node_instance is None:
        raise HTTPException(status_code=503, detail="Node not initialized")
    return [b.to_dict() for b in node_instance.blockchain.chain]

@app.post("/chain")
async def receive_chain(chain_data: List[BlockSchema]):
    if node_instance is None:
        raise HTTPException(status_code=503, detail="Node not initialized")
    
    try:
        new_blocks = []
        for b_schema in chain_data:
            txs = [Transaction(tx.sender, tx.receiver, tx.amount, tx.timestamp) for tx in b_schema.transactions]
            block = Block(b_schema.index, txs, b_schema.prev_hash, b_schema.timestamp)
            block.nonce = b_schema.nonce
            block.hash = b_schema.hash
            new_blocks.append(block)
        
        node_instance.blockchain.overwrite(new_blocks)
        return {"message": "Chain processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid chain received: {str(e)}")

@app.post("/mine/{miner}")
async def mine(miner: str):
    if node_instance is None:
        raise HTTPException(status_code=503, detail="Node not initialized")
    
    try:
        node_instance.mine(miner)
        asyncio.create_task(broadcast_chain())
        return {"message": "Block mined and broadcasted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transaction/{sender}/{receiver}/{amount}")
async def add_transaction(sender: str, receiver: str, amount: int):
    if node_instance is None:
        raise HTTPException(status_code=503, detail="Node not initialized")
    
    try:
        node_instance.add_transaction(sender, receiver, amount)
        return {"message": "Transaction added to mempool"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/balance/{user}")
def get_balance(user: str) -> int:
    if node_instance is None:
        raise HTTPException(status_code=503, detail="Node not initialized")
    return node_instance.blockchain.get_balance(user)

async def fetch_peers():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{REGISTRY_URL}/peers")
            if response.status_code == 200:
                data = AvailablePeers(**response.json())
                global peers
                peers = set(data.peers)
        except Exception as e:
            print(f"Failed to fetch peers from registry: {e}")

async def broadcast_chain():
    await fetch_peers()
    chain_json = [b.to_dict() for b in node_instance.blockchain.chain]
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for peer_url in peers:
            tasks.append(client.post(f"{peer_url}/chain", json=chain_json, timeout=3.0))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def register_with_registry(registry_url: str, own_url: str):
    global REGISTRY_URL
    REGISTRY_URL = registry_url
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.post(f"{registry_url}/hello", json={"peer_url": own_url})
            except Exception as e:
                print(f"Periodic registration failed: {e}")
            await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This is slightly tricky because we need registry_url and own_url
    # which are only known in run_node
    yield

def run_node(node_id: str, port: int, registry_url: str = "http://localhost:8000"):
    global node_instance
    node_instance = Node(node_id=node_id)
    own_url = f"http://localhost:{port}"
    
    @asynccontextmanager
    async def dynamic_lifespan(app: FastAPI):
        reg_task = asyncio.create_task(register_with_registry(registry_url, own_url))
        yield
        reg_task.cancel()

    app.router.lifespan_context = dynamic_lifespan
    uvicorn.run(app, host="0.0.0.0", port=port)
