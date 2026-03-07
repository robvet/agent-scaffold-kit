import streamlit as st
import requests
from typing import Dict, Any

API_URL = "http://127.0.0.1:8010"

def call_supervisor(prompt: str) -> Dict[str, Any] | None:
    """Call the supervisor endpoint."""
    try:
        response = requests.post(
            f"{API_URL}/post",
            json={"user_prompt": prompt},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return None

# Page config
st.set_page_config(
    page_title="Architecture Accelerator",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ Architecture Accelerator")
st.markdown("This UI demonstrates a complete end-to-end trace from the UX, through the FastAPI REST layer, into the Supervisor agent, which fans out to Child Agents reading from a static JSON data file.")

# Status area
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# Input form
with st.form("query_form"):
    user_input = st.text_area("User Request (sent to API)", placeholder="Type anything to trace the architecture...")
    submitted = st.form_submit_button("Send to Supervisor", type="primary")

if submitted and user_input:
    with st.spinner("Executing Architecture Trace..."):
        result = call_supervisor(user_input)
        if result:
            st.session_state.last_response = result
            st.rerun()

# Output Display
if st.session_state.last_response:
    data = st.session_state.last_response
    st.divider()
    st.subheader("Architectural Trace Results")
    
    st.markdown("### Aggregated Output")
    st.info(data.get("aggregated_response", "No aggregation returned."))
    
    st.markdown("### Child Agent Payload")
    responses = data.get("responses", {})
    
    col1, col2 = st.columns(2)
    with col1:
        if "AgentAlpha" in responses:
            st.success("AgentAlpha Response")
            st.write(responses["AgentAlpha"].get("text", ""))
    
    with col2:
        if "AgentBeta" in responses:
            st.warning("AgentBeta Response")
            st.write(responses["AgentBeta"].get("text", ""))
            
    with st.expander("Raw API JSON Payload"):
        st.json(data)
