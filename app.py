import sys
import streamlit as st
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from assistant import build_conversational_chain, generate_response

# -----------------------------
# 1. INITIALIZATION
# -----------------------------
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chain" not in st.session_state:
        st.session_state.chain = None
    if "current_personality" not in st.session_state:
        st.session_state.current_personality = "Professor Z"

def ensure_chain():
    if st.session_state.chain is None:
        st.session_state.chain = build_conversational_chain()

# -----------------------------
# 2. THE BUD AI "SQUAD" SIDEBAR
# -----------------------------
def llm_config_sidebar():
    st.sidebar.markdown("### ⚙️ System Control")
    
    # MASCOT SELECTION (The "Secret Sauce" for PromptWars)
    st.sidebar.subheader("🛡️ Active Buddy")
    agent_mode = st.sidebar.radio("Switch Personality:", ["Professor Z", "Aman"])
    
    if agent_mode == "Professor Z":
        st.sidebar.success("👨‍🏫 **Mentor Mode**\nSocratic & Patient")
        st.session_state.current_personality = "You are Professor Z, a patient academic mentor. Don't give answers directly; guide the user with analogies and encouraging questions."
    else:
        st.sidebar.warning("🏎️ **Rival Mode**\nBrutal & Technical")
        st.session_state.current_personality = "You are Aman, a sharp technical rival. Challenge the user's logic aggressively. Point out bugs bluntly and push them to be better."

    st.sidebar.divider()
    
    # PROVIDER LOGIC
    provider = st.sidebar.selectbox(
        "LLM Provider",
        ["OpenAI", "Groq", "Ollama (Local)"],
        index=0
    )

    if provider == "OpenAI":
        api_key = st.sidebar.text_input("OpenAI Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if st.sidebar.button("Connect OpenAI"):
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "openai"
            st.session_state.chain = None
            st.rerun()

    elif provider == "Groq":
        api_key = st.sidebar.text_input("Groq Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
        if st.sidebar.button("Connect Groq"):
            os.environ["GROQ_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "groq"
            st.session_state.chain = None
            st.rerun()

    elif provider == "Ollama (Local)":
        model = st.sidebar.text_input("Ollama Model", value="llama3")
        if st.sidebar.button("Connect Ollama"):
            os.environ["OLLAMA_MODEL"] = model
            os.environ["LLM_PROVIDER"] = "ollama"
            st.session_state.chain = None
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🔄 Reset Session"):
        st.session_state.messages = []
        st.session_state.chain = None
        st.rerun()

# -----------------------------
# 3. THE LIQUID-GLASS UI
# -----------------------------
def chat_ui():
    st.markdown(
        """
        <style>
        /* Modern Dark Gradient Background */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #ffffff;
        }
        /* Glassmorphism Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        /* Frosted Glass Chat Bubbles */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.07) !important;
            backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin-bottom: 15px;
        }
        /* Input Field Styling */
        .stChatInputContainer {
            padding-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("🛡️ Bud AI: The Squad Hub")
    st.caption("Developed in Google Antigravity | Rival-Mentor Framework v2.0")

    llm_config_sidebar()
    ensure_chain()

    # Determine Active Avatar
    is_prof = "Professor Z" in st.session_state.current_personality
    assistant_avatar = "👨‍🏫" if is_prof else "🏎️"

    # Display History
    for role, content in st.session_state.messages:
        avatar = "🧑‍💻" if role == "user" else assistant_avatar
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

    # Chat Input
    if prompt := st.chat_input("Drop a message for the Squad... 🚀"):
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=assistant_avatar):
            placeholder = st.empty()
            try:
                if st.session_state.chain is None:
                    answer = "⚠️ Please configure your LLM provider in the sidebar first."
                else:
                    # We pass the personality string specifically here
                    answer = generate_response(
                        st.session_state.chain, 
                        prompt, # The actual question
                        st.session_state.messages[:-1], # History
                        personality=st.session_state.current_personality # The Mascot!
                    )
            except Exception as e:
                answer = f"❌ Error: {e}"

            placeholder.markdown(answer)
        st.session_state.messages.append(("assistant", answer))

# -----------------------------
# 4. EXECUTION
# -----------------------------
if __name__ == "__main__":
    init_state()
    chat_ui()