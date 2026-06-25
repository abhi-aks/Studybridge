import os
import time
import streamlit as st
from groq import RateLimitError

# Load secrets from st.secrets if available (Streamlit Cloud), otherwise fall back to env vars (HuggingFace/Docker)
try:
    for key in ["GROQ_API_KEY", "OPENAI_API_KEY"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass

from rag import build_chain

st.set_page_config(page_title="StudyBridge — TH Bingen", page_icon="🎓")
st.title("🎓 StudyBridge")
st.caption("AI assistant for TH Bingen — ask about programs, enrollment, dormitories, visas, and more.")

# Cache chain across all users — embedding model loads once, not per session
@st.cache_resource(show_spinner="Loading knowledge base...")
def get_chain():
    return build_chain()

try:
    chain = get_chain()
except Exception as e:
    st.error(f"Failed to load knowledge base: {e}")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about TH Bingen..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        response = ""
        try:
            for attempt in range(3):
                try:
                    for chunk in chain.stream(prompt):
                        response += chunk
                        placeholder.markdown(response + "▌")
                    break
                except RateLimitError:
                    if attempt < 2:
                        response = ""
                        time.sleep(10 * (attempt + 1))
                    else:
                        raise
            placeholder.markdown(response)
        except Exception as e:
            response = f"Error: {type(e).__name__}: {e}"
            placeholder.markdown(response)

    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": response})
