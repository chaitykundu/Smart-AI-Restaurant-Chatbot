from pydantic import BaseModel
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
# Chat Logic Function
# -------------------------------------
def process_chat(req: ChatRequest):
    """
    Handles chat messages, maintains history,
    communicates with Gemini, and returns the result.
    """

    # Create session if not exists
    if req.session_id not in chat_sessions:
        chat_sessions[req.session_id] = []

    # Append user message
    chat_sessions[req.session_id].append({
        "role": "user",
        "content": req.message
    })

    # Build history text
    history_text = ""
    for msg in chat_sessions[req.session_id]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    # AI Prompt
    prompt = f"""
    You are a food recommendation AI assistant for MANILA only.

    RULES:
    - Recommend restaurants ONLY within Metro Manila.
    - Include the restaurant name and the area (Makati, BGC, Manila, Pasay).
    - Suggest dishes available in Manila.
    - Keep replies short, friendly, and helpful.

    Conversation History:
    {history_text}

    User request: {req.message}
    """

    # Gemini API Call
    response = model.generate_content(prompt)
    answer = response.text

    # Save AI message to history
    chat_sessions[req.session_id].append({
        "role": "assistant",
        "content": answer
    })

    return {
        "reply": answer,
        "history": chat_sessions[req.session_id]
    }