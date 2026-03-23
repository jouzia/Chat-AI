import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from vector_store import get_vector_store
from langchain_core.messages import HumanMessage
import streamlit as st
import os
import sys
import os
print(os.getcwd())
print(os.listdir(".."))
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# ---------- LLM ----------
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

    # fallback
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage

    err_msg = f"⚠️ Please configure {provider} API key or settings. Choose a provider from the sidebar."
    if provider == "ollama":
        err_msg = "⚠️ Make sure Ollama is installed and running locally on port 11434, or check 'pip install langchain-community'."

    return FakeMessagesListChatModel(
        responses=[AIMessage(content=err_msg)]
    )


# ---------- PROMPT ----------
CONVERSATION_TEMPLATE = """You are a helpful AI assistant.

Use context if available.
If not, answer normally.

Chat History:
{chat_history}

Context:
{context}

Question: {question}

Answer:"""

CONVERSATION_PROMPT = PromptTemplate.from_template(CONVERSATION_TEMPLATE)


# ---------- CHAIN ----------
def build_conversational_chain(model: str = "auto"):
    llm = get_llm(model)

    try:
        retriever = get_vector_store(
            collection_name="conversations"
        ).as_retriever(search_kwargs={"k": 5})
    except Exception:
        retriever = None

    return _SimpleRAGAssistant(llm, retriever)


class _SimpleRAGAssistant:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def _format_chat_history(self, chat_history):
        if not chat_history:
            return ""

        last = chat_history[-6:]
        return "\n".join(
            f"{'User' if r=='user' else 'Assistant'}: {c}"
            for r, c in last
        )

    def _get_context(self, question):
        if not self.retriever:
            return ""

        try:
            docs = self.retriever.get_relevant_documents(question)
            return "\n\n".join(
                getattr(d, "page_content", str(d)) for d in docs
            )
        except Exception:
            return ""

    def answer(self, question, chat_history=None):
        context = self._get_context(question)
        chat_history_text = self._format_chat_history(chat_history)

        prompt = CONVERSATION_PROMPT.format(
            chat_history=chat_history_text,
            context=context,
            question=question,
        )

        try:
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            return getattr(resp, "content", str(resp))
        except Exception as e:
            return f"❌ Error: {e}"

    def invoke(self, inputs: dict):
        return {
            "answer": self.answer(
                inputs.get("question", ""),
                chat_history=inputs.get("chat_history"),
            )
        }


# ---------- HELPER ----------
def generate_response(chain, user_input: str, chat_history=None):
    return chain.invoke({
        "question": user_input,
        "chat_history": chat_history or []
    })["answer"]