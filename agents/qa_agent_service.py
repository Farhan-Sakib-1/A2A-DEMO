# qa_agent_service.py
from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI()

class TaskRequest(BaseModel):
    capability: str
    input: str

AGENT_CARD = {
    "agent_id": "qa-agent-004",
    "name": "Question Answering Agent",
    "capabilities": ["answer_question"],
    "endpoint": "/qa_agent/.well-known/agent.json"
}

@app.get("/.well-known/agent.json")
def get_agent_card():
    return AGENT_CARD

@app.post("/task")
def handle_task(task: TaskRequest):
    if task.capability != "answer_question":
        return {"error": "Unsupported capability"}
    time.sleep(1)
    return {
        "artifact": f"Answer to: '{task.input}' is... [simulated answer]"
    }
