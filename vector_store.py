import os
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings.fake import FakeEmbeddings


def get_embeddings():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAIEmbeddings()
    else:
        # FakeEmbeddings for local testing without an API key
        return FakeEmbeddings(size=1536)


def get_vector_store(collection_name: str = "conversations"):
    """
    Returns a LangChain-compatible Chroma vector store backed by a persistent
    ChromaDB client.  Falls back to FakeEmbeddings when no OPENAI_API_KEY is set.
    """
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    embeddings = get_embeddings()

    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )


def add_documents(texts: list[str], metadatas: list[dict] = None,
                  collection_name: str = "conversations"):
    """
    Chunk and embed a list of text strings, then upsert them into ChromaDB.
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    docs = []
    for i, text in enumerate(texts):
        meta = metadatas[i] if metadatas else {}
        chunks = splitter.create_documents([text], metadatas=[meta])
        docs.extend(chunks)

    store = get_vector_store(collection_name)
    store.add_documents(docs)
    return len(docs)
