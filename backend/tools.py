import json
from pathlib import Path
from typing import Dict, Any, List

CRM_PATH = Path(__file__).parent / "mock_crm.json"


def load_crm() -> List[Dict[str, Any]]:
    with CRM_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_customer(customer_id: str) -> Dict[str, Any]:
    for customer in load_crm():
        if customer["customer_id"].lower() == customer_id.lower():
            return customer
    raise ValueError(f"Customer {customer_id} was not found in CRM")


def find_order(customer_id: str, order_id: str) -> Dict[str, Any]:
    customer = find_customer(customer_id)
    for order in customer.get("orders", []):
        if order["order_id"].lower() == order_id.lower():
            return order
    raise ValueError(f"Order {order_id} was not found for customer {customer_id}")


def evaluate_refund_policy(customer_id: str, order_id: str) -> Dict[str, Any]:
    customer = find_customer(customer_id)
    order = find_order(customer_id, order_id)
    reasons = []
    logs = []

    logs.append(f"Loaded CRM profile for {customer['name']} ({customer_id}).")
    logs.append(f"Loaded order {order_id}: {order['product']}, ${order['price']}, status={order['status']}.")

    if customer["fraud_flag"]:
        reasons.append("Customer account has a fraud flag and must be escalated.")
        return {"decision": "DENIED_ESCALATE", "reasons": reasons, "logs": logs}

    if order["status"] != "delivered":
        reasons.append("Refunds are only available for delivered orders.")
        return {"decision": "DENIED", "reasons": reasons, "logs": logs}

    if order["category"] in ["digital", "gift_card", "personalized"] or order["final_sale"]:
        reasons.append("Policy excludes final-sale, digital, gift card, and personalized products.")
        return {"decision": "DENIED", "reasons": reasons, "logs": logs}

    if customer["refunds_last_12_months"] > 3:
        reasons.append("Customer has more than 3 refunds in the last 12 months; manual review required.")
        return {"decision": "MANUAL_REVIEW", "reasons": reasons, "logs": logs}

    if order["price"] > 500:
        reasons.append("Refund amount is above $500 and requires manual review.")
        return {"decision": "MANUAL_REVIEW", "reasons": reasons, "logs": logs}

    if order["condition"] in ["damaged", "incorrect_item"]:
        if order["delivery_days_ago"] <= 45 and order["evidence_provided"]:
            reasons.append("Damaged/incorrect item reported within 45 days with evidence provided.")
            return {"decision": "APPROVED", "reasons": reasons, "logs": logs}
        reasons.append("Damaged/incorrect item exception requires evidence and must be within 45 days.")
        return {"decision": "DENIED", "reasons": reasons, "logs": logs}

    if order["delivery_days_ago"] > 30:
        reasons.append("Order is outside the standard 30-day refund window.")
        return {"decision": "DENIED", "reasons": reasons, "logs": logs}

    if order["condition"] != "unused":
        reasons.append("Standard refunds require the item to be unused and in original condition.")
        return {"decision": "DENIED", "reasons": reasons, "logs": logs}

    reasons.append("Order is delivered, within 30 days, unused, and not excluded by policy.")
    return {"decision": "APPROVED", "reasons": reasons, "logs": logs}
