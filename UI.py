import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ---------------------------
# Load .env & Configure Gemini
# ---------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------
# Streamlit Page Settings
# ---------------------------
st.set_page_config(page_title="Manila Food Chatbot", page_icon="🍽️")
st.title("🍽️ Manila Food Recommendation Chatbot")
st.write("Ask anything related to food or restaurants in **Metro Manila**.")

# ---------------------------
# Chat History
# ---------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Show chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# User Input
# ---------------------------
user_input = st.chat_input("Ask something about food or restaurants in Metro Manila...")

if user_input:
    # Add user message to session
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # ---------------------------
    # AI Prompt
    # ---------------------------
    prompt = f"""
    You are a friendly Manila Food Recommendation AI Assistant.

    RULES:
    - Only recommend restaurants within **Metro Manila** (Makati, BGC, Manila City, Pasay, Quezon City, Mandaluyong, Pasig, etc.)
    - Provide 2–4 suggestions per answer.
    - Include:
        • restaurant name  
        • location (city/area)  
        • 1 short highlight (why it’s good)
    - NEVER suggest restaurants outside Metro Manila.
    - Keep answer short and helpful.

    User message: {user_input}
    """

    # ---------------------------
    # AI Response
    # ---------------------------
    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = "⚠️ Sorry, something went wrong while generating the response."

    # Save assistant message
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(answer)
