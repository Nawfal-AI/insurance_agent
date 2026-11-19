"""
Streamlit frontend — a plain-language chat interface over the /ask API.
Designed so a non-technical caseworker at a Swiss cantonal insurance office
can query policy documents without knowing anything about the underlying model.

Run locally:
    streamlit run app/frontend/streamlit_app.py

The app talks to the FastAPI backend at BACKEND_URL (default: http://localhost:8080).
Set BACKEND_URL in your .env or environment to point at the deployed AWS endpoint.
"""
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Swiss Insurance Policy Assistant",
    page_icon="🏥",
    layout="centered",
)

st.title("🏥 Swiss Insurance Policy Assistant")
st.caption(
    "Ask questions about KVG/LAMal coverage in plain language. "
    "Every answer is grounded in the actual policy documents."
)

# --- session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_traces" not in st.session_state:
    st.session_state.tool_traces = []

# --- render history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- input ---
if question := st.chat_input("e.g. What is the deductible for a standard claim?"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching policy documents…"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={
                        "question": question,
                        "history": st.session_state.messages[:-1],
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("answer", "No answer returned.")
                tool_calls = data.get("tool_calls", [])
            except requests.exceptions.ConnectionError:
                answer = (
                    "⚠️ Could not reach the backend. "
                    f"Make sure the server is running at {BACKEND_URL}."
                )
                tool_calls = []
            except Exception as e:
                answer = f"⚠️ Error: {e}"
                tool_calls = []

        st.markdown(answer)

        if tool_calls:
            with st.expander("🔍 How this answer was produced (tool trace)", expanded=False):
                for i, tc in enumerate(tool_calls, 1):
                    st.markdown(f"**Step {i} — `{tc['tool']}`**")
                    st.json(tc.get("tool_input", {}))
                    st.text_area(
                        f"Result {i}",
                        value=tc.get("observation", ""),
                        height=100,
                        key=f"obs_{len(st.session_state.messages)}_{i}",
                    )

    st.session_state.messages.append({"role": "assistant", "content": answer})

# --- sidebar ---
with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This assistant helps caseworkers and policyholders query Swiss public
        health insurance (KVG/LAMal) documents in plain language.

        **It does not replace professional legal or medical advice.**

        Built on:
        - LangGraph ReAct agent
        - FAISS vector retrieval
        - Sentence Transformers embeddings
        - Deployed on AWS ECS (Fargate)
        """
    )
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.tool_traces = []
        st.rerun()
