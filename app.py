import os
import streamlit as st


# Load Streamlit secrets into environment variables
def load_secrets():
    for key in ["GROQ_API_KEY", "OPENAI_API_KEY", "LLM_PROVIDER", "OLLAMA_MODEL"]:
        if key in st.secrets and not os.getenv(key):
            os.environ[key] = st.secrets[key]

load_secrets()

from assistant import build_conversational_chain, generate_response

# INIT STATE
# -----------------------------
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chain" not in st.session_state:
        st.session_state.chain = None


# -----------------------------
# BUILD CHAIN SAFELY
# -----------------------------
def ensure_chain():
    if st.session_state.chain is None:
        st.session_state.chain = build_conversational_chain()


# -----------------------------
# SIDEBAR CONFIG
# -----------------------------
def llm_config_sidebar():
    st.sidebar.subheader("⚙️ LLM Setup")

    provider = st.sidebar.selectbox(
        "Select Provider",
        ["OpenAI", "Groq", "Ollama (Local)"],
        index=["openai", "groq", "ollama"].index(os.getenv("LLM_PROVIDER", "openai")) if os.getenv("LLM_PROVIDER", "openai") in ["openai", "groq", "ollama"] else 0
    )

    if provider == "OpenAI":
        has_key = bool(os.getenv("OPENAI_API_KEY"))
        st.sidebar.caption(f"OpenAI key set: {has_key}")

        if not has_key:
            api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...")
            if st.sidebar.button("Save Key"):
                if api_key and api_key.strip():
                    os.environ["OPENAI_API_KEY"] = api_key.strip()
                    os.environ["LLM_PROVIDER"] = "openai"
                    st.session_state.chain = None
                    st.success("✅ OpenAI API key added!")
                    st.rerun()
                else:
                    st.error("❌ Invalid key")
        else:
            if st.sidebar.button("Use OpenAI"):
                os.environ["LLM_PROVIDER"] = "openai"
                st.session_state.chain = None
                st.rerun()
            if os.getenv("LLM_PROVIDER") == "openai":
                st.sidebar.success("✅ OpenAI Connected")

    elif provider == "Groq":
        has_key = bool(os.getenv("GROQ_API_KEY"))
        st.sidebar.caption(f"Groq key set: {has_key}")

        if not has_key:
            api_key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
            if st.sidebar.button("Save Key"):
                if api_key and api_key.strip():
                    os.environ["GROQ_API_KEY"] = api_key.strip()
                    os.environ["LLM_PROVIDER"] = "groq"
                    st.session_state.chain = None
                    st.success("✅ Groq API key added!")
                    st.rerun()
                else:
                    st.error("❌ Invalid key")
        else:
            if st.sidebar.button("Use Groq"):
                os.environ["LLM_PROVIDER"] = "groq"
                st.session_state.chain = None
                st.rerun()
            if os.getenv("LLM_PROVIDER") == "groq":
                st.sidebar.success("✅ Groq Connected")

    elif provider == "Ollama (Local)":
        st.sidebar.info("Ensure Ollama is running locally.")
        model = st.sidebar.text_input("Model Name", value=os.getenv("OLLAMA_MODEL", "llama3"))
        
        if st.sidebar.button("Connect Ollama"):
            os.environ["OLLAMA_MODEL"] = model.strip()
            os.environ["LLM_PROVIDER"] = "ollama"
            st.session_state.chain = None
            st.rerun()
            
        if os.getenv("LLM_PROVIDER") == "ollama":
            st.sidebar.success(f"✅ Ollama Connected ({os.getenv('OLLAMA_MODEL', 'llama3')})")


os.environ["LLM_PROVIDER"] = os.getenv("LLM_PROVIDER", "groq")

# -----------------------------
# CHAT UI
# -----------------------------
def chat_ui():
    st.markdown(
        """
        <style>
        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .stApp {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientAnimation 15s ease infinite;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("chat AI")

    with st.sidebar:
        st.subheader("Session")
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.session_state.chain = None
            st.rerun()

    llm_config_sidebar()
    ensure_chain()

    # Show messages
    for role, content in st.session_state.messages:
        avatar = "🧑‍💻" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

    # Input
    if prompt := st.chat_input("Drop a message... 🚀"):
        st.session_state.messages.append(("user", prompt))

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()

            try:
                if st.session_state.chain is None:
                    answer = "⚠️ Please configure your LLM provider in the sidebar first."
                else:
                    # Pass previous messages (excluding the current one just appended) to the chain
                    answer = generate_response(
                        st.session_state.chain, 
                        prompt,
                        st.session_state.messages[:-1]
                    )
            except Exception as e:
                answer = f"❌ Error: {e}"

            placeholder.markdown(answer)

        st.session_state.messages.append(("assistant", answer))


# -----------------------------
# MAIN
# -----------------------------
def main():
    init_state()
    chat_ui()


if __name__ == "__main__":
    main()
