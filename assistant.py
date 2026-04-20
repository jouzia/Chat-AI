import os
import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

# Standardizing the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Try-except for the vector store in case it's not set up yet
try:
    from vector_store import get_vector_store
except ImportError:
    get_vector_store = None

# ---------- LLM LOADER ----------
def get_llm(model: str = "auto"):
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            resolved = model if model not in ("auto",) else "gpt-3.5-turbo"
            return ChatOpenAI(model=resolved, temperature=0.7)

    elif provider == "groq":
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            from langchain_groq import ChatGroq
            return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)

    elif provider == "ollama":
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(model=ollama_model, temperature=0.7)
        except ImportError:
            pass

    # Fallback to a fake model with an error message
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage
    return FakeMessagesListChatModel(responses=[AIMessage(content="⚠️ Provider not configured correctly.")])

# ---------- BUD AI PROMPT TEMPLATE ----------
# Added {personality} so the agent knows if it's Prof Z or Aman
BUD_TEMPLATE = """{personality}

Use the following context if available to help the student.
If no context is found, answer based on your persona.

Chat History:
{chat_history}

Context:
{context}

Question: {question}

Answer:"""

BUD_PROMPT = PromptTemplate.from_template(BUD_TEMPLATE)

# ---------- THE ASSISTANT CLASS ----------
class _SimpleRAGAssistant:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def _format_chat_history(self, chat_history):
        if not chat_history: return ""
        last = chat_history[-6:]
        return "\n".join(f"{'User' if r=='user' else 'Assistant'}: {c}" for r, c in last)

    def _get_context(self, question):
        if not self.retriever: return ""
        try:
            docs = self.retriever.get_relevant_documents(question)
            return "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)
        except: return ""

    def answer(self, question, chat_history=None, personality="You are a helpful AI assistant."):
        context = self._get_context(question)
        chat_history_text = self._format_chat_history(chat_history)

        # Injects the Mascot Personality here!
        prompt_text = BUD_PROMPT.format(
            personality=personality,
            chat_history=chat_history_text,
            context=context,
            question=question,
        )

        try:
            resp = self.llm.invoke([HumanMessage(content=prompt_text)])
            return getattr(resp, "content", str(resp))
        except Exception as e:
            return f"❌ Error: {e}"


    # ---------- HELPER ----------
def generate_response(chain, user_input: str, chat_history=None, personality=None):
    # This now matches the call in your app.py
    return chain.answer(
        question=user_input,
        chat_history=chat_history or [],
        personality=personality
    )

def generate_response(chain, user_input: str, chat_history=None, personality=None):
    # Now accepts 'personality' from app.py
    return chain.answer(
        question=user_input,
        chat_history=chat_history or [],
        personality=personality or "You are a helpful AI assistant."
    )