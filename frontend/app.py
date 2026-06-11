import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Loopp AI Refund Agent", layout="wide")
st.title("AI Customer Support Refund Agent")
st.caption("Full-stack vertical slice: customer chat + admin reasoning logs")

@st.cache_data(ttl=10)
def get_customers():
    return requests.get(f"{API_URL}/customers", timeout=5).json()

left, right = st.columns([1, 1])

with left:
    st.subheader("Customer Chat")
    try:
        customers = get_customers()
        labels = [f"{c['customer_id']} - {c['name']}" for c in customers]
        selected = st.selectbox("Select Customer", labels)
        customer_id = selected.split(" - ")[0]
        customer = next(c for c in customers if c["customer_id"] == customer_id)
        order = customer["orders"][0]

        st.write("**Order:**", order["order_id"], "—", order["product"])
        st.json(order)

        message = st.text_area("Customer Message", value=f"Hi, I want a refund for order {order['order_id']}.")
        if st.button("Send to Agent", type="primary"):
            payload = {"customer_id": customer_id, "order_id": order["order_id"], "message": message}
            response = requests.post(f"{API_URL}/chat", json=payload, timeout=15)
            if response.ok:
                data = response.json()
                st.success(f"Decision: {data['decision']}")
                st.chat_message("assistant").write(data["response"])
            else:
                st.error(response.text)
    except Exception as exc:
        st.error("Backend is not running. Start it with: uvicorn main:app --reload --port 8000")
        st.exception(exc)

with right:
    st.subheader("Admin Dashboard: Real-Time Reasoning Logs")
    if st.button("Refresh Logs"):
        st.rerun()
    try:
        logs = requests.get(f"{API_URL}/logs", timeout=5).json()
        if not logs:
            st.info("No agent runs yet. Submit a chat request first.")
        for i, run in enumerate(logs, start=1):
            with st.expander(f"Run {i}: {run['customer_id']} / {run['order_id']} / {run['decision']}", expanded=i == 1):
                st.write("**Customer message:**", run["user_message"])
                st.write("**Final response:**", run["response"])
                st.write("**Reasons:**")
                for reason in run["reasons"]:
                    st.write("-", reason)
                st.write("**Reasoning/tool logs:**")
                for log in run["reasoning_logs"]:
                    st.code(log)
    except Exception:
        st.warning("Logs unavailable until backend is running.")
