from fastapi import FastAPI
from chatbot import ChatRequest, process_chat

app = FastAPI(title="Manila Food Chatbot API", version="1.0")


@app.post("/chat")
async def chat(req: ChatRequest):
    return process_chat(req)
