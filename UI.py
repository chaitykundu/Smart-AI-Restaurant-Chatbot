import streamlit as st
import openai
from dotenv import load_dotenv
import os
import tempfile

# ---------------------------
# Load .env & Configure OpenAI
# ---------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY

# ---------------------------
# Streamlit Page Settings
# ---------------------------
st.set_page_config(page_title="Manila Food Chatbot", page_icon="🍽️")
st.title("🍽️ Manila Food Recommendation Chatbot")
st.write("Ask anything related to food or restaurants in **Metro Manila**.")

# ---------------------------
# Initialize Chat History
# ---------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # list of dicts: {role, content}

# ---------------------------
# File Upload (Optional)
# ---------------------------
uploaded_file = st.file_uploader(
    "Optional: Upload a menu / food photo / receipt (image or PDF)",
    type=["jpg", "jpeg", "png", "pdf"],
    help="Attach a file to give the AI more context, like a menu or bill."
)

# ---------------------------
# Show chat history
# ---------------------------
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# User Input
# ---------------------------
user_input = st.chat_input("Ask something about Manila food...")

if user_input:
    # Add user message to session
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # ---------------------------
    # Build conversation history for prompt
    # ---------------------------
    history_text = ""
    for m in st.session_state["messages"]:
        role = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{role}: {m['content']}\n"

    base_prompt = f"""
You are a friendly Manila Food Recommendation AI Assistant.

RULES:
- Only recommend restaurants located within Metro Manila (Makati, BGC, Manila City, Pasay, Quezon City, Mandaluyong, Pasig, etc.).
- Provide 2–4 suggestions per answer.
- Include restaurant name, location (city/area), and 1 short highlight.
- Keep answers short, helpful, and friendly.
- Never suggest restaurants outside Metro Manila.

Conversation so far:
{history_text}

New user message: {user_input}
"""

    # ---------------------------
    # Generate AI Response using OpenAI >=1.0.0
    # ---------------------------
    try:
        # If file uploaded, mention it in the prompt
        if uploaded_file is not None:
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            base_prompt += f"\n\nThe user also uploaded a file: {uploaded_file.name} (content not directly readable)."
            os.remove(tmp_path)  # clean up

        # New API call
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": base_prompt}],
            temperature=0.7,
            max_tokens=500
        )

        # Extract the assistant reply
        answer = response.choices[0].message.content

    except Exception as e:
        answer = f"⚠️ Sorry, something went wrong while generating the response: {e}"

    # ---------------------------
    # Save assistant message
    # ---------------------------
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    # Show assistant bubble
    with st.chat_message("assistant"):
        st.markdown(answer)