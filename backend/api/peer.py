from fastapi import FastAPI
from schemas import TransactionSchema


app = FastAPI()


@app.get("/")
def get_status():
    return {"node_id": app.state.node_id, "health": "ok"}

@app.post("/hello")
def say_hello(port: str):    
    pass
