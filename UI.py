import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import tempfile


# ---------------------------
# Load .env & Configure Gemini
# ---------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# Streamlit Page Settings
# ---------------------------
st.set_page_config(page_title="Manila Food Chatbot", page_icon="🍽️")
st.title("🍽️ Manila Food Recommendation Chatbot")
st.write("Ask anything related to food or restaurants in **Metro Manila**.")

# ---------------------------
# Chat History
# Streamlit Page Setup
# ---------------------------
st.set_page_config(page_title="Manila Food Chatbot", page_icon="🍽️")
st.title("🍽️ Manila Food Recommendation Chatbot")
st.write("Chat with the AI and get restaurant and food suggestions in Metro Manila.")

# ---------------------------
# Initialize Chat History
# ---------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # list of {role, content}


# ---------------------------
# File Upload (Optional)
# ---------------------------
uploaded_file = st.file_uploader(
    "Optional: Upload a menu / food photo / receipt (image or PDF)",
    type=["jpg", "jpeg", "png", "pdf"],
    help="Attach a file to give the AI more context, like a menu or bill."
)


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
    # 1) Add user message to history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # User bubble
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2) Build conversation history text for the prompt
    history_text = ""
    for m in st.session_state["messages"]:
        role = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{role}: {m['content']}\n"

    base_prompt = f"""
    You are a food recommendation AI assistant for Manila only.

    RULES:
    - Only recommend restaurants located within Metro Manila.
    - Always include restaurant name + area (e.g., Makati, BGC, Manila City, Pasay, etc.)
    - You may suggest dishes commonly available in Manila.
    - Never recommend places outside Metro Manila.
    - Keep messages short, friendly, and helpful.

    Conversation so far:
    {history_text}

    New user message: {user_input}
    """

    response = model.generate_content(prompt)
    answer = response.text

    # Append assistant message
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    # Show assistant bubble

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 3) If file is uploaded, use it as extra context
            try:
                if uploaded_file is not None:
                    # Save to temporary file for Gemini upload
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    try:
                        gemini_file = genai.upload_file(
                            path=tmp_path,
                            mime_type=uploaded_file.type
                        )
                        # File + prompt together
                        response = model.generate_content([gemini_file, base_prompt])
                    finally:
                        # Clean up temp file
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                else:
                    # Text-only chat
                    response = model.generate_content(base_prompt)

                answer = response.text

            except Exception as e:
                answer = f"Sorry, something went wrong while processing your request: `{e}`"

            # 4) Save assistant reply to history
            st.session_state["messages"].append(
                {"role": "assistant", "content": answer}
            )

            # Show answer
            st.markdown(answer)
