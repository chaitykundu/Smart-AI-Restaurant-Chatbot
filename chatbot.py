from typing import Dict, List, Literal, TypedDict
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

# -------------------------------------
# Load ENV + Configure Gemini
# -------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # Fail fast if key is missing – easier to debug
    raise RuntimeError("GEMINI_API_KEY is not set in the environment.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# -------------------------------------
# Types & In-Memory Chat Storage
# -------------------------------------
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


chat_sessions: Dict[str, List[Message]] = {}  # {session_id: [ {role, content}, ... ]}
MAX_HISTORY_MESSAGES = 12  # limit total messages per session to avoid memory issues


# -------------------------------------
# Request Model (used by FastAPI)
# -------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str


# -------------------------------------
# System Prompt (Chatbot Behavior)
# -------------------------------------
SYSTEM_PROMPT = """
You are a friendly food recommendation AI assistant for Metro Manila ONLY.

RULES:
- Recommend restaurants ONLY within Metro Manila.
- Always include the restaurant name AND the area (e.g., Makati, BGC, Manila, Pasay, Quezon City, Mandaluyong, Ortigas).
- Suggest realistic dishes you can typically find in Manila.
- If the user asks about locations outside Metro Manila, politely explain that you are limited to Metro Manila only.
- Keep replies short, friendly, and helpful.
- If the user is vague (e.g., "I'm hungry"), ask 1–2 clarifying questions (budget, cuisine, area) before giving a final recommendation.
""".strip()


# -------------------------------------
# Helper: Get/Init Session
# -------------------------------------
def _get_session_history(session_id: str) -> List[Message]:
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]


def _trim_history(session_id: str) -> None:
    """
    Keep only the last MAX_HISTORY_MESSAGES messages for that session.
    """
    history = chat_sessions.get(session_id, [])
    if len(history) > MAX_HISTORY_MESSAGES:
        chat_sessions[session_id] = history[-MAX_HISTORY_MESSAGES:]


# -------------------------------------
# Core Chat Logic Function
# -------------------------------------
def process_chat(req: ChatRequest):
    """
    Handles chat messages, maintains history,
    communicates with Gemini, and returns the result.
    """

    session_id = req.session_id
    user_message = (req.message or "").strip()

    # Guard: handle empty message
    if not user_message:
        # Don't change history, just respond nicely
        return {
            "reply": "Please type something about food or restaurants in Metro Manila 😊",
            "history": chat_sessions.get(session_id, []),
        }

    # Get or create history
    history = _get_session_history(session_id)

    # Append user message to history
    history.append({"role": "user", "content": user_message})

    # Build history text for the prompt
    # Example:
    # USER: ...
    # ASSISTANT: ...
    history_text_lines = []
    for msg in history:
        role_upper = msg["role"].upper()
        history_text_lines.append(f"{role_upper}: {msg['content']}")
    history_text = "\n".join(history_text_lines) if history_text_lines else "No previous conversation."

    # Final prompt to Gemini
    prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:
{history_text}

Now respond as the assistant to the last user message in a concise, friendly way.
ASSISTANT:
""".strip()

    try:
        # Gemini API Call
        response = model.generate_content(prompt)
        answer = (response.text or "").strip()
    except Exception as e:
        # Fallback in case of API error
        answer = (
            "Sorry, I'm having trouble accessing my recommendations right now. "
            "Please try again in a moment."
        )
        # In a real app, you would log `e` using proper logging

    if not answer:
        # Another safety net
        answer = "Hmm, I couldn't generate a response. Could you please try asking in a different way?"

    # Save AI message to history
    history.append({
        "role": "assistant",
        "content": answer,
    })

    # Trim history so it doesn't grow forever
    _trim_history(session_id)

    return {
        "reply": answer,
        "history": history,
    }
