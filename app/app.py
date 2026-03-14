import streamlit as st
import joblib
import random

# Load ML model
model = joblib.load("model/depression_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

st.set_page_config(page_title="Mental Health AI", page_icon="🧠")

# UI Styling
st.markdown("""
<style>
.stChatMessage {
    padding: 12px;
    border-radius: 12px;
}
[data-testid="stChatInput"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Mental Health AI Assistant")

st.write(
"""
Talk about how you're feeling and the AI will listen and offer support.

⚠️ This tool is **not a medical diagnosis**.
"""
)

# Sidebar
mode = st.sidebar.selectbox(
    "Assistant Style",
    ["Supportive Friend", "Counselor"]
)

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# Emotion keywords
emotion_keywords = {
    "loneliness": ["lonely","alone","isolated","nobody"],
    "sadness": ["sad","hopeless","empty","worthless"],
    "stress": ["tired","exhausted","overwhelmed","burnt"],
    "social": ["ignored","rejected","friends","roommates"]
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
        "Take 5 slow deep breaths and focus only on breathing.",
        "Step outside for a short walk or fresh air.",
        "Write your thoughts in a journal for a few minutes.",
        "Send a small message to someone you trust.",
        "Listen to music that usually comforts you.",
        "Drink some water and take a short pause."
    ]

    chosen = random.sample(suggestions,3)

    return "\n".join([f"• {c}" for c in chosen])


# Friend responses
friend_reactions = [
    "Yeah, that sounds really frustrating.",
    "That must feel really heavy to deal with.",
    "I can understand why that would hurt.",
    "That sounds exhausting honestly.",
    "Anyone in that situation would feel upset."
]

friend_support = [
    "I'm really glad you shared that with me.",
    "Talking about it is actually a strong step.",
    "You don't have to carry this alone.",
    "Your feelings make sense.",
    "I'm here with you."
]


# Response generator
def generate_response(prob, emotion, mode):

    suggestions = coping_suggestions()

    if mode == "Supportive Friend":

        reaction = random.choice(friend_reactions)
        support = random.choice(friend_support)

        if prob > 0.65:

            return f"""
{reaction}

{support}

Feeling this way for a long time can be really exhausting.

🌿 Something that might help a little right now:

{suggestions}

You don't have to go through this alone.
"""

        elif prob > 0.40:

            return f"""
{reaction}

{support}

Sometimes even small things can help shift the feeling a little.

🌿 Maybe try one of these:

{suggestions}
"""

        else:

            light_lines = [
                "I'm glad you shared that.",
                "It's good that you're talking about how you feel.",
                "Sometimes just saying things out loud can help.",
                "I'm here to listen.",
                "Thanks for trusting me with that.",
                "It's okay to take things slowly."
            ]

            return f"""
{random.choice(light_lines)}

If you'd like, you can tell me more about what's been on your mind.
"""


    else:  # Counselor mode

        if prob > 0.65:

            return f"""
Thank you for sharing that.

It sounds like you're carrying something very heavy right now.

Sometimes when emotional pain builds up it can start to feel overwhelming.

🌿 You might try one small grounding step:

{suggestions}

If you'd like, you can tell me more about when these feelings started.
"""

        elif prob > 0.40:

            return f"""
I appreciate you opening up about this.

It sounds like you're experiencing some emotional strain.

🌿 One small step that sometimes helps:

{suggestions}

Would you like to share more about what's been happening recently?
"""

        else:

            return """
Thank you for reflecting on how you're feeling.

Taking time to notice emotions is an important step toward understanding yourself.

If you'd like, you can tell me more about what's been on your mind.
"""


# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []


# Welcome message
if len(st.session_state.messages) == 0:
    st.info("""
You can talk about anything that's on your mind.

Examples:
• "I feel really lonely lately"
• "I'm overwhelmed with work"
• "I feel like nobody understands me"

This space is here for you.
""")


# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# User input
user_input = st.chat_input("Tell me how you're feeling...")


low_information_words = ["hi","hello","hey","ok","okay","yo"]

question_words = [
    "what should i do",
    "what can i do",
    "any advice",
    "help me",
    "what now",
    "what do you suggest"
]

closing_words = [
    "no thanks",
    "no thank you",
    "im good",
    "i'm good",
    "not now",
    "later maybe",
    "thats enough",
    "that's enough",
    "im done",
    "i'm done",
    "done for now",
    "its okay for now",
    "it's okay for now",
    "nah its okay",
    "nah it's okay",
    "thats fine",
    "that's fine",
    "bye",
"goodbye",
"see you",
"thanks",
"thank you",
"talk later"

]


if user_input:

    st.chat_message("user").write(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    text = user_input.lower().strip()

    # Detect conversation closing FIRST
    if any(c in text for c in closing_words):
        response = random.choice([
        "That's completely okay. I'm here whenever you feel like talking again.",
        "No worries at all. Take care of yourself.",
        "That's alright. I'm here anytime you want to talk.",
        "Totally okay. Take it easy today."])
    # Then check short messages
    elif len(text.split()) < 3 or text in low_information_words:
        response = """Could you tell me a bit more about how you're feeling?

Example:
• "I feel really tired and unmotivated lately"
• "I feel lonely and disconnected from people"
"""

    elif any(c in text for c in closing_words) or "done" in text:

        response = random.choice([
            "That's completely okay. I'm here whenever you feel like talking again.",
            "No worries at all. Take care of yourself.",
            "That's alright. I'm here anytime you want to talk.",
            "Totally okay. Take it easy today."
        ])

    elif any(q in text for q in question_words):

        if "last_emotion" in st.session_state:

            emotion = st.session_state.last_emotion
            prob = st.session_state.last_prob

            response = generate_response(prob, emotion, mode)

        else:
            response = "Could you tell me a bit more about what's been going on?"

    else:

        vector = vectorizer.transform([user_input])
        prob = model.predict_proba(vector)[0][1]

        emotion = detect_emotion(user_input)

        st.session_state.last_emotion = emotion
        st.session_state.last_prob = prob

        response = generate_response(prob, emotion, mode)

    st.chat_message("assistant").write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })