import streamlit as st
import joblib
import random
import time
import pandas as pd
import requests

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
            
            [data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 10px;
    background-color: rgba(255,255,255,0.6);
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
# EMOTION KEYWORDS
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
# COPING SUGGESTIONS
# -----------------------------

def coping_suggestions():

    suggestions = [

    "Take 5 slow deep breaths and focus on breathing.",
    "Step outside for a short walk or fresh air.",
    "Write what you're feeling in a journal.",
    "Send a small message to someone you trust.",
    "Listen to a song that comforts you.",
    "Drink some water and pause for a moment."

    ]

    return "\n".join([f"• {s}" for s in random.sample(suggestions,3)])

# -----------------------------
# RESPONSE POOLS
# -----------------------------

validation_pool = [

"That sounds really difficult.",
"I can understand why that would hurt.",
"That must feel exhausting.",
"Anyone in that situation would struggle.",
"That sounds really frustrating."

]

support_pool = [

"I'm here with you.",
"You don't have to carry this alone.",
"Your feelings make sense.",
"I'm really glad you shared that.",
"Talking about this is a strong step."

]

curiosity_pool = [

"How long have you been feeling this way?",
"What part of this affects you the most?",
"Did something happen recently?",
"What usually goes through your mind when this happens?",
"Would you like to tell me more about it?"

]

# -----------------------------
# RESPONSE GENERATOR
# -----------------------------

def generate_ai_response(user_input, emotion, history):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": "Bearer YOUR_OPENROUTER_API_KEY",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": f"""
You are Nira, a warm, kind, emotionally supportive companion.

You speak like a real human friend texting.
You are gentle, natural, and never robotic.

Rules:
- Always validate feelings first
- Keep responses conversational
- Avoid repetition
- Be calm and supportive
- Keep responses 2–5 sentences
- Give advices only when it is asked
- Current detected emotion: {emotion}
"""
        }
    ]

    for msg in history[-6:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": user_input
    })

    data = {
        "model": "openrouter/free",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()['choices'][0]['message']['content']




# -----------------------------
# EMOTIONAL WEATHER
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
# MOOD JOURNEY
# -----------------------------

st.sidebar.markdown("### 📈 Mood Journey")

if st.session_state.emotion_history:

    mood_map = {
        "loneliness":2,
        "sadness":2,
        "stress":3,
        "anxiety":3,
        "social":3,
        "selfworth":2,
        "general":4
    }

    values = [mood_map.get(e,3) for e in st.session_state.emotion_history]

    df = pd.DataFrame(values, columns=["Mood"])

    st.sidebar.line_chart(df)


# -----------------------------
# CALM TOOLS
# -----------------------------

st.sidebar.markdown("### 🫁 Calm Tools")

if st.sidebar.button("Guided Breathing"):

    st.sidebar.write("Follow the breathing guide:")

    for i in range(3):

        st.sidebar.write("Breathe in...")
        time.sleep(3)

        st.sidebar.write("Hold...")
        time.sleep(3)

        st.sidebar.write("Breathe out...")
        time.sleep(4)

# -----------------------------
# WELCOME PANEL
# -----------------------------

if len(st.session_state.messages) == 0:

    st.info("""
You can talk about anything here.

Some people talk about:
• how their day went
• something they've been thinking about
• things that feel difficult
• or simply how they're feeling

There's no pressure here.  
Just talk.
""")

    c1,c2,c3,c4 = st.columns(4)

    if c1.button("😔 Feeling lonely"):
        st.session_state.messages.append({"role":"user","content":"I've been feeling lonely lately."})

    if c2.button("😓 Feeling stressed"):
        st.session_state.messages.append({"role":"user","content":"I've been feeling stressed lately."})

    if c3.button("🤔 Overthinking"):
        st.session_state.messages.append({"role":"user","content":"I've been overthinking a lot recently."})

    if c4.button("💭 Just want to talk"):
        st.session_state.messages.append({"role":"user","content":"I just wanted someone to talk to."})

# -----------------------------
# DISPLAY CHAT
# -----------------------------

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------

user_input = st.chat_input("Share what's on your mind...")

greetings = ["hi","hello","hey","yo"]
closings = ["bye","thanks","thank you","im done","i'm done","bye for now","bye bye", "later","thank you for now","i should leave"]

if user_input:

    st.chat_message("user").write(user_input)

    st.session_state.messages.append({
        "role":"user",
        "content":user_input
    })

    text = user_input.lower().strip()

    # CRISIS RESPONSE
    if any(word in text for word in crisis_words):

        response = """
I'm really sorry that you're feeling this much pain.

You don't have to go through this alone.

If you can, consider reaching out to someone you trust or a trained counselor.

Talking to a real person right now could really help.
"""

    # GREETING
    elif text in greetings:

        response = random.choice([
        "Hey. I'm here. How are you feeling today?",
        "Hi there. What's been on your mind lately?",
        "Hello. What would you like to talk about today?",
        "Hey. I'm listening."
        ])

    # CLOSING
    elif any(c in text for c in closings):

        response = random.choice([
        "Take care of yourself today. You're always welcome here.",
        "I'm glad you shared a little of your thoughts. Be kind to yourself.",
        "No worries at all. I'm here whenever you want to come back."
        ])

    else:

        vector = vectorizer.transform([user_input])
        prob = model.predict_proba(vector)[0][1]

        emotion = detect_emotion(user_input)

        st.session_state.topic_memory.append(emotion)
        st.session_state.emotion_history.append(emotion)

        try:
            response = generate_ai_response(
        user_input,
        emotion,
        st.session_state.messages
        )
        except:
            response = "I'm here with you. Want to tell me a bit more?"
    
    
    # THINKING ANIMATION

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🌿 Nira is typing...")
        time.sleep(1)
        
        typed = ""
        for char in response:
            typed += char
            placeholder.markdown(typed)
            
            if char in ".!?":
                time.sleep(0.2)
            else:
                time.sleep(0.01)
    st.session_state.messages.append({
        "role":"assistant",
        "content":response
    })