from typing import Dict, List, Literal, TypedDict
from fastapi import UploadFile
import openai
from dotenv import load_dotenv
import os, json

from file import prepare_gemini_file
from qr_code import generate_unique_qr


# -------------------------------------
# Load ENV + Configure OpenAI GPT
# -------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing.")

openai.api_key = OPENAI_API_KEY


# -------------------------------------
# Load Restaurant List from JSON
# -------------------------------------
def load_restaurant_list():
    path = os.path.join("Files", "Res_List.json")
    if not os.path.exists(path):
        print(" Res_List.json NOT FOUND! Returning empty list.")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading Res_List.json:", e)
        return []


RESTAURANTS = load_restaurant_list()


# -------------------------------------
# Sessions
# -------------------------------------
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


chat_sessions: Dict[str, List[Message]] = {}
pending_offers: Dict[str, dict] = {}
MAX_HISTORY = 12


# -------------------------------------
# System Prompt
# -------------------------------------
SYSTEM_PROMPT = """
You are a friendly restaurant recommendation AI assistant for Metro Manila only.
Your job:
- Recommend Manila restaurants (you may use general knowledge).
- Additionally, enhance suggestions using curated restaurants from the JSON file if relevant.
- NEVER restrict recommendations only to curated ones.
- If user uploads an image, acknowledge it.
- If user asks for discounts, check backend logic.
- Always be friendly, concise, and helpful.
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


def is_discount_question(message: str):
    msg = message.lower()
    return any(k in msg for k in ["discount", "promo", "voucher", "offer", "code"])


def is_yes(message: str):
    msg = message.strip().lower()
    return msg in {"yes", "yeah", "yep", "sure", "ok", "okay", "generate"}


async def fetch_discount_from_backend(food_query: str):
    """TODO: Replace this with your real backend API."""
    return None


# -------------------------------------
# Curated Restaurant Search
# -------------------------------------
def search_curated_restaurants(query: str):
    if not query:
        return []
    query = query.lower()
    results = []

    for r in RESTAURANTS:
        if (
            query in r["name"].lower()
            or query in r["category"].lower()
            or query in r["description"].lower()
            or query in r["address"].lower()
        ):
            results.append(r)

    return results[:3]  # limit suggestions


# -------------------------------------
# MAIN CHAT HANDLER
# -------------------------------------
async def process_chat_file(session_id: str, message: str, upload: UploadFile):
    history = _load_session(session_id)
    message = (message or "").strip()

    # -----------------------
    # File Upload Handling
    # -----------------------
    gemini_file = await prepare_gemini_file(upload)
    if gemini_file:
        history.append({"role": "user", "content": f"[User uploaded: {upload.filename}]"})

    # -----------------------
    # Save User Message
    # -----------------------
    if message:
        history.append({"role": "user", "content": message})

    # -----------------------
    # Discount → YES → Generate QR
    # -----------------------
    if session_id in pending_offers and is_yes(message):
        offer = pending_offers.pop(session_id)
        offer_text = f"{offer['restaurant']} | {offer['item']} | {offer['discount_percent']}% OFF"

        qr_data = generate_unique_qr(offer_text)

        reply = (
            "Great! Here's your one-time promo QR code 🎉\n\n"
            f"Offer: {offer_text}\n"
            f"Token: {qr_data['token']}\n\n"
            f"Scan this QR:\n"
            f"data:image/png;base64,{qr_data['qr_code']}"
        )

        history.append({"role": "assistant", "content": reply})
        _trim_history(session_id)
        return {"reply": reply, "history": history}

    # -----------------------
    # User Asks About Discount
    # -----------------------
    if is_discount_question(message):
        offer = await fetch_discount_from_backend(message)

        if offer:
            pending_offers[session_id] = offer

            reply = (
                f"Yes! There's a {offer['discount_percent']}% discount on "
                f"{offer['item']} at {offer['restaurant']} ({offer['area']}).\n\n"
                "Would you like me to generate a one-time QR code for this offer?"
            )

            history.append({"role": "assistant", "content": reply})
            _trim_history(session_id)
            return {"reply": reply, "history": history}

    # -----------------------
    # Curated Suggestion Block
    # -----------------------
    curated = search_curated_restaurants(message)

    curated_block = ""
    if curated:
        curated_block = "\n\nHere are some curated picks you might also like:\n"
        for r in curated:
            curated_block += (
                f"• **{r['name']}** ({r['category']})\n"
                f"  📍 {r['address']}\n"
                f"  ✨ {r['description']}\n"
            )

    # -----------------------
    # GPT-4o-mini Response
    # -----------------------
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history
            ],
            temperature=0.7
        )

        ai_answer = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("OpenAI error:", e)
        ai_answer = "Sorry, I couldn't process that right now."

    final_answer = ai_answer + curated_block

    history.append({"role": "assistant", "content": final_answer})
    _trim_history(session_id)

    return {"reply": final_answer, "history": history}
