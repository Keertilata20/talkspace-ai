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

def detect_stage(text):
    text = text.lower()

    if any(x in text for x in ["i dont need", "leave me", "stop", "no thanks"]):
        return "resistant"

    elif any(x in text for x in ["what should i do", "help me", "any advice"]):
        return "seeking_help"

    else:
        return "venting"

# -----------------------------
# AI RESPONSE
# -----------------------------

def generate_ai_response(user_input, emotion, mode, stage):

    st.session_state.chat_history.append(user_input)
    recent_memory = " ".join(st.session_state.chat_history[-3:])

    system_prompt = f"""
You are Nira, a deeply empathetic human-like companion.

Your ONLY goal is to make the user feel understood.

STRICT RULES (never break these):
- NEVER give suggestions unless user explicitly asks for help
- NEVER use phrases like:
  "I'm here with you"
  "Your feelings make sense"
  "I'm glad you shared that"
- NEVER ask generic questions repeatedly
- NEVER respond positively to negative expressions (e.g., if user says "I hate you", do NOT thank them)

BEHAVIOR:
- Respond like a real person in a conversation, not a therapist
- Reflect the exact feeling behind the words
- Use the user’s language (e.g., "alone", "ignored", "invisible")
- Sometimes just respond without asking anything
- Keep responses natural and varied

IMPORTANT:
If user rejects help (e.g., "I don't need suggestions"):
→ Respect it and STOP giving suggestions

If user shows anger:
→ Acknowledge it, don’t soften it unnaturally

User stage: {stage}

BEHAVIOR:
- If stage = venting → just reflect, no advice
- If stage = resistant → no suggestions, no pushing
- If stage = seeking_help → gentle suggestions allowed

Respond like a real human:
- Use user's words
- Be natural
- Sometimes don't ask questions

Tone:
- Calm, real, grounded
- Not repetitive
- Not overly structured

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
    

def clean_response(response):

    banned_phrases = [
        "i'm here with you",
        "your feelings make sense",
        "i'm glad you shared that",
        "how long have you been feeling",
        "what part of this affects",
        "would you like to tell me more"
    ]

    for phrase in banned_phrases:
        response = response.replace(phrase, "")

    return response.strip()

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
    stage = detect_stage(user_input)

    # CRISIS
    if any(word in text for word in crisis_words):

        response = """
I'm really sorry you're feeling this way… it sounds really heavy.

You don’t have to go through this alone, even if it feels like it right now.

If you can, reaching out to someone you trust might help — even just to not sit with this by yourself.

If you're in immediate danger, please contact a local helpline or emergency service.

You can stay here and talk to me. I'm listening.
"""
    # 🔥 HANDLE ANGER
    elif "hate you" in text:
        response = "That sounds like a lot of frustration coming out."
    # 🔥 HANDLE RESISTANCE
    elif "dont want" in text or "no suggestions" in text:
        response = "Okay… we don’t have to fix anything right now."

    else:
        emotion = detect_emotion(user_input)
        st.session_state.topic_memory.append(emotion)
        st.session_state.emotion_history.append(emotion)

        response = generate_ai_response(user_input, emotion, mode, stage)
        response = clean_response(response)

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