import os
import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

# Attempt to import vector store, handle path issues gracefully
try:
    from vector_store import get_vector_store
except ImportError:
    # If vector_store is in a parent directory
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from vector_store import get_vector_store
    except ImportError:
        get_vector_store = None

# ---------- LLM LOADER ----------
def get_llm(model: str = "auto"):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key.startswith("sk-"):
            return ChatOpenAI(model="gpt-4o", temperature=0.7)

    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if api_key.startswith("gsk_"):
            try:
                from langchain_groq import ChatGroq
                # Use the most stable 2026 model name
                return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)
            except ImportError:
                return FakeMessagesListChatModel(responses=[AIMessage(content="⚠️ Install: pip install langchain-groq")])

    elif provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), temperature=0.7)
        except ImportError:
            pass

    # Fallback with clear error message
    err_msg = f"⚠️ Provider '{provider}' not configured. Check your API keys in the sidebar."
    return FakeMessagesListChatModel(responses=[AIMessage(content=err_msg)])

# ---------- PROMPT ----------
CONVERSATION_TEMPLATE = """You are Bud AI, a helpful engineering assistant.
Use the provided context to answer. If the context isn't relevant, use your own knowledge.

Chat History:
{chat_history}

Context:
{context}

Question: {question}
Answer:"""

CONVERSATION_PROMPT = PromptTemplate.from_template(CONVERSATION_TEMPLATE)

# ---------- RAG ENGINE ----------
class _SimpleRAGAssistant:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def _format_chat_history(self, chat_history):
        if not chat_history: return ""
        # Keep last 6 exchanges for context window safety
        return "\n".join([f"{'User' if r=='user' else 'Assistant'}: {c}" for r, c in chat_history[-6:]])

    def _get_context(self, question):
        if not self.retriever: return "No additional context available."
        try:
            docs = self.retriever.get_relevant_documents(question)
            return "\n\n".join([d.page_content for d in docs])
        except Exception:
            return ""

    def invoke(self, inputs: dict):
        question = inputs.get("question", "")
        chat_history = inputs.get("chat_history", [])
        
        context = self._get_context(question)
        history_text = self._format_chat_history(chat_history)

        formatted_prompt = CONVERSATION_PROMPT.format(
            chat_history=history_text,
            context=context,
            question=question
        )

        try:
            # LangChain 2026 standard 'invoke'
            resp = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            content = getattr(resp, "content", str(resp))
            return {"answer": content}
        except Exception as e:
            return {"answer": f"❌ LLM Error: {str(e)}"}

# ---------- EXPORTED FUNCTIONS ----------
def build_conversational_chain(model: str = "auto"):
    llm = get_llm(model)
    retriever = None
    
    if get_vector_store:
        try:
            retriever = get_vector_store(collection_name="conversations").as_retriever(search_kwargs={"k": 3})
        except Exception:
            retriever = None
            
    return _SimpleRAGAssistant(llm, retriever)

def generate_response(chain, user_input: str, chat_history=None):
    # This matches the call from your app.py
    result = chain.invoke({
        "question": user_input,
        "chat_history": chat_history or []
    })
    return result["answer"]
