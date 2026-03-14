import streamlit as st
import joblib

# load model
model = joblib.load("model/depression_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

st.set_page_config(page_title="Mental Health AI", page_icon="🧠")

st.title("🧠 Mental Health AI Assistant")

st.write(
"""
Share how you're feeling and the AI will analyze emotional signals in your text.

⚠️ This tool is **not a medical diagnosis**.  
It is meant to encourage awareness and reflection.
"""
)

user_input = st.text_area("How are you feeling today?")

# list of nonsense / short responses
low_information_words = [
    "hi","hello","hey","ok","okay","hmm","lol","yes","no","yo"
]

if st.button("Analyze"):

    text = user_input.strip().lower()

    if text == "":
        st.warning("Please enter something about how you're feeling.")
    
    elif len(text.split()) < 3 or text in low_information_words:
        st.info(
        """
Try describing your feelings a bit more.

Example:
- "I feel tired and unmotivated lately"
- "I feel lonely and disconnected from people"
"""
        )

    else:

        with st.spinner("Analyzing emotional signals..."):

            vector = vectorizer.transform([user_input])
            prob = model.predict_proba(vector)[0][1]

        st.divider()

        if prob > 0.65:
            st.error("⚠️ Strong depression signal detected")

        elif prob > 0.40:
            st.warning("⚠️ Possible emotional distress detected")

        else:
            st.success("✅ No strong depression signal detected")

        st.write(f"Confidence score: **{prob*100:.2f}%**")

        if prob > 0.40:
            st.info(
            """
If you're struggling, consider talking to someone you trust.

Professional support can make a real difference.  
You don't have to go through things alone. ❤️
"""
            )