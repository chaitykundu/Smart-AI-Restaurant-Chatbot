from typing import Dict, List, Literal, TypedDict
from pydantic import BaseModel
from fastapi import UploadFile
import google.generativeai as genai
from dotenv import load_dotenv
import os
from file import prepare_gemini_file


# -------------------------------------
# Load ENV + Configure Gemini
# -------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------------------------
# Message Type + Session Storage
# -------------------------------------
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


chat_sessions: Dict[str, List[Message]] = {}
MAX_HISTORY = 12


# -------------------------------------
# System Prompt
# -------------------------------------
SYSTEM_PROMPT = """
You are a friendly food recommendation AI assistant for Metro Manila ONLY.
...
""".strip()


# -------------------------------------
# Helpers
# -------------------------------------
def _load_session(session_id: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]


def _trim_history(session_id: str):
    history = chat_sessions.get(session_id, [])
    if len(history) > MAX_HISTORY:
        chat_sessions[session_id] = history[-MAX_HISTORY:]


# -------------------------------------
# FINAL: Chat Logic (Supports Text + Files)
# -------------------------------------
async def process_chat_file(session_id: str, message: str, upload: UploadFile):

    history = _load_session(session_id)
    message = (message or "").strip()

    # Process file
    gemini_file = await prepare_gemini_file(upload)

    if gemini_file:
        history.append({
            "role": "user",
            "content": f"[User uploaded: {upload.filename}]"
        })

    if message:
        history.append({"role": "user", "content": message})

    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}" for msg in history
    )

    prompt_intro = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Now respond as ASSISTANT:
""".strip()

    gemini_inputs = [prompt_intro]

    if message:
        gemini_inputs.append(message)

    if gemini_file:
        gemini_inputs.append(gemini_file)

    try:
        response = model.generate_content(gemini_inputs)
        answer = (response.text or "").strip()
    except:
        answer = "Sorry, I couldn't analyze the file right now."

    history.append({"role": "assistant", "content": answer})
    _trim_history(session_id)

    return {
        "reply": answer,
        "history": history
    }
