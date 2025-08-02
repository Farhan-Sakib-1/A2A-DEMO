Python 3.10 or 3.11 (⚠️ Not supported on Python 3.13+)
Pip (latest)
Internet access (for LLM to call Gemini API)
Create a Virtual Environment:
python -m venv venv
venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt

GEMINI_API_KEY=your_real_key_here
Run the Agents:
uvicorn agents.data_agent_service:app --port 8001
uvicorn agents.summary_agent_service:app --port 8002
uvicorn agents.formatter_agent_service:app --port 8003
uvicorn agents.qa_agent_service:app --port 8004
cient agent:
python client_agent.py
