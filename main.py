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
    You are a friendly AI Food Recommendation Assistant.
    User message: {req.message}
    Suggest foods based on user preference. Keep responses short.
    """

    response = model.generate_content(prompt)
    answer = response.text

    return {"reply": answer}
