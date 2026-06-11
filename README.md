# Loopp Full-Stack AI Challenge: AI Customer Support Refund Agent

This project is a functional vertical slice for an AI customer support agent that processes or denies e-commerce refunds using CRM data, a strict refund policy, tool-style orchestration, and a live admin reasoning dashboard.

## Features

- Mock CRM database with 15 customer profiles and order scenarios
- Strict refund policy document
- FastAPI backend with refund decision endpoint
- Tool-style orchestration for CRM lookup and policy validation
- Optional OpenAI response polishing when `OPENAI_API_KEY` is configured
- Streamlit frontend with customer chat interface
- Admin dashboard showing real-time reasoning/tool logs
- Edge cases: final sale, over 30 days, fraud flag, high value order, excessive refund history, damaged/incorrect item exception

## Tech Stack

- Backend: Python, FastAPI, Pydantic
- Frontend: Streamlit
- Agent orchestration: raw function-calling/tool loop style
- Data: JSON mock CRM + markdown policy
- Optional LLM: OpenAI API

## Project Structure

```text
loopp-ai-refund-agent/
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── tools.py
│   ├── mock_crm.json
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── refund_policy.md
├── loom_script.md
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd loopp-ai-refund-agent
```

### 2. Start backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend health check:

```text
http://localhost:8000
```

### 3. Start frontend

Open a second terminal:

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Frontend opens at:

```text
http://localhost:8501
```

## Optional LLM Configuration

The project works without an API key using deterministic policy-based responses. To enable OpenAI polishing:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4o-mini"
```

## Demo Scenarios

### Approved Standard Refund

- Customer: `C001 - Ava Johnson`
- Order: `ORD1001`
- Reason: Delivered 12 days ago, unused, not final sale, within 30-day policy window.

### Denied Edge Case / Holding the Line

- Customer: `C004 - Liam Patel`
- Order: `ORD1004`
- Reason: Delivered 47 days ago, outside standard 30-day refund window.

### Other Useful Cases

- `C003`: final sale item denied
- `C005`: damaged item approved because evidence is provided within 45 days
- `C006`: manual review due to more than 3 refunds in 12 months
- `C007`: fraud flag denied and escalated
- `C008`: high-value refund requires manual review
- `C009`: digital product denied
- `C010`: personalized product denied

## API Endpoints

### `GET /customers`
Returns mock CRM customer profiles.

### `POST /chat`
Processes refund request.

Example request:

```json
{
  "customer_id": "C001",
  "order_id": "ORD1001",
  "message": "Hi, I want a refund for my order."
}
```

### `GET /logs`
Returns the latest agent decisions and reasoning traces.

## Design Notes

The agent uses tool-style orchestration instead of making the LLM directly decide policy outcomes. This is intentional because refund decisions must be auditable, deterministic, and policy-compliant. The LLM is optional and only used to polish the customer-facing language without changing the policy decision.

## Future Improvements

- LangGraph state machine for multi-step retry/fallback flows
- Voice pipeline using OpenAI Realtime API or LiveKit
- Persistent database using SQLite/PostgreSQL
- Authentication for admin dashboard
- Automated unit tests for each policy rule
