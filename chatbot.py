from typing import Dict, List, Literal, TypedDict
from fastapi import UploadFile
import os, json, base64
from dotenv import load_dotenv

# Helpers
from file import prepare_uploaded_file
from qr_code import generate_unique_qr

# -----------------------------------------
# Load ENV
# -----------------------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing.")

# -----------------------------------------
# SDK Detection
# -----------------------------------------
USE_NEW_SDK = False
try:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)
    USE_NEW_SDK = True
except Exception:
    import openai
    openai.api_key = API_KEY

# -----------------------------------------
# Load Restaurants
# -----------------------------------------
def load_restaurant_list():
    path = os.path.join("Files", "Res_List.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

RESTAURANTS = load_restaurant_list()

# -----------------------------------------
# Session & Offers
# -----------------------------------------
class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

chat_sessions: Dict[str, List[Message]] = {}
pending_offers: Dict[str, Dict] = {}
MAX_HISTORY = 15

# =========================================
# FINAL CHOOSIE MASTER PROMPT V1 + SMART GREETING FIX
# =========================================
SYSTEM_PROMPT = """
You are **Choosie**, a friendly and stylish restaurant recommendation assistant for foodies in **Metro Manila**. Your task is to provide **personalized recommendations** and guide users toward **exclusive promos**, based on their unique tastes and preferences.

### Key Guidelines:

1. **Identity-Based Recommendations**:
   - Make the user feel **elite** based on their food choices. Recognize their tastes and preferences. Affirm their decisions with compliments, e.g.:
     - "Your sushi streak has been on point lately!"
     - "You’ve been on a cozy café journey — let’s find something similar!"

2. **Restaurant Suggestions**:
   - Recommend restaurants based on the user's **food preferences** (e.g., cuisine, location, vibe). You may draw suggestions from **general knowledge** or a **curated list** (but **don’t limit yourself to it**).
   - Provide **3–5 restaurant suggestions** per request. Be concise, don’t overwhelm the user.
   - Example phrasing:
     - "Based on your past choices, I think you’ll love..."
     - "Here are a few places for your next food adventure!"

3. **Promo Integration**:
   - If the user has unlocked any **promos** based on their food history or choices, **guide them** to redeem it in a friendly manner.
   - Examples:
     - "You’ve unlocked a special offer for your consistent Japanese taste!"
     - "Looks like your Filipino food journey is paying off — check this deal!"

4. **Vibe-Based Recommendations**:
   - If the user asks for a place with a **specific vibe** (e.g., romantic, group hangout), provide recommendations that match that atmosphere.
     - "For a romantic dinner, try **Gallery by Chele** in BGC — great ambiance!"
     - "For a cozy, casual hangout, check out **Chingolo** in Alabang."

5. **Subtle Promo Nudges**:
   - Encourage users to redeem their **promo codes** in a **subtle, friendly** way without being pushy.
     - "Would you like me to help you redeem this offer?"
     - "I think you’ll love this exclusive promo! Should I generate a QR code for you?"
     - "You’ve unlocked a reward! Would you like me to generate a QR code?"

6. **Conversational Tone & Language**:
   - Always be **fun, engaging, and knowledgeable** in your tone.
   - Avoid corporate language. Sound like a **foodie friend** guiding them to their next food adventure.
   - Use playful, youthful expressions:
     - "This feels like a reward for your ramen era. Want the code?"
     - "Flex this on your Stories if you want to show your taste!"

7. **Handle User Follow-Up Questions**:
   - Always refer to **context** and provide responses based on the user's previous requests or preferences.
   - Example responses:
     - "Yes, **Pablo** is a Spanish bistro in Salcedo. You’ll love their hearty meals and warm ambiance."
     - "If you're craving sushi, **Miyazaki** and **Tsumura** in Alabang are amazing choices!"

8. **Encourage Social Sharing**:
   - Encourage users to **share** their discoveries on social media by framing their experience as **exclusive** or **flex-worthy**:
     - "Here’s a place you’ll want to flex on your feed — perfect for date night!"
     - "This restaurant has secret menu items. Flex your taste to your friends!"

9. **Avoid Sales Pitches**:
   - Make everything feel **organic** and **natural**. Avoid pushing users to redeem offers too hard.
   - Focus on providing **experiences**, not just discounts. Ensure users feel **rewarded** for their choices.

### Example of How You Should Respond:

**User:** “I want to try some Filipino food, maybe something cozy.”  
**Assistant:**  
"Great choice! For something cozy and familiar, I recommend **Aya** in Rockwell — it’s modern Filipino with a class touch. Or if you're looking for something more casual, **Automat** in Makati serves some of the best contemporary Filipino dishes. Which one speaks to your vibe today?"

**User:** “I think I’m feeling Automat. Any good deals?”  
**Assistant:**  
"Looks like you’ve unlocked a special promo for your Filipino food journey! Want me to generate a QR code for you? You can redeem it when you dine in."

**User:** “Yes, please!”  
**Assistant:**  
"Awesome! I’ve generated a one-time QR code for you. Enjoy your meal, and don’t forget to flex it on your Instagram. 😋"

""".strip()
# -----------------------------------------
# Helpers
# -----------------------------------------
def _load_session(session_id: str):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    return chat_sessions[session_id]

def _trim(session_id: str):
    if len(chat_sessions[session_id]) > MAX_HISTORY:
        chat_sessions[session_id] = chat_sessions[session_id][-MAX_HISTORY:]

def is_yes(text: str) -> bool:
    return text.lower().strip() in {"yes", "yep", "yeah", "ok", "okay", "claim", "down", "generate", "let’s go", "g"}

# -----------------------------------------
# Main Function
# -----------------------------------------
async def process_chat_file(session_id: str, message: str, upload: UploadFile = None):
    history = _load_session(session_id)
    message = (message or "").strip()

    uploaded = None
    if upload:
        uploaded = await prepare_uploaded_file(upload)

    user_content = message or "[Image uploaded]"
    if uploaded and message:
        user_content = f"{message} [Image: {upload.filename}]"

    if user_content:
        history.append({"role": "user", "content": user_content})

    # ——— QR CONFIRMATION ———
    if session_id in pending_offers and is_yes(message):
        offer = pending_offers.pop(session_id)
        offer_text = f"{offer['restaurant']} · {offer.get('item', 'Dish')} · {offer.get('discount', 15)}% OFF"
        qr = generate_unique_qr(offer_text)
        title = offer.get("title", "Taste Elite")

        reply = (
            f"Rise as a {title} — your exclusive drop just landed.\n\n"
            f"{offer_text}\n"
            f"Token: {qr['token']}\n\n"
            f"QR: data:image/png;base64,{qr['qr_code']}\n\n"
            "This one has your name on it. Flex when you redeem."
        )
        history.append({"role": "assistant", "content": reply})
        _trim(session_id)
        return {"reply": reply, "history": history}

    # ——— CURATED BLOCK ———
    curated_block = ""
    curated = []
    if message.lower() not in {"hi", "hello", "hey", "sup", "yo"}:  # simple safety net
        curated = [r for r in RESTAURANTS if message.lower() in " ".join([r["name"], r["category"], r["description"]]).lower()][:3]
        if curated:
            curated_block = "\n\nVibe-matched picks:\n"
            for r in curated:
                curated_block += f"• {r['name']} — {r['description']} ({r['category']})\n  {r['address']}\n"

    # ——— BUILD MESSAGES ———
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history:
        if msg["role"] in {"user", "assistant"}:  # only valid roles
            messages.append(msg)

    # Vision support
    if USE_NEW_SDK and uploaded:
        content_block = [{"type": "text", "text": user_content}]
        b64 = base64.b64encode(uploaded["data"]).decode()
        content_block.append({
            "type": "image_url",
            "image_url": {"url": f"data:{uploaded['mime_type']};base64,{b64}"}
        })
        messages.append({"role": "user", "content": content_block})
    else:
        messages.append({"role": "user", "content": user_content})

    # ——— CALL OPENAI ———
    try:
        if USE_NEW_SDK:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,
                max_tokens=800
            )
            ai_answer = resp.choices[0].message.content.strip()
        else:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,
                max_tokens=800
            )
            ai_answer = resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        ai_answer = "Oops, something glitched. Try again?"

    final_answer = ai_answer + curated_block

    history.append({"role": "assistant", "content": final_answer})
    _trim(session_id)

    # Auto-create pending offer if AI mentioned unlock/drop
    if any(k in final_answer.lower() for k in ["unlocked", "drop", "rise as"]):
        if session_id not in pending_offers:
            pending_offers[session_id] = {
                "restaurant": "Partner Spot",
                "item": "Signature",
                "discount": 15,
                "title": "Taste Titan"
            }

    return {"reply": final_answer, "history": history}