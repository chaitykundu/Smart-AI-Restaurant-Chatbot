from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
import os


# -------------------------------------
# Load ENV + Configure Gemini
# -------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------------------------
# Chat History (In-Memory)
# -------------------------------------
chat_sessions = {}   # {session_id: [ {role, content}, ... ]}


# -------------------------------------
# Request Model
# -------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str


# -------------------------------------
# Single chat handler: with or without file
# -------------------------------------
def handle_chat(
    session_id: str,
    message: str,
    file_path: Optional[str] = None,
    mime_type: Optional[str] = None
):
    """
    Single function for chat:
    - If file_path is None  -> normal text chat
    - If file_path is given -> chat with file context
    """

    # Ensure session exists
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    # Append user message if provided
    if message:
        chat_sessions[session_id].append({
            "role": "user",
            "content": message
        })

    # Build history text
    history_text = ""
    for msg in chat_sessions[session_id]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    # Base system prompt
    base_prompt = f"""
    You are a food recommendation AI assistant for MANILA only.

    RULES:
    - Recommend restaurants ONLY within Metro Manila.
    - Include the restaurant name and the area (Makati, BGC, Manila, Pasay).
    - Suggest dishes available in Manila.
    - Keep replies short, friendly, and helpful.

    Conversation History:
    {history_text}

    User message: {message if message else "User only uploaded a file."}
    """

    # If there is a file, upload it and include it in the request
    if file_path is not None:
        if mime_type:
            uploaded_file = genai.upload_file(path=file_path, mime_type=mime_type)
        else:
            uploaded_file = genai.upload_file(path=file_path)

        # File + prompt together
        response = model.generate_content([uploaded_file, base_prompt])
    else:
        # Text-only
        response = model.generate_content(base_prompt)

    answer = response.text

    # Save assistant message
    chat_sessions[session_id].append({
        "role": "assistant",
        "content": answer
    })

    return {
        "reply": answer,

        "history": chat_sessions[session_id]

        "history": chat_sessions[req.session_id]
    }