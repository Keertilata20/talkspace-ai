import streamlit as st
import joblib
import random
import time
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="TalkSpace",
    page_icon="🌿",
    layout="wide"
)

# -----------------------------
# LOAD MODEL
# -----------------------------

model = joblib.load("model/depression_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

# -----------------------------
# UI STYLE
# -----------------------------

st.markdown("""
<style>
body {
background: linear-gradient(135deg,#F6F8F7,#EAF3EE);
}
[data-testid="stSidebar"] {
background-color:#F1F5F3;
}
.block-container {
padding-top:2rem;
max-width:900px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------

st.markdown("""
# 🌿 TalkSpace
Your companion **🌿 Nira** is here to listen.
*A quiet place for your thoughts.*
""")

# -----------------------------
# SIDEBAR
# -----------------------------

mode = st.sidebar.selectbox(
"Conversation Style",
["Supportive Friend","Counselor"]
)

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.session_state.topic_memory = []
    st.session_state.emotion_history = []
    st.rerun()

# -----------------------------
# DAILY AFFIRMATION
# -----------------------------

affirmations = [
"You deserve patience today.",
"Small steps still matter.",
"It's okay to take things slowly.",
"Your feelings are valid.",
"You are stronger than you think."
]

st.sidebar.markdown("### 🌱 Small Reminder")
st.sidebar.write(random.choice(affirmations))

# -----------------------------
# SESSION STATE
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "topic_memory" not in st.session_state:
    st.session_state.topic_memory = []

if "emotion_history" not in st.session_state:
    st.session_state.emotion_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# CRISIS DETECTION
# -----------------------------

crisis_words = [
"i want to die",
"kill myself",
"suicide",
"end my life",
"i can't live anymore",
"i can't do it anymore",
"i hate myself",
"i dont want to live",
"life is pointless"
]

# -----------------------------
# EMOTION DETECTION
# -----------------------------

emotion_keywords = {
"loneliness":["lonely","alone","isolated","nobody"],
"sadness":["sad","hopeless","empty","worthless","down"],
"stress":["tired","exhausted","overwhelmed","burnt","pressure"],
"anxiety":["anxious","panic","nervous","overthinking"],
"social":["ignored","rejected","friends","roommates","people"],
"selfworth":["inferior","failure","useless","comparison"]
}

def detect_emotion(text):
    text = text.lower()
    for emotion,words in emotion_keywords.items():
        for w in words:
            if w in text:
                return emotion
    return "general"

# -----------------------------
# AI RESPONSE
# -----------------------------

def generate_ai_response(user_input, emotion, mode):

    st.session_state.chat_history.append(user_input)
    recent_memory = " ".join(st.session_state.chat_history[-3:])

    system_prompt = f"""
You are Nira, a deeply empathetic and emotionally intelligent companion.

Your purpose is to make the user feel truly understood and less alone.

IMPORTANT RULES:
- Do NOT use generic phrases like "your feelings make sense", "I'm here with you", or "would you like to tell me more"
- Do NOT ask the same type of question repeatedly
- Do NOT follow a fixed pattern
- Do NOT jump into advice unless user asks
- Avoid repeating sentence structures
- Only give suggestions if explicitly asked

HOW TO RESPOND:
- Reflect the user's feelings in a specific way
- Use their words (like invisible, alone, etc.)
- Sometimes do NOT ask a question
- Sound human, not robotic

TONE:
- Warm, calm, personal
- Not too long

Conversation style: {mode}
Emotion: {emotion}
Recent thoughts: {recent_memory}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.65
        )
        return response.choices[0].message.content

    except:
        return "I'm here with you… something went wrong on my side, but you can keep talking 💙"

# -----------------------------
# SIDEBAR INFO
# -----------------------------

st.sidebar.markdown("### 🌤 Emotional Weather")

if st.session_state.emotion_history:
    current_emotion = st.session_state.emotion_history[-1]
    emotion_labels = {
        "loneliness":"Feeling Lonely",
        "sadness":"Feeling Low",
        "stress":"Feeling Stressed",
        "anxiety":"Feeling Anxious",
        "social":"Social Pressure",
        "selfworth":"Self Doubt",
        "general":"Neutral"
    }
    st.sidebar.write(emotion_labels.get(current_emotion))
else:
    st.sidebar.write("No signals yet")

# -----------------------------
# CHAT UI
# -----------------------------

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Share what's on your mind...")

if user_input:

    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role":"user","content":user_input})

    text = user_input.lower().strip()

    # CRISIS
    if any(word in text for word in crisis_words):

        response = """
I'm really sorry you're feeling this way… it sounds really heavy.

You don’t have to go through this alone, even if it feels like it right now.

If you can, reaching out to someone you trust might help — even just to not sit with this by yourself.

If you're in immediate danger, please contact a local helpline or emergency service.

You can stay here and talk to me. I'm listening.
"""

    else:
        emotion = detect_emotion(user_input)
        st.session_state.topic_memory.append(emotion)
        st.session_state.emotion_history.append(emotion)

        response = generate_ai_response(user_input, emotion, mode)

    # typing effect
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🌿 Nira is thinking...")
        time.sleep(0.5)

        typed = ""
        for char in response:
            typed += char
            placeholder.markdown(typed)
            time.sleep(0.01)

    st.session_state.messages.append({"role":"assistant","content":response})