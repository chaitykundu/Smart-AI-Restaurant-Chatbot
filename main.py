from fastapi import FastAPI, UploadFile, File, Form
from chatbot import process_chat_file

app = FastAPI(title="Manila Food Chatbot API", version="2.0")


@app.post("/chat")
async def chat(
    session_id: str = Form(...),
    message: str = Form(""),
    file: UploadFile = File(None)
):
    return await process_chat_file(session_id, message, file)
