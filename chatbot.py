from typing import Dict, List, Literal, TypedDict
from fastapi import UploadFile
import openai  # Import OpenAI API
from dotenv import load_dotenv
import os

from file import prepare_gemini_file
from qr_code import generate_unique_qr  # QR code logic


# -------------------------------------
# Load ENV + Configure OpenAI GPT
# -------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing.")

openai.api_key = OPENAI_API_KEY


# -------------------------------------
# Sessions
# -------------------------------------
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


chat_sessions: Dict[str, List[Message]] = {}
pending_offers: Dict[str, dict] = {}   # discount flow
MAX_HISTORY = 12


# -------------------------------------
# System Prompt
# -------------------------------------
SYSTEM_PROMPT = """
You are a friendly food recommendation AI assistant for Metro Manila ONLY.
Recommend restaurants ONLY within Metro Manila.
Include the restaurant name and area (Makati, BGC, Manila, Pasay, QC).
Suggest real dishes available in Manila restaurants.
If the user asks for discounts or promo codes, you may say that you can check available offers.
Always stay friendly and concise.
""".strip()


# -------------------------------------
# Internal Helpers
# -------------------------------------
def _load_session(session_id: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]


def _trim_history(session_id: str):
    history = chat_sessions.get(session_id, [])
    if len(history) > MAX_HISTORY:
        chat_sessions[session_id] = history[-MAX_HISTORY:]


def is_discount_question(message: str) -> bool:
    msg = message.lower()
    return any(k in msg for k in ["discount", "promo", "voucher", "offer", "code"])


def is_yes(message: str) -> bool:
    msg = message.lower().strip()
    return msg in {"yes", "yeah", "yep", "sure", "ok", "okay", "generate"}


async def fetch_discount_from_backend(food_query: str):
    """
    TODO: Replace with your actual backend API call.
    Return format:
        {
          "restaurant": "...",
          "area": "...",
          "item": "...",
          "discount_percent": 15
        }
    """
    return None  # currently no discounts available


# -------------------------------------
# Chat Logic (Text + Image + Discount + QR)
# -------------------------------------
async def process_chat_file(session_id: str, message: str, upload: UploadFile):
    history = _load_session(session_id)  # Load existing history or start new session
    message = (message or "").strip()

    # Process file (optional)
    gemini_file = await prepare_gemini_file(upload)
    if gemini_file:
        history.append({"role": "user", "content": f"[User uploaded: {upload.filename}]"})


    # Store the user message
    if message:
        history.append({"role": "user", "content": message})

    # Build the conversation context to pass to OpenAI
    history_text = "\n".join(f"{msg['role'].upper()}: {msg['content']}" for msg in history)

    # Prepare the prompt for OpenAI
    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Now respond as ASSISTANT:
""".strip()

    # Make the API call to OpenAI with the full conversation context
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use the GPT-4o-mini model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},  # System message for context
                *[{"role": msg["role"], "content": msg["content"]} for msg in history]  # Include the full conversation
            ],
            temperature=0.7
        )

        # Extract the assistant's response
        answer = response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"Error while calling OpenAI API: {e}")  # Log error for better debugging
        answer = "Sorry, I couldn't process your request right now."

    # Save assistant's response to history
    history.append({"role": "assistant", "content": answer})
    _trim_history(session_id)  # Limit history size if needed

    return {"reply": answer, "history": history}

