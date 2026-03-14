import streamlit as st
import joblib
import random
import time

# Load ML model
model = joblib.load("model/depression_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

st.set_page_config(
    page_title="TalkSpace AI",
    page_icon="🌿",
    layout="wide"
)

# -------------------------
# UI STYLE
# -------------------------

st.markdown("""
<style>

body {
background-color:#FAF7F2;
}

.stChatMessage {
padding:14px;
border-radius:14px;
}

[data-testid="stChatInput"] {
border-radius:20px;
}

.block-container {
padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------

st.markdown("""
# 🌿 TalkSpace AI
*A quiet place for your thoughts.*

Share what's on your mind.  
I'm here to listen.
""")

# -------------------------
# SIDEBAR
# -------------------------

mode = st.sidebar.selectbox(
"Conversation Style",
["Supportive Friend","Counselor"]
)

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.session_state.topic_memory = []
    st.rerun()

# -------------------------
# EMOTION KEYWORDS
# -------------------------

emotion_keywords = {
"loneliness":["lonely","alone","isolated","nobody"],
"sadness":["sad","hopeless","empty","worthless"],
"stress":["tired","exhausted","overwhelmed","burnt"],
"social":["ignored","rejected","friends","roommates"]
}

def detect_emotion(text):
    text = text.lower()
    for emotion,words in emotion_keywords.items():
        for w in words:
            if w in text:
                return emotion
    return "general"

# -------------------------
# COPING SUGGESTIONS
# -------------------------

def coping_suggestions():

    suggestions = [
    "Take 5 slow deep breaths and focus on breathing.",
    "Step outside for a short walk or fresh air.",
    "Write what you're feeling in a journal.",
    "Send a small message to someone you trust.",
    "Listen to a song that comforts you.",
    "Drink some water and pause for a moment."
    ]

    chosen = random.sample(suggestions,3)

    return "\n".join([f"• {c}" for c in chosen])

# -------------------------
# EMPATHY POOLS
# -------------------------

emotion_empathy = {

"loneliness":[
"Feeling alone for a long time can be really heavy.",
"Humans naturally need connection. Feeling lonely can hurt deeply."
],

"stress":[
"It sounds like things have been draining your energy lately.",
"That kind of exhaustion can slowly build up."
],

"sadness":[
"That kind of feeling can weigh on someone quietly.",
"It's understandable that this would affect you."
],

"social":[
"Being around people who make you feel small can be exhausting.",
"Difficult social environments can affect us more than we realize."
],

"general":[
"Thanks for sharing that.",
"I'm really glad you felt comfortable saying that."
]

}

friend_support = [
"I'm here with you.",
"You don't have to carry this alone.",
"Your feelings make sense.",
"Talking about it is a strong step."
]

# -------------------------
# RESPONSE GENERATOR
# -------------------------

def generate_response(prob,emotion,mode):

    empathy = random.choice(emotion_empathy.get(emotion,emotion_empathy["general"]))
    support = random.choice(friend_support)
    suggestions = coping_suggestions()

    if mode == "Supportive Friend":

        if prob > 0.65:

            return f"""
{empathy}

{support}

Feeling this way for a long time can be exhausting.

🌿 Something that might help a little right now:

{suggestions}

You're not alone in this.
"""

        elif prob > 0.40:

            return f"""
{empathy}

{support}

Sometimes even small things can help shift the feeling.

🌿 Maybe try one of these:

{suggestions}
"""

        else:

            return f"""
{support}

If you'd like, you can tell me more about what's been on your mind.
"""

    else:

        if prob > 0.65:

            return f"""
Thank you for sharing that.

{empathy}

Sometimes when emotions build up they can feel overwhelming.

🌿 One grounding step you might try:

{suggestions}

If you'd like, you can tell me more about what's been happening.
"""

        elif prob > 0.40:

            return f"""
I appreciate you opening up.

{empathy}

🌿 One small step that sometimes helps:

{suggestions}
"""

        else:

            return """
Thank you for reflecting on how you're feeling.

If you'd like, you can share more about what's on your mind.
"""

# -------------------------
# SESSION STATE
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "topic_memory" not in st.session_state:
    st.session_state.topic_memory = []

# -------------------------
# REFLECTION PANEL
# -------------------------

with st.sidebar.expander("Conversation Signals"):

    if st.session_state.topic_memory:

        for topic in set(st.session_state.topic_memory):
            st.write("•",topic)

    else:
        st.write("No strong signals yet")

# -------------------------
# WELCOME BOX
# -------------------------

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

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("😔 Feeling lonely"):
        st.session_state.messages.append({"role":"user","content":"I've been feeling lonely lately."})

    if col2.button("😓 Feeling stressed"):
        st.session_state.messages.append({"role":"user","content":"I've been feeling stressed lately."})

    if col3.button("🤔 Overthinking"):
        st.session_state.messages.append({"role":"user","content":"I've been overthinking a lot recently."})

    if col4.button("💭 Just want to talk"):
        st.session_state.messages.append({"role":"user","content":"I just needed someone to talk to."})

# -------------------------
# DISPLAY CHAT
# -------------------------

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# -------------------------
# USER INPUT
# -------------------------

user_input = st.chat_input("Share what's on your mind...")

greeting_words = ["hi","hello","hey","yo"]
closing_words = ["bye","thanks","thank you","im done","i'm done","bye for now"]

if user_input:

    st.chat_message("user").write(user_input)

    st.session_state.messages.append({
    "role":"user",
    "content":user_input
    })

    text = user_input.lower().strip()

    # Greeting
    if text in greeting_words:

        response = random.choice([
        "Hey. I'm here. How are you feeling today?",
        "Hi there. What's been on your mind lately?",
        "Hello. What would you like to talk about today?",
        "Hey. I'm listening."
        ])

    # Closing
    elif any(c in text for c in closing_words):

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

        response = generate_response(prob,emotion,mode)

    # Thinking animation
    with st.chat_message("assistant"):

        placeholder = st.empty()
        placeholder.markdown("● ● ● thinking")
        time.sleep(1)

        typed = ""

        for char in response:
            typed += char
            placeholder.markdown(typed)
            time.sleep(0.01)

    st.session_state.messages.append({
    "role":"assistant",
    "content":response
    })