
# main.py
from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
import tempfile
import os
from fastapi import FastAPI

from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from qr_utils import generate_qr_for_promo
import os

from chatbot import ChatRequest, process_chat


from chatbot import handle_chat

app = FastAPI(title="Manila Food Chatbot API", version="2.0")
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

# Serve QR folder
from fastapi.staticfiles import StaticFiles
app.mount("/qr_codes", StaticFiles(directory="qr_codes"), name="qr_codes")


class ChatRequest(BaseModel):
    message: str
    history: list = []     # 🟢 VERY IMPORTANT — Store previous messages


@app.post("/chat")
async def chat(req: ChatRequest):

    user_msg = req.message.lower()

    # 1️⃣ PHASE 1 — Check if user previously asked for promo confirmation
    if req.history:
        last_bot_msg = req.history[-1].get("bot", "").lower()

        if "generate the promo code for you" in last_bot_msg:
            # User answered
            if "yes" in user_msg or "sure" in user_msg or "okay" in user_msg:
                promo_code, qr_path = generate_qr_for_promo("Special Promo")

                return {
                    "reply": f"Great! 🎉 Here’s your promo code:\n**{promo_code}**",
                    "qr_image_url": f"/qr_codes/{qr_path}",
                    "promo_code": promo_code,
                    "is_promo": True,
                    "history": req.history + [{"user": req.message, "bot": "Promo generated"}]
                }
            else:
                return {
                    "reply": "No problem! Let me know if you need anything else 😊",
                    "is_promo": False,
                    "history": req.history + [{"user": req.message, "bot": "User declined promo"}]
                }

    # 2️⃣ PHASE 2 — Detect if user is asking for offers
    intent_prompt = f"""
    Determine if this message is asking for:
    - promo
    - discount
    - special offer
    - deal
    - free item
    - cheaper option

    If yes return ONLY "PROMO_INTENT".
    If not return ONLY "NORMAL".

    User message: {req.message}
    """

    intent = model.generate_content(intent_prompt).text.strip()

    if "PROMO_INTENT" in intent:
        # 2A — Bot gives a SHORT offer message & asks for confirmation
        offer_prompt = f"""
        Create a SHORT exciting message about a random Manila restaurant offer.
        Format:
        - 1 sentence describing a special offer
        - Then ask: "Would you like me to generate the promo code for you?"
        """

        offer_text = model.generate_content(offer_prompt).text.strip()

        return {
            "reply": offer_text,
            "is_promo": False,
            "history": req.history + [{"user": req.message, "bot": offer_text}]
        }

    # 3️⃣ PHASE 3 — Normal food recommendation
    rec_prompt = f"""
    You are a Manila-only restaurant recommendation AI.
    Keep responses friendly and short.

    User: {req.message}
    """

    response = model.generate_content(rec_prompt).text.strip()

    return {
        "reply": response,
        "is_promo": False,
        "history": req.history + [{"user": req.message, "bot": response}]
    }
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

async def chat(req: ChatRequest):
    return process_chat(req)
