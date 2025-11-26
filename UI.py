import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

<<<<<<< HEAD
# ---------------------------
# Load .env & Configure Gemini
# ---------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

=======
# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
>>>>>>> 73227df581c5d6fff1eaaaa50cb7a0ee5613b151
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------
<<<<<<< HEAD
# Streamlit Page Settings
# ---------------------------
st.set_page_config(page_title="Manila Food Chatbot", page_icon="🍽️")
st.title("🍽️ Manila Food Recommendation Chatbot")
st.write("Ask anything related to food or restaurants in **Metro Manila**.")

# ---------------------------
# Chat History
=======
# Streamlit Page Setup
# ---------------------------
st.set_page_config(page_title="Manila Food Chatbot", page_icon="🍽️")
st.title("🍽️ Manila Food Recommendation Chatbot")
st.write("Chat with the AI and get restaurant and food suggestions in Metro Manila.")

# ---------------------------
# Initialize Chat History
>>>>>>> 73227df581c5d6fff1eaaaa50cb7a0ee5613b151
# ---------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

<<<<<<< HEAD
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

=======
# ---------------------------
# Chat History Display
# ---------------------------
for msg in st.session_state["messages"]:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)

    else:
        with st.chat_message("assistant"):
            st.markdown(content)

# ---------------------------
# Chat Input Box
# ---------------------------
user_input = st.chat_input("Ask something about Manila food...")

if user_input:
    # Append user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Show user bubble
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build AI prompt using same rules you provided
    prompt = f"""
    You are a food recommendation AI assistant for **Manila** only.

    RULES:
    - Only recommend restaurants located within Metro Manila.
    - Always include restaurant name + area (Makati, BGC, Manila City, Pasay, etc.)
    - You may also suggest dishes commonly available in Manila.
    - Never recommend places outside Metro Manila.
    - Keep messages short, friendly, and helpful.

    User request: {user_input}
    """

    response = model.generate_content(prompt)
    answer = response.text

    # Append assistant message
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    # Show assistant bubble
>>>>>>> 73227df581c5d6fff1eaaaa50cb7a0ee5613b151
    with st.chat_message("assistant"):
        st.markdown(answer)
