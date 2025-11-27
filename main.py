# main.py
from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
import tempfile
import os

from chatbot import handle_chat

app = FastAPI(title="Manila Food Chatbot API", version="2.0")


@app.post("/chat")
async def chat(
    session_id: str = Form(...),
    message: str = Form(""),
   file: Optional[UploadFile] = File(None) 
):
    """
    Single ChatGPT-style endpoint.

    Supports:
    - Text-only chat (just send session_id + message)
    - Chat with file (send session_id + message + file)
    """

    # Case 1: no file → text-only chat
    if file is None:
        result = handle_chat(
            session_id=session_id,
            message=message,
            file_path=None,
            mime_type=None
        )
        return result

    # Case 2: file uploaded → save temp then send to Gemini
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = handle_chat(
            session_id=session_id,
            message=message,
            file_path=tmp_path,
            mime_type=file.content_type
        )
    finally:
        # clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return result
