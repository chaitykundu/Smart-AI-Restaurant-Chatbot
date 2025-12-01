from typing import Dict, List, Literal, TypedDict
from fastapi import UploadFile
import google.generativeai as genai
from dotenv import load_dotenv
import os

from file import prepare_gemini_file
from qr_utils import generate_unique_qr   # <-- QR system


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

    history = _load_session(session_id)
    message = (message or "").strip()

    # Handle file upload
    gemini_file = await prepare_gemini_file(upload)
    if gemini_file:
        history.append({"role": "user", "content": f"[User uploaded: {upload.filename}]"})


    # Store user message
    if message:
        history.append({"role": "user", "content": message})


    # ------------------------------------------
    # 1) USER SAID YES → GENERATE QR CODE
    # ------------------------------------------
    if session_id in pending_offers and is_yes(message):
        offer = pending_offers.pop(session_id)

        offer_text = f"{offer['restaurant']} | {offer['item']} | {offer['discount_percent']}% OFF"
        qr_result = generate_unique_qr(offer_text)

        reply = (
            "Great! Here is your one-time promo QR code 🎉\n\n"
            f"Offer: {offer_text}\n"
            f"Token: {qr_result['token']}\n\n"
            "Scan this QR:\n"
            f"data:image/png;base64,{qr_result['qr_code']}"
        )

        history.append({"role": "assistant", "content": reply})
        _trim_history(session_id)

        return {"reply": reply, "history": history}


    # ------------------------------------------
    # 2) USER ASKED FOR DISCOUNT
    # ------------------------------------------
    if is_discount_question(message):
        offer = await fetch_discount_from_backend(message)

        if offer:
            pending_offers[session_id] = offer

            reply = (
                f"Yes! There is a {offer['discount_percent']}% discount on "
                f"{offer['item']} at {offer['restaurant']} in {offer['area']}.\n\n"
                "Would you like me to generate a one-time QR code for this offer?"
            )

            history.append({"role": "assistant", "content": reply})
            _trim_history(session_id)

            return {"reply": reply, "history": history}
        # else → let Gemini handle


    # ------------------------------------------
    # 3) Normal Gemini Response
    # ------------------------------------------
    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}" for msg in history
    )

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Now respond as ASSISTANT:
""".strip()

    gemini_inputs = [prompt]

    if message:
        gemini_inputs.append(message)
    if gemini_file:
        gemini_inputs.append(gemini_file)

    try:
        response = model.generate_content(gemini_inputs)
        answer = (response.text or "").strip()
    except:
        answer = "Sorry, I couldn't process your request right now."

    history.append({"role": "assistant", "content": answer})
    _trim_history(session_id)

    return {"reply": answer, "history": history}
