# formatter_agent_service.py
from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI()

class TaskRequest(BaseModel):
    capability: str
    input: str

AGENT_CARD = {
    "agent_id": "formatter-agent-003",
    "name": "Formatter Agent",
    "capabilities": ["format_report"],
    "endpoint": "/formatter_agent/.well-known/agent.json"
}

@app.get("/.well-known/agent.json")
def get_agent_card():
    return AGENT_CARD

@app.post("/task")
def handle_task(task: TaskRequest):
    if task.capability != "format_report":
        return {"error": "Unsupported capability"}
    time.sleep(1)
    return {
        "artifact": f"\n==== A2A Report ====\n{task.input}\n====================\n"
    }
