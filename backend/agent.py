import os
from typing import Dict, Any, List
from tools import evaluate_refund_policy, find_customer, find_order

try:
    from openai import OpenAI
except Exception:  # keeps app runnable without OpenAI installed/configured
    OpenAI = None


def build_customer_response(decision: str, reasons: List[str], customer_name: str, order_id: str) -> str:
    reason_text = " ".join(reasons)
    if decision == "APPROVED":
        return f"Hi {customer_name}, your refund for {order_id} is approved. {reason_text} You will receive a confirmation email shortly."
    if decision == "MANUAL_REVIEW":
        return f"Hi {customer_name}, I cannot automatically approve this refund for {order_id}. {reason_text} I am escalating it for manual review."
    if decision == "DENIED_ESCALATE":
        return f"Hi {customer_name}, I cannot process this refund automatically. {reason_text} A support specialist will review the case."
    return f"Hi {customer_name}, I’m unable to approve the refund for {order_id}. {reason_text}"


def optional_llm_polish(message: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return message
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Rewrite customer support refund messages to be concise, polite, and policy-faithful. Do not change the decision."},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception:
        return message


def run_refund_agent(customer_id: str, order_id: str, user_message: str) -> Dict[str, Any]:
    reasoning_logs = [
        "Agent received refund request.",
        "Agent selected CRM lookup tool.",
        "Agent selected policy validation tool.",
    ]
    customer = find_customer(customer_id)
    order = find_order(customer_id, order_id)
    result = evaluate_refund_policy(customer_id, order_id)
    reasoning_logs.extend(result["logs"])
    reasoning_logs.append(f"Policy engine returned decision={result['decision']}.")

    response = build_customer_response(result["decision"], result["reasons"], customer["name"], order_id)
    response = optional_llm_polish(response)
    reasoning_logs.append("Agent generated final customer-facing response.")

    return {
        "customer_id": customer_id,
        "order_id": order_id,
        "user_message": user_message,
        "decision": result["decision"],
        "reasons": result["reasons"],
        "response": response,
        "order_snapshot": order,
        "reasoning_logs": reasoning_logs,
    }
