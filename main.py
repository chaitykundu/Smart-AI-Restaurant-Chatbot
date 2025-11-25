from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os

# QR Imports
from qr_code import generate_unique_qr, validate_qr_token


# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# FastAPI App
app = FastAPI()


# -------------------------------
# Chat Request Model
# -------------------------------
class ChatRequest(BaseModel):
    message: str


# -------------------------------
# QR Request Model
# -------------------------------
class QRRequest(BaseModel):
    offer_text: str


# -------------------------------
# Home Route
# -------------------------------
@app.get("/")
def home():
    return {"message": "Smart AI Restaurant Chatbot API is running!"}


# -------------------------------
# Chat Endpoint
# -------------------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    prompt = f"""
    You are a food recommendation AI assistant for MANILA only.

    RULES:
    - Only recommend restaurants located within Metro Manila.
    - Include name + area (Makati, BGC, Manila, Pasay, etc.)
    - You may suggest dishes widely available in Manila.
    - Never recommend locations outside Metro Manila.
    - Keep replies short, friendly, and helpful.

    User request: {req.message}
    """

    response = model.generate_content(prompt)
    answer = response.text

    return {"reply": answer}


# -------------------------------
# Generate Unique QR Endpoint
# -------------------------------
@app.post("/generate_unique_qr")
def create_qr(req: QRRequest):
    return generate_unique_qr(req.offer_text)


# -------------------------------
# Validate QR Token Endpoint
# -------------------------------
@app.get("/validate_qr")
def validate_qr(token: str):
    return validate_qr_token(token)
