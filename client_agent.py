# client_agent.py
import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()
AGENT_ENDPOINTS = {
    "data_agent": "http://localhost:8001",
    "summary_agent": "http://localhost:8002",
    "formatter_agent": "http://localhost:8003",
    "qa_agent": "http://localhost:8004"
}

def fetch_agent_card(agent):
    url = f"{AGENT_ENDPOINTS[agent]}/.well-known/agent.json"
    response = requests.get(url)
    return response.json()

def dispatch_to_agent(agent, capability, payload):
    card = fetch_agent_card(agent)
    if capability not in card["capabilities"]:
        raise Exception(f"{capability} not supported by {agent}")
    
    print(f"\n[Client Agent] Calling {agent} with capability: {capability}")
    print(json.dumps(card, indent=2))

    response = requests.post(
        f"{AGENT_ENDPOINTS[agent]}/task",
        json={"capability": capability, "input": payload}
    )

    if response.status_code == 200:
        return response.json()["artifact"]
    else:
        raise Exception(f"{agent} failed: {response.text}")

def llm_decision_engine(user_input):
    print("[LLM] Sending user input to Gemini...")

    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    API_KEY = os.getenv("GEMINI_API_KEY")

    prompt = f"""
    You are an AI coordinator. Based on the following user query, decide which agents should handle it.
    Return a JSON list of steps. Each step should have:
    - 'agent': one of 'data_agent', 'summary_agent', 'formatter_agent', 'qa_agent'
    - 'capability': capability name
    - 'input': the text to process

    User Query: {user_input}
    """

    headers = { "Content-Type": "application/json" }
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500}
    }

    try:
        res = requests.post(f"{GEMINI_API_URL}?key={API_KEY}", headers=headers, json=body)
        content = res.json()
        reply = content["candidates"][0]["content"]["parts"][0]["text"]
        print("[LLM] Gemini responded with:\n", reply)
        return json.loads(reply)
    except Exception as e:
        print("[LLM] Gemini failed, falling back:", e)
        return [{"agent": "qa_agent", "capability": "answer_question", "input": user_input}]

def run_a2a_workflow(query):
    print("\n🔍 [Client Agent] Received Query:", query)
    steps = llm_decision_engine(query)
    output = None

    for step in steps:
        payload = step.get("input", output)
        output = dispatch_to_agent(step["agent"], step["capability"], payload)

    print("\n✅ Final Output:\n", output)

if __name__ == "__main__":
    run_a2a_workflow("Tell me about the A2A protocol")
    run_a2a_workflow("What is the future of agent communication?")
