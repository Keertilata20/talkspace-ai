import streamlit as st
import joblib
import random

# Load model
model = joblib.load("model/depression_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

st.set_page_config(page_title="Mental Health AI", page_icon="🧠")

st.title("🧠 Mental Health AI Assistant")

st.write(
"""
Talk about how you're feeling and the AI will listen and offer support.

⚠️ This tool is **not a medical diagnosis**.
"""
)

# Assistant personality selector
mode = st.sidebar.selectbox(
    "Assistant Style",
    ["Supportive Friend", "Calm Therapist"]
)

# Emotion keyword detection
emotion_keywords = {
    "loneliness": ["lonely","alone","nobody","isolated"],
    "sadness": ["sad","empty","hopeless","worthless"],
    "stress": ["tired","overwhelmed","exhausted","burnt"],
    "social_pain": ["friends","ignored","rejected","talk"]
}

def detect_emotion(text):
    text = text.lower()
    for emotion, words in emotion_keywords.items():
        for w in words:
            if w in text:
                return emotion
    return "general"

# Coping suggestions
def coping_suggestions():

    suggestions = [
        "Take 5 slow deep breaths and focus on the feeling of breathing.",
        "Step outside for a short walk or get some fresh air.",
        "Write down what you're feeling in a journal.",
        "Send a small message to someone you trust.",
        "Drink some water and take a short pause.",
        "Listen to a song that usually comforts you."
    ]

    chosen = random.sample(suggestions,3)

    return "\n".join([f"• {c}" for c in chosen])

# Response generator
def generate_response(prob, emotion, mode):

    suggestions = coping_suggestions()

    if mode == "Supportive Friend":

        if prob > 0.65:

            responses = [
                "I'm really glad you told me that. It sounds like you're going through a difficult time.",
                "That sounds really heavy. I'm glad you're sharing this instead of holding it inside.",
                "I'm here with you. What you're describing sounds really painful."
            ]

            return f"""
{random.choice(responses)}

Feeling this way can be exhausting. You're not weak for experiencing it.

🌿 A few small things that might help right now:

{suggestions}

You don't have to go through this alone ❤️

Would you like to tell me more about what's been happening lately?
"""

        elif prob > 0.40:

            responses = [
                "Thanks for sharing how you're feeling.",
                "I'm really glad you're talking about this.",
                "Sometimes saying these feelings out loud can help a little."
            ]

            return f"""
{random.choice(responses)}

It sounds like things might be weighing on you.

🌿 Something small that might help right now:

{suggestions}

Do these feelings happen often or did something happen recently?
"""

        else:

            responses = [
                "Thanks for sharing that with me.",
                "I'm glad you checked in with yourself emotionally.",
                "It's always good to pause and notice how you're feeling."
            ]

            return f"""
{random.choice(responses)}

If you'd like, you can tell me more about what's been on your mind lately.
"""

    else:  # Therapist mode

        if prob > 0.65:

            return f"""
Thank you for sharing that. It sounds like you're going through something very difficult.

Sometimes when emotional pain builds up, it can feel overwhelming and isolating.

🌿 You might consider trying one of these small grounding steps:

{suggestions}

If these feelings continue, it could also help to talk with a trusted person or a mental health professional.

Would you like to tell me when these feelings started?
"""

        elif prob > 0.40:

            return f"""
I appreciate you opening up about this.

It sounds like you're experiencing some emotional strain.

🌿 You might try one of these small self-care steps:

{suggestions}

Would you like to share more about what has been happening recently?
"""

        else:

            return """
Thank you for sharing how you're feeling.

Taking time to reflect on your emotions is an important step toward understanding yourself better.

If you'd like, you can tell me more about what's been on your mind.
"""

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
user_input = st.chat_input("Tell me how you're feeling...")

low_information_words = ["hi","hello","hey","ok","okay","yo"]

if user_input:

    st.chat_message("user").write(user_input)

    st.session_state.messages.append({
        "role":"user",
        "content":user_input
    })

    text = user_input.lower().strip()

    if len(text.split()) < 3 or text in low_information_words:

        response = """
Could you tell me a bit more about how you're feeling?

For example:
• "I feel really tired and unmotivated lately"
• "I feel lonely and disconnected from people"
"""

    else:
       question_words = [
    "what should i do",
    "what can i do",
    "any advice",
    "help me",
    "what now",
    "what do you suggest"
]

if any(q in text for q in question_words):

    if "last_emotion" in st.session_state:

        emotion = st.session_state.last_emotion
        prob = st.session_state.last_prob

        response = generate_response(prob, emotion, mode)

        st.chat_message("assistant").write(response)

        st.session_state.messages.append({
            "role":"assistant",
            "content":response
        })

        st.stop()

        # ML prediction
        vector = vectorizer.transform([user_input])
        prob = model.predict_proba(vector)[0][1]

        # Emotion detection
        emotion = detect_emotion(user_input)
        st.session_state.last_emotion = emotion
        st.session_state.last_prob = prob

        # Generate response
        response = generate_response(prob, emotion, mode)

    st.chat_message("assistant").write(response)

    st.session_state.messages.append({
        "role":"assistant",
        "content":response
    })