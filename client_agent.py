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
        raise Exception(f"[ERROR] {capability} not supported by {agent}. Available: {card['capabilities']}")
    
    print(f"\n[Client Agent] Calling {agent} with capability: {capability}")
    print(json.dumps(card, indent=2))

    response = requests.post(
        f"{AGENT_ENDPOINTS[agent]}/task",
        json={"capability": capability, "input": payload}
    )

    if response.status_code == 200:
        return response.json().get("artifact", "[No result]")
    else:
        raise Exception(f"[ERROR] {agent} failed: {response.text}")

def llm_decision_engine(user_input):
    print("[LLM] Sending user input to Gemini...")

    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    API_KEY = os.getenv("GEMINI_API_KEY")

    prompt = f"""
You are an AI coordinator. Based on the user query, break the task into steps.
Use only the following valid capabilities:

- data_agent: fetch_data
- summary_agent: summarize
- formatter_agent: format_report
- qa_agent: answer_question

Return a pure JSON list of steps (no markdown).
Example:

[
  {{
    "agent": "data_agent",
    "capability": "fetch_data",
    "input": "example query"
  }}
]

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

        # Print full response for debug
        print("[LLM] Full API response:", json.dumps(content, indent=2))

        # Extract raw reply
        reply_raw = content["candidates"][0]["content"]["parts"][0]["text"]
        print("[LLM] Gemini responded with:\n", reply_raw)

        # Clean up any markdown formatting
        reply_clean = reply_raw.strip()
        if reply_clean.startswith("```json"):
            reply_clean = reply_clean.removeprefix("```json").removesuffix("```").strip()
        elif reply_clean.startswith("```"):
            reply_clean = reply_clean.removeprefix("```").removesuffix("```").strip()

        steps = json.loads(reply_clean)
        if not isinstance(steps, list):
            raise ValueError("Expected list of steps.")
        return steps

    except Exception as e:
        print("[LLM] Gemini failed or invalid response. Fallback activated. Reason:", e)
        return [{
            "agent": "qa_agent",
            "capability": "answer_question",
            "input": user_input
        }]

def run_a2a_workflow(query):
    print("\n🔍 [Client Agent] Received Query:", query)
    steps = llm_decision_engine(query)
    output = None

    for step in steps:
        agent = step.get("agent")
        capability = step.get("capability")
        payload = step.get("input", output)

        if not agent or not capability:
            print(f"[WARNING] Skipping invalid step: {step}")
            continue

        try:
            output = dispatch_to_agent(agent, capability, payload)
        except Exception as e:
            print(f"[ERROR] Agent dispatch failed:", e)
            break

    print("\n✅ Final Output:\n", output)

if __name__ == "__main__":
    run_a2a_workflow("Tell me about the A2A protocol")
    run_a2a_workflow("What is the future of agent communication?")
