import os
import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

try:
    from vector_store import get_vector_store
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from vector_store import get_vector_store
    except ImportError:
        get_vector_store = None

def get_llm(model: str = "auto"):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key.startswith("sk-"):
            return ChatOpenAI(model="gpt-4o", temperature=0.8)
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if api_key.startswith("gsk_"):
            from langchain_groq import ChatGroq
            return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.8)
    # Fallback
    return FakeMessagesListChatModel(responses=[AIMessage(content="⚠️ Check your API keys, dev!")])

# --- THE WITTY PROMPT ---
CONVERSATION_TEMPLATE = """You are Bud AI, a brilliant but super chill engineering assistant. 
Think of yourself as a senior dev peer who actually enjoys helping out.

CHILL RULES:
1. Use tech puns and engineering humor (keep it fun, not robotic).
2. Use emojis to keep the energy high (🚀, 💻, ⚡, 🎨).
3. If you're stuck, say "Internal Server Error in my brain! Try again?"
4. Be a hype-man for the user's projects.

History: {chat_history}
Context: {context}
Question: {question}
Answer:"""

CONVERSATION_PROMPT = PromptTemplate.from_template(CONVERSATION_TEMPLATE)

class _SimpleRAGAssistant:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def _format_chat_history(self, chat_history):
        if not chat_history: return ""
        return "\n".join([f"{'User' if r=='user' else 'Assistant'}: {c}" for r in chat_history[-6:]])

    def _get_context(self, question):
        if not self.retriever: return "No extra docs found."
        try:
            docs = self.retriever.get_relevant_documents(question)
            return "\n\n".join([d.page_content for d in docs])
        except: return ""

    def invoke(self, inputs: dict):
        question, chat_history = inputs.get("question", ""), inputs.get("chat_history", [])
        formatted_prompt = CONVERSATION_PROMPT.format(
            chat_history=self._format_chat_history(chat_history),
            context=self._get_context(question),
            question=question
        )
        try:
            resp = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            return {"answer": getattr(resp, "content", str(resp))}
        except Exception as e:
            return {"answer": f"❌ Logic Error: {str(e)}"}

def build_conversational_chain(model: str = "auto"):
    llm = get_llm(model)
    retriever = None
    if get_vector_store:
        try: retriever = get_vector_store(collection_name="conversations").as_retriever(search_kwargs={"k": 3})
        except: retriever = None
    return _SimpleRAGAssistant(llm, retriever)

def generate_response(chain, user_input: str, chat_history=None):
    return chain.invoke({"question": user_input, "chat_history": chat_history or []})["answer"]
