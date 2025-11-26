# Smart-AI-Restaurant-Chatbot

# Manila Food Recommendation AI Chatbot

This project is a simple AI-powered **Food Recommendation Chatbot** focused exclusively on **Manila restaurants**, built using:

* **FastAPI** (Backend)
* **Gemini 2.5 Flash** (LLM)
* **python-dotenv** (Environment variables)
* **JavaScript/HTML** (Frontend with suggestion board)

The chatbot behaves similarly to ChatGPT but provides **restaurant suggestions only within Manila**.

---

## 🚀 Features

### 🔥 AI Food Recommendations

The chatbot uses **Gemini 2.5 Flash** to generate human-like suggestions based on user queries like:

* "Recommend spicy ramen in Manila"
* "Suggest Filipino comfort food"
* "Show me budget-friendly restaurants"

### 📍 Manila‑Only Output

AI is restricted to recommending restaurants **strictly inside Metro Manila**, including:

* Makati
* BGC / Taguig
* Manila City
* Pasay
* Mandaluyong
* Quezon City

### 💬 ChatGPT‑Style Interaction

Users can type messages normally, and the chatbot responds in a conversational tone.

### 🧠 Optional Restaurant Filtering (Hybrid Mode)

A local restaurant database can be added to reduce hallucinations and ensure credible recommendations.

### 🎛️ Suggestion Board UI (Quick Reply Chips)

Frontend includes suggestion buttons like ChatGPT:

* Spicy ramen
* Filipino comfort food
* Budget-friendly places
* Top Korean BBQ

These help users quickly choose topics without typing.

---

## 📂 Project Structure

```
project/
│-- main.py
│-- .env
│-- requirements.txt
│-- static/
│     └── index.html (Frontend UI)
```

---

## 📦 Installation

### 1. Clone the project

```
git clone <your-repo-url>
cd project
```

### 2. Create virtual environment (Python 3.10 recommended)

```
python -m venv venv
```

### 3. Activate environment

**Windows CMD:**

```
venv\Scripts\activate
```

**Windows PowerShell:**

```
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

Make sure you have a valid Gemini API key from Google AI Studio.

---

## 🧠 Backend: FastAPI + Gemini (main.py)

The backend exposes a `/chat` endpoint that accepts user messages and returns AI‑generated responses tailored to Manila restaurants.

Key logic ensures:

* Manila‑only recommendations
* Short, friendly responses
* Optional restaurant filtering

Run the server:

```
uvicorn main:app --reload
```

Backend runs on:

```
http://127.0.0.1:8000/chat
```

---

## 🖥️ Frontend: Suggestion Board + Chat UI

A lightweight HTML + JavaScript interface is provided which includes:

* Input box
* Send button
* Chat log
* Suggestion chips (like ChatGPT)

Clicking a chip automatically sends the text to the chatbot.

---

## 🧪 Example Queries

* "Recommend spicy ramen in Manila."
* "Show me Filipino comfort food places in BGC."
* "What are budget-friendly restaurants in Makati?"
* "Top Korean BBQ places in Manila City."

---

## 🚧 Future Improvements

* Add real Manila restaurant database (JSON)
* Add cuisine, price, rating filters
* Add real-time search by location
* Add session memory for longer conversations
* Deploy using Docker or Render

---

## 🤝 Contributing

Feel free to submit issues or enhancements. PRs are welcome!

---

## 👨‍💻 Author

Developed as part of a Manila-focused AI assistant project using Gemini 2.5 Flash.
