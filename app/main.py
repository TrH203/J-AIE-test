from fastapi import FastAPI
from app.api import chat, knowledge, audit

app = FastAPI()

app.include_router(knowledge.router, prefix="/knowledge")
app.include_router(chat.router, prefix="/chat")
app.include_router(audit.router, prefix="/audit")