import sys
import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

# -----------------------------
# 1. CORE LOGIC (THE ENGINE)
# -----------------------------

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    elif provider == "groq":
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            from langchain_groq import ChatGroq
            return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=groq_key)

    # Fallback
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage
    return FakeMessagesListChatModel(responses=[AIMessage(content="⚠️ Provider not configured correctly.")])

class _SimpleRAGAssistant:
    def __init__(self, llm):
        self.llm = llm

    def _format_chat_history(self, chat_history):
        if not chat_history: return ""
        last = chat_history[-6:]
        return "\n".join(f"{'User' if r=='user' else 'Assistant'}: {c}" for r, c in last)

    def answer(self, question, chat_history=None, personality="You are a helpful AI assistant."):
        chat_history_text = self._format_chat_history(chat_history)
        
        BUD_TEMPLATE = """{personality}
        Chat History: {chat_history}
        Question: {question}
        Answer:"""
        
        prompt_text = BUD_TEMPLATE.format(
            personality=personality,
            chat_history=chat_history_text,
            question=question
        )

        try:
            resp = self.llm.invoke([HumanMessage(content=prompt_text)])
            return getattr(resp, "content", str(resp))
        except Exception as e:
            return f"❌ Error: {e}"

# This is the function the UI was missing!
def build_conversational_chain():
    llm = get_llm()
    return _SimpleRAGAssistant(llm)

def generate_response(chain, user_input: str, chat_history=None, personality=None):
    return chain.answer(
        question=user_input,
        chat_history=chat_history or [],
        personality=personality or "You are a helpful AI assistant."
    )

# -----------------------------
# 2. UI & INITIALIZATION
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

def llm_config_sidebar():
    st.sidebar.markdown("### ⚙️ System Control")
    st.sidebar.subheader("🛡️ Active Buddy")
    agent_mode = st.sidebar.radio("Switch Personality:", ["Professor Z", "Aman"])
    
    if agent_mode == "Professor Z":
        st.sidebar.success("👨‍🏫 **Mentor Mode**")
        st.session_state.current_personality = "You are Professor Z, a patient academic mentor. Don't give answers directly; guide the user with analogies."
    else:
        st.sidebar.warning("🏎️ **Rival Mode**")
        st.session_state.current_personality = "You are Aman, a sharp technical rival. Point out bugs bluntly and push the user to be better."

    st.sidebar.divider()
    provider = st.sidebar.selectbox("LLM Provider", ["Groq", "OpenAI"], index=0)

    if provider == "Groq":
        # API Key is hidden as a password type
        api_key = st.sidebar.text_input("Groq Key", type="password")
        if st.sidebar.button("Connect Groq"):
            os.environ["GROQ_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "groq"
            st.session_state.chain = None
            st.rerun()
    elif provider == "OpenAI":
        api_key = st.sidebar.text_input("OpenAI Key", type="password")
        if st.sidebar.button("Connect OpenAI"):
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "openai"
            st.session_state.chain = None
            st.rerun()

    if st.sidebar.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

def chat_ui():
    st.markdown("""<style>
        .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #fff; }
        .stChatMessage { background: rgba(255, 255, 255, 0.07) !important; backdrop-filter: blur(12px); border-radius: 20px; }
        </style>""", unsafe_allow_html=True)
    
    st.title("🛡️ Bud AI: The Squad Hub")
    llm_config_sidebar()
    ensure_chain()

    is_prof = "Professor Z" in st.session_state.current_personality
    assistant_avatar = "👨‍🏫" if is_prof else "🏎️"

    for role, content in st.session_state.messages:
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else assistant_avatar):
            st.markdown(content)

    if prompt := st.chat_input("Drop a message..."):
        st.session_state.messages.append(("user", prompt))
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=assistant_avatar):
            try:
                answer = generate_response(
                    st.session_state.chain, 
                    prompt, 
                    st.session_state.messages[:-1], 
                    personality=st.session_state.current_personality
                )
            except Exception as e:
                answer = f"❌ Error: {e}"
            st.markdown(answer)
        st.session_state.messages.append(("assistant", answer))

if __name__ == "__main__":
    init_state()
    chat_ui()
