# data_agent_service.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import time

app = FastAPI()

class TaskRequest(BaseModel):
    capability: str
    input: str

AGENT_CARD = {
    "agent_id": "data-agent-001",
    "name": "Data Retriever Agent",
    "capabilities": ["fetch_data"],
    "endpoint": "/data_agent/.well-known/agent.json"
}

@app.get("/.well-known/agent.json")
def get_agent_card():
    return AGENT_CARD

@app.post("/task")
def handle_task(task: TaskRequest):
    if task.capability != "fetch_data":
        return {"error": "Unsupported capability"}
    time.sleep(1)
    return {
        "artifact": f"Data about '{task.input}' from various sources."
    }
