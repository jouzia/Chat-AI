import os
import streamlit as st

# 1. LOAD SECRETS & CONFIG
def load_secrets():
    for key in ["GROQ_API_KEY", "OPENAI_API_KEY", "LLM_PROVIDER", "OLLAMA_MODEL"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

load_secrets()

# Import the 'Brain' logic from assistant.py
from assistant import build_conversational_chain, generate_response

# 2. INIT STATE
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chain" not in st.session_state:
        st.session_state.chain = None

# 3. BUILD CHAIN SAFELY
def ensure_chain():
    if st.session_state.chain is None:
        try:
            st.session_state.chain = build_conversational_chain()
        except Exception as e:
            st.error(f"Failed to initialize AI: {e}")

# 4. UI STYLING (The Animated Tri-Color Gradient)
def apply_custom_styles():
    st.markdown("""
        <style>
        /* 1. DEFINE THE ANIMATION */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* 2. APPLY TO THE APP CONTAINER */
        .stApp {
            background: linear-gradient(-45deg, #4facfe, #a76dcc, #f093fb, #4facfe) !important;
            background-size: 400% 400% !important;
            animation: gradientBG 12s ease infinite !important;
            background-attachment: fixed;
        }

        /* 3. ENSURE CHAT BUBBLES ARE SEE-THROUGH (Glassmorphism) */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.12) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            margin-bottom: 15px !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        /* 4. MAKE SIDEBAR GLASSY */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(20px) !important;
        }

        /* 5. FIX TEXT CLARITY */
        h1, h2, h3, p {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
# 5. CHAT LOGIC
def main():
    init_state()
    apply_custom_styles()
    
    st.title("Bud AI 🤖")
    st.caption("BCA Engineering Edition | v2.5")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        if st.button("🔄 Reset Session"):
            st.session_state.messages = []
            st.session_state.chain = None
            st.rerun()
        
        provider = st.selectbox("LLM Provider", ["Groq", "OpenAI", "Ollama"], index=0)
        os.environ["LLM_PROVIDER"] = provider.lower()
        
    ensure_chain()

    # Display History
    for role, content in st.session_state.messages:
        # User is coder, Assistant is the Spark/Flash icon
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "⚡"):
            st.markdown(content)

    # User Input (Hitting Enter sends the message)
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            placeholder = st.empty()
            with st.spinner("Bud is thinking..."):
                try:
                    # Pass chain, current prompt, and history
                    answer = generate_response(
                        st.session_state.chain, 
                        prompt, 
                        st.session_state.messages[:-1]
                    )
                except Exception as e:
                    answer = f"❌ Error: {str(e)}"
            
            placeholder.markdown(answer)
            st.session_state.messages.append(("assistant", answer))

if __name__ == "__main__":
    main()
