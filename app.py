import os
import streamlit as st

# 1. LOAD SECRETS & CONFIG
def load_secrets():
    # Priority: Streamlit Secrets -> Environment Variables
    for key in ["GROQ_API_KEY", "OPENAI_API_KEY", "LLM_PROVIDER", "OLLAMA_MODEL"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

load_secrets()

# Import the 'Brain' logic
from assistant import build_conversational_chain, generate_response

# 2. INIT STATE
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chain" not in st.session_state:
        st.session_state.chain = None

# 3. BUILD CHAIN SAFELY
def ensure_chain():
    # Only build if we have a provider set
    if st.session_state.chain is None:
        try:
            st.session_state.chain = build_conversational_chain()
        except Exception as e:
            st.error(f"Failed to initialize AI: {e}")

# 4. UI STYLING
def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp {
            background: #0d0f1a;
            color: #ffffff;
        }
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        .stChatMessage {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# 5. CHAT LOGIC
def main():
    init_state()
    apply_custom_styles()
    
    st.title("Bud AI 🤖")
    st.caption("BCA Engineering Edition | v2.4")

    # Sidebar for Config
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
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
            st.markdown(content)

    # User Input
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            with st.spinner("Grok is thinking..."):
                try:
                    # Pass the chain and history to generate the answer
                    answer = generate_response(
                        st.session_state.chain, 
                        prompt, 
                        st.session_state.messages[:-1]
                    )
                except Exception as e:
                    answer = f"❌ Connection Error: {str(e)}"
            
            placeholder.markdown(answer)
            st.session_state.messages.append(("assistant", answer))

if __name__ == "__main__":
    main()
