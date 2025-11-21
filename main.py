from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

# Request body
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # Prompt logic (can improve later)
    prompt = f"""
    You are a food recommendation AI assistant for MANILA only.

    RULES:
    - Only recommend restaurants located within Metro Manila.
    - Include name, area (e.g., Makati, BGC, Manila City, Pasay).
    - You can also suggest dishes available in Manila restaurants.
    - Never recommend foreign cities or non-Manila places.
    - Keep responses short, friendly, and helpful.

    User request: {req.message}
    """


    response = model.generate_content(prompt)
    answer = response.text

    return {"reply": answer}
