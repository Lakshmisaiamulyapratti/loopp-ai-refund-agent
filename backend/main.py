from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from tools import load_crm
from agent import run_refund_agent

app = FastAPI(title="Loopp AI Customer Support Refund Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RefundRequest(BaseModel):
    customer_id: str
    order_id: str
    message: str

RUN_LOGS: List[Dict[str, Any]] = []

@app.get("/")
def health():
    return {"status": "ok", "service": "AI Refund Agent"}

@app.get("/customers")
def customers():
    return load_crm()

@app.post("/chat")
def chat(req: RefundRequest):
    try:
        result = run_refund_agent(req.customer_id, req.order_id, req.message)
        RUN_LOGS.insert(0, result)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/logs")
def logs():
    return RUN_LOGS[:20]
