import streamlit as st
import joblib
import random

# load model
model = joblib.load("model/depression_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

st.set_page_config(page_title="Mental Health AI", page_icon="🧠")

st.title("🧠 Mental Health AI Assistant")

st.write(
"""
Talk about how you're feeling and the AI will analyze emotional signals.

⚠️ This tool is **not a medical diagnosis**.
"""
)

# supportive response generator
def generate_response(prob, words):

    if prob > 0.75:
        responses = [
            "I'm really glad you shared that. It sounds like you're going through a very heavy time.",
            "Thank you for opening up. What you're describing sounds really difficult.",
            "It seems like things might feel overwhelming right now."
        ]

        advice = [
            "You might consider talking to someone you trust or a mental health professional.",
            "You deserve support. Reaching out to a friend, family member, or counselor could help.",
            "Remember that difficult moments don't define your whole story."
        ]

        return f"""
⚠️ **Strong emotional distress signals detected**

{random.choice(responses)}

Confidence: {prob*100:.2f}%

Key emotional indicators:
{words}

{random.choice(advice)}

You are not alone ❤️
"""

    elif prob > 0.40:

        responses = [
            "I notice some emotional stress in what you're sharing.",
            "It sounds like you might be dealing with some difficult feelings.",
            "Thanks for being open about how you're feeling."
        ]

        advice = [
            "Taking a short walk, journaling, or talking to someone supportive might help.",
            "Sometimes sharing feelings with someone close can make things lighter.",
            "Try to take things one step at a time."
        ]

        return f"""
💬 **Some emotional distress signals detected**

{random.choice(responses)}

Confidence: {prob*100:.2f}%

Key emotional indicators:
{words}

{random.choice(advice)}
"""

    else:

        responses = [
            "Thanks for sharing how you're feeling.",
            "I'm glad you took a moment to reflect on your emotions.",
            "It's good to check in with yourself emotionally."
        ]

        return f"""
✅ **No strong depression signals detected**

{random.choice(responses)}

Confidence: {prob*100:.2f}%

Key emotional indicators:
{words}

Your feelings still matter. Take care of yourself.
"""


# store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# show previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# chat input
user_input = st.chat_input("Tell me how you're feeling...")

low_information_words = ["hi","hello","hey","ok","okay","lol","yo"]

if user_input:

    st.chat_message("user").write(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    text = user_input.lower().strip()

    if len(text.split()) < 3 or text in low_information_words:

        response = """
Could you tell me a bit more about how you're feeling?

Example:
• "I feel tired and unmotivated lately"
• "I feel lonely and disconnected from people"
"""

    else:

        vector = vectorizer.transform([user_input])
        prob = model.predict_proba(vector)[0][1]

        # Explainable AI: find important words
        feature_names = vectorizer.get_feature_names_out()
        vector_array = vector.toarray()[0]

        important_words = []

        for i, value in enumerate(vector_array):
            if value > 0:
                important_words.append((feature_names[i], value))

        important_words = sorted(important_words, key=lambda x: x[1], reverse=True)

        top_words = [word for word, score in important_words[:3]]

        word_display = "\n".join([f"• {w}" for w in top_words]) if top_words else "• emotional signals detected"

        response = generate_response(prob, word_display)

    st.chat_message("assistant").write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })