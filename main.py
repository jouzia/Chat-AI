import os
os.environ["LLM_PROVIDER"] = os.getenv("LLM_PROVIDER", "groq")

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI, Depends
from auth.routes import router as auth_router
from database.config import engine, Base
from auth.security import get_current_user
from database.models import User


ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Productivity Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


# ---------- Health ----------

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Platform API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# 🔥 ADD THIS DEBUG ENDPOINT
@app.get("/debug-key")
def debug_key():
    return {"key": os.getenv("OPENAI_API_KEY")}


@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}


# ---------- Chat ----------

class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None


@app.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    from ai.assistant import build_conversational_chain

    chain = build_conversational_chain()

    async def token_stream():
        async for chunk in chain.astream({"question": req.message}):
            token = chunk.get("answer", "")
            if token:
                yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)