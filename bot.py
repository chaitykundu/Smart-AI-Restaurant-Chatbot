import os
from dotenv import load_dotenv
import json
from typing import Dict, Optional
from openai import OpenAI

# Import prompts
from prompt import get_system_prompt, INTENT_PROMPT, QR_EXTRACTION_PROMPT

# ===============================
# Load environment variables
# ===============================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# ===============================
# Load static restaurants & menu
# ===============================
def load_restaurant_list():
    path = os.path.join("Files", "Res_List.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

RESTAURANTS = load_restaurant_list()
base_url = "http://10.10.12.9:8001"

# ===============================
# In-memory chat state & history
# ===============================
chat_state: Dict[int, dict] = {}
chat_history: Dict[int, list[dict]] = {}

def get_chat_history(chat_id: int, limit: int = 15):
    return chat_history.get(chat_id, [])[-limit:]

def save_chat_message(chat_id: int, role: str, content: str):
    chat_history.setdefault(chat_id, []).append({"role": role, "content": content})

# ===============================
# Build system prompt with context
# ===============================
SYSTEM_PROMPT = get_system_prompt(
    "\n".join([
        f"Restaurant: {r['name']}\n>>> CURRENT MENU & OFFERS\n" +
        "\n".join(
            f"- {item['name']}: ₱{item['price']}" +
            (f" [PROMO {item['discount']}% OFF]" if item.get("discount", 0) else "")
            for item in r.get("menu", [])
        ) + "\n"
        for r in RESTAURANTS
    ])
)

# ===============================
# Helper functions
# ===============================
def extract_restaurant_from_reply(reply: str) -> Optional[str]:
    for r in RESTAURANTS:
        if r["name"].lower() in reply.lower():
            return r["name"]
    return None

def detect_intent(history: list, message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": INTENT_PROMPT}, *history[-5:], {"role": "user", "content": message}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# ===============================
# Main chat function
# ===============================
def process_chat(chat_id: int, message: str = ""):
    message = (message or "").strip()
    history = get_chat_history(chat_id)
    save_chat_message(chat_id, "user", message)

    if chat_id not in chat_state:
        chat_state[chat_id] = {"restaurant": None, "awaiting_qr_confirmation": False, "pending_offer": None}

    intent = detect_intent(history, message)

    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": message}]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_payload,
        temperature=0.7,
        max_tokens=900
    )

    reply = response.choices[0].message.content.strip()
    save_chat_message(chat_id, "assistant", reply)

    restaurant_name = extract_restaurant_from_reply(reply)
    if restaurant_name:
        chat_state[chat_id]["restaurant"] = restaurant_name

    return {"reply": reply, "intent": intent, "restaurant": chat_state[chat_id].get("restaurant")}

# ===============================
# Run interactively
# ===============================
if __name__ == "__main__":
    chat_id = 1
    print("Welcome to Choosie AI Chat! Type 'exit' to quit.")
    while True:
        user_msg = input("You: ")
        if user_msg.lower() in ("exit", "quit"):
            break
        response = process_chat(chat_id, user_msg)
        print(f"Choosie: {response['reply']}\n")
