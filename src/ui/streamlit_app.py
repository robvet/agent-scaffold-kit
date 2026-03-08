"""
Streamlit UI for Architecture Accelerator.
Provides a clear, single view of the architectural trace through the Supervisor agent.
"""
import base64
from pathlib import Path

import streamlit as st
import requests
from typing import Dict, Any

# FastAPI backend URL
API_URL = "http://127.0.0.1:8010"

# Load logo image as base64 for inline embedding in the header
_logo_path = Path(__file__).parent / "images" / "agent-framework-logo.png"
_logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode() if _logo_path.exists() else ""

@st.dialog("📋 Copy Raw JSON", width="large")
def show_copy_dialog(json_content: str):
    """Dialog popup showing raw JSON with copy button."""
    st.markdown("Click the copy icon in the code block below:")
    st.code(json_content, language="json")
    if st.button("Close", use_container_width=True):
        st.rerun()

def call_supervisor(prompt: str) -> Dict[str, Any] | None:
    """Call the supervisor endpoint."""
    try:
        response = requests.post(
            f"{API_URL}/post",
            json={"user_prompt": prompt},
            timeout=120.0,
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and styling
bg_gradient = "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)"
accent_color = "#e94560"

st.markdown(f"""
    <style>
        /* Dark theme colors */
        .main .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
        }}
        .main .block-container > div:first-child {{
            margin-top: 0 !important;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Header styling */
        .main-header {{
            background: {bg_gradient};
            padding: 0.55rem 1.1rem;
            border-radius: 10px;
            margin-top: -0.55rem;
            margin-bottom: 1rem;
            text-align: center;
            border-bottom: 3px solid {accent_color};
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .main-header h1 {{
            color: {accent_color};
            margin: 0;
            font-size: 2.5rem;
            line-height: 1.05;
        }}
        .main-header p {{
            color: #a0a0a0;
            margin: 0.05rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 500;
        }}
        .stApp {{
            background: {bg_gradient};
        }}
        /* Summary section styling */
        .summary-header {{
            background: linear-gradient(135deg, {accent_color} 0%, #0f3460 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 10px 10px 0 0;
            font-weight: bold;
            font-size: 1.2rem;
            margin-top: 2rem;
        }}
        /* Button styling */
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {accent_color} 0%, #c73659 100%);
            border: none;
            font-weight: bold;
        }}
        .stButton > button[kind="primary"]:hover {{
            background: linear-gradient(135deg, {accent_color} 0%, #a62d4e 100%);
        }}
        .agent-card {{
            background-color: #262730;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #444;
            height: 100%;
        }}
        .agent-card-title {{
            color: #4B8BF5;
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 10px;
            border-bottom: 1px solid #444;
            padding-bottom: 5px;
        }}
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
    <div class="main-header">
        <div style="flex: 1; text-align: center;">
            <h1>🏗️ Architecture Accelerator</h1>
            <p>Trace the flow from UX → API → Supervisor → Agents → Tools/LLM</p>
        </div>
        <img src="data:image/png;base64,{_logo_b64}" style="height: 100px; margin-left: 1rem;" alt="Agent Framework" />
    </div>
""", unsafe_allow_html=True)

if "last_response" not in st.session_state:
    st.session_state.last_response = None

# Input section
with st.container():
    st.markdown("""
        <div style="background: #2a9d8f; color: white; padding: 0.5rem 1rem; border-radius: 10px 10px 0 0; font-weight: bold; font-size: 1.1rem; margin-bottom: -1px; border: 2px solid #2a9d8f;">
            User Request
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([10, 2])
    with col1:
        user_input = st.text_area(
            "Prompt", 
            placeholder="Type anything to trigger the flow...",
            height=100,
            label_visibility="collapsed"
        )
    with col2:
        st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
        send_clicked = st.button("🚀 Send to API", type="primary", use_container_width=True)
        clear_clicked = st.button("🗑️ Clear", use_container_width=True)

if clear_clicked:
    st.session_state.last_response = None
    st.rerun()

if send_clicked and user_input:
    with st.spinner("Executing Architecture Trace... (Supervisor is calling Child Agents)"):
        result = call_supervisor(user_input)
        if result:
            st.session_state.last_response = result
            st.rerun()

# Results Section
if st.session_state.last_response:
    data = st.session_state.last_response
    
    st.markdown('<div class="summary-header">🎯 Final Aggregated Result (From Supervisor)</div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background-color: #262730; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #444; border-top: none; font-size: 1.1rem; line-height: 1.6;">
            {data.get("aggregated_response", "No aggregation returned.")}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br/><h3>⛓️ Child Agent Capabilities (Fan-out execution)</h3>", unsafe_allow_html=True)
    responses = data.get("responses", {})
    
    if responses:
        # Create columns based on number of active child agents
        cols = st.columns(len(responses))
        for idx, (agent_name, agent_data) in enumerate(responses.items()):
            text = agent_data.get("text", "")
            if agent_data.get("status") == "error":
                text = f"❌ Error: {agent_data.get('error_message', 'Unknown error')}"
                
            with cols[idx]:
                st.markdown(f"""
                    <div class="agent-card">
                        <div class="agent-card-title">🤖 {agent_name}</div>
                        <div>{text}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No child agent responses found in payload.")
        
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔍 View Raw API Payload JSON"):
        import json
        show_copy_dialog(json.dumps(data, indent=2))
