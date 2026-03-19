from fastapi import FastAPI
from schemas import TransactionSchema
import requests

app = FastAPI()

PEER_HANDLER_PORT = 8001


@app.get("/")
def get_status():
    return {"node_id": app.state.node_id, "health": "ok"}

def start_peer(node_id: str, port: int):
    app.state.node_id = node_id
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
    requests.post(f"http://localhost:{PEER_HANDLER_PORT}/hello", json={"port": port})


