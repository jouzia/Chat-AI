import os
from assistant import get_llm
from vector_store import get_embeddings
from langchain_core.embeddings.fake import FakeEmbeddings
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel

def test_verification():
    print("--- VERIFICATION ---")
    
    # Test embeddings
    print("Testing embeddings validation...")
    embeddings = get_embeddings()
    if isinstance(embeddings, FakeEmbeddings):
        print("[SUCCESS] Embeddings correctly fell back to FakeEmbeddings")
    else:
        print("[FAILURE] Embeddings DID NOT fall back to FakeEmbeddings")
        
    # Test main LLM (default to Groq, which is not set)
    print("\nTesting LLM validation (Groq)...")
    llm = get_llm()
    if isinstance(llm, FakeMessagesListChatModel):
        resp = llm.invoke("Hi")
        print(f"[SUCCESS] LLM correctly fell back to FakeMessagesListChatModel. Message: {resp.content}")
    else:
        print("[FAILURE] LLM DID NOT fall back to FakeMessagesListChatModel")

    # Test OpenAI LLM (set to invalid 19 char key)
    print("\nTesting LLM validation (OpenAI invalid key)...")
    os.environ["LLM_PROVIDER"] = "openai"
    llm = get_llm()
    if isinstance(llm, FakeMessagesListChatModel):
        resp = llm.invoke("Hi")
        print(f"[SUCCESS] OpenAI LLM correctly fell back. Message: {resp.content}")
    else:
        print("[FAILURE] OpenAI LLM DID NOT fall back")

    print("-------------------")

if __name__ == "__main__":
    test_verification()
