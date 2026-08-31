import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage


# ---------- LLM LOADER ----------
def get_llm(model: str = "auto"):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            resolved = model if model != "auto" else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return ChatOpenAI(model=resolved, temperature=0.7)

    if provider == "groq":
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0.7,
                groq_api_key=groq_key,
            )

    # Safe fallback so the API still starts when no provider is configured.
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
    from langchain_core.messages import AIMessage
    return FakeMessagesListChatModel(
        responses=[AIMessage(content="AI provider is not configured. Set GROQ_API_KEY or OPENAI_API_KEY.")]
    )


# ---------- BUD AI PROMPT ----------
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


class _SimpleAssistant:
    def __init__(self, llm):
        self.llm = llm

    def _format_chat_history(self, chat_history):
        if not chat_history:
            return ""
        last = chat_history[-6:]
        return "\n".join(
            f"{'User' if role == 'user' else 'Assistant'}: {content}"
            for role, content in last
        )

    def _prompt(self, question, chat_history=None, personality=None):
        return BUD_PROMPT.format(
            personality=personality or "You are a helpful AI assistant.",
            chat_history=self._format_chat_history(chat_history),
            context="",
            question=question,
        )

    def answer(self, question, chat_history=None, personality=None):
        try:
            response = self.llm.invoke([
                HumanMessage(content=self._prompt(question, chat_history, personality))
            ])
            return getattr(response, "content", str(response))
        except Exception as exc:
            return f"AI error: {exc}"

    async def astream(self, payload):
        question = payload.get("question", "")
        prompt = self._prompt(question)

        try:
            async for chunk in self.llm.astream([HumanMessage(content=prompt)]):
                content = getattr(chunk, "content", "")
                if content:
                    yield {"answer": content}
        except Exception as exc:
            yield {"answer": f"AI error: {exc}"}


def build_conversational_chain():
    """Build the lightweight API chat chain without ChromaDB/Streamlit dependencies."""
    return _SimpleAssistant(get_llm())


def generate_response(chain, user_input: str, chat_history=None, personality=None):
    return chain.answer(
        question=user_input,
        chat_history=chat_history or [],
        personality=personality or "You are a helpful AI assistant.",
    )
