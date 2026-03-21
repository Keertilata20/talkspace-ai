import streamlit as st
import joblib
import random
import time
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import re
from supabase import create_client, Client
import uuid

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

load_dotenv()


# -----------------------------
# USER IDENTIFICATION
# -----------------------------
query_params = st.query_params

if "user_id" in query_params:
    st.session_state.user_id = query_params["user_id"]
else:
    new_id = str(uuid.uuid4())
    st.session_state.user_id = new_id
    st.query_params["user_id"] = new_id


if "conversation_id" in st.query_params:
    st.session_state.conversation_id = st.query_params["conversation_id"]
else:
    new_conv = str(uuid.uuid4())
    st.session_state.conversation_id = new_conv
    st.query_params["conversation_id"] = new_conv


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
    background: linear-gradient(120deg, #E8F5E9, #F1F8F6, #E3F2FD);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F1F5F3, #E8F0EC);
    padding: 1rem;
}
            [data-testid="stSidebar"] h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    color: #374151;
}

.block-container {
padding-top:2rem;
max-width:900px;
}
            
            [data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 14px 18px;
    max-width:75%;
    margin-bottom: 12px;
    background-color: rgba(255,255,255,0.7);
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
               animation: fadeIn 0.3s ease-in;
}
            @keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
            [data-testid="stChatMessage"]:hover {
    transform: translateY(-2px);
         
}
            img {
    border-radius: 50%;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}

/* Nira glow */
[data-testid="stChatMessage"][data-testid*="assistant"] img {
    box-shadow: 0 0 0 2px rgba(134,239,172,0.4);
}

/* User subtle */
[data-testid="stChatMessage"][data-testid*="user"] img {
    opacity: 0.95;
}
            

/* user messages */
[data-testid="stChatMessage"][data-testid*="user"] {
    margin-left: auto;
    background: linear-gradient(135deg, #DCF8E6, #CFF3E1);
    border-radius: 18px 18px 4px 18px;

}

/* assistant messages */
[data-testid="stChatMessage"][data-testid*="assistant"] {
    margin-right: auto;
    background: #ffffff;
    border-radius: 18px 18px 18px 4px;
}
            textarea {
    border-radius: 999px !important;
    padding: 14px 20px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
            textarea:focus {
    border-color: #86efac !important;
    box-shadow: 0 0 0 2px rgba(134,239,172,0.3);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------

st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
    <h1 style="margin-bottom:5px;">🌿 TalkSpace</h1>
    <p style="color:#6b7280;">Nira is here… just for you</p>
</div>
""", unsafe_allow_html=True)
# -----------------------------
# GET CONVERSATIONS
# -----------------------------

def get_conversations():
    response = supabase.table("messages") \
        .select("conversation_id, content, role, created_at") \
        .eq("user_id", st.session_state.user_id) \
        .order("created_at") \
        .execute()

    data = response.data if response.data else []

    conversations = {}
    greetings = ["hi", "hello", "hey", "yo"]

    for msg in data:
        cid = msg["conversation_id"]

        if cid not in conversations and msg["role"] == "user":
            text = msg["content"].lower()

            # skip boring greetings
            if any(greet in text for greet in greetings) and len(text) < 10:
                continue

            conversations[cid] = msg["content"][:40]

    return conversations

# -----------------------------
# SIDEBAR
# -----------------------------

mode = st.sidebar.selectbox(
"Conversation Style",
["Supportive Friend","Counselor"]
)


if st.sidebar.button("➕ New Chat"):
    new_conv = str(uuid.uuid4())
    st.session_state.conversation_id = new_conv
    st.query_params["conversation_id"] = new_conv
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Clear Conversation"):
    # delete from database
    supabase.table("messages") \
    .delete() \
    .eq("user_id", st.session_state.user_id) \
    .eq("conversation_id", st.session_state.conversation_id) \
    .execute()

    # clear session
    st.session_state.messages = []
    st.session_state.topic_memory = []
    st.session_state.emotion_history = []

    st.rerun()

st.sidebar.markdown("### 💬 Your Chats")

conversations = get_conversations()

for cid, title in conversations.items():
    if st.sidebar.button(title, key=cid):
        st.session_state.conversation_id = cid
        st.query_params["conversation_id"] = cid
        st.session_state.messages = []
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

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    response = supabase.table("messages") \
        .select("*") \
        .eq("user_id", st.session_state.user_id) \
        .eq("conversation_id", st.session_state.conversation_id) \
        .order("created_at") \
        .execute()

    data = response.data if response.data else []

    st.session_state.messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in data
    ]

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
"life is pointless",
 "should die",
    "told me to die",
    "want me to die",
    "they said i should die",
    "i feel worthless",
    "i am hopeless"
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

    if not text:
        return "general"

    text = text.lower()

    for emotion, words in emotion_keywords.items():
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




def clean_response(text):
    if not text:
        return text

    # fix glued lowercase words using common patterns
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # fix common broken joins
    fixes = {
        "thatloneliness": "that loneliness",
        "fightreally": "fight really",
        "ifeel": "i feel",
        "iwant": "i want",
        "imso": "i'm so",
        "itsreally": "it's really"
    }

    for wrong, correct in fixes.items():
        text = text.replace(wrong, correct)

    return text

def get_memory_reference():

    if len(st.session_state.messages) < 6:
        return ""

    # get a past user message (not too recent)
    for msg in reversed(st.session_state.messages[:-2]):
        if msg["role"] == "user":
            return f"\n\nYou mentioned earlier: \"{msg['content']}\""

    return ""

# -----------------------------
# RESPONSE GENERATOR
# -----------------------------

def generate_ai_response(user_input, emotion, history, intensity):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
       "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    user_messages = [m["content"] for m in history if m["role"] == "user"]
    memory_context = ""
    if len(user_messages) >= 3:
        recent = user_messages[-3:]
        memory_context = f"Recent user themes: {', '.join(recent)}"
    

    messages = [
        {
            "role": "system",
            "content": f"""
You are Nira, a gentle and emotionally present companion.

You speak like a real human who genuinely cares — not like an assistant, therapist, or system.

IMPORTANT:
- Keep responses short (1–2 sentences most of the time).
- Avoid long explanations or paragraphs.
- Keep replies natural and flowing, not overly minimal or empty.
- Each response should feel slightly different and not repetitive.
- Do not sound scripted, structured, or “perfect”.
- Keep language simple and everyday, like texting. Avoid complex or formal words.

Tone:
- warm, calm, and natural
- slightly casual, like real conversation
- emotionally present but not overly intense or dramatic

Conversation style:
- Sometimes respond with a short reflection
- Sometimes gently continue the conversation
- Sometimes just acknowledge and pause
- Not every reply needs a question
- Let the conversation breathe — don’t push it forward every time

You:
- acknowledge feelings in a human, personal way (not generic or formulaic)
- reflect naturally on what the user said (no analysis tone)
- ask a gentle question only when it feels natural and helpful

Avoid:
- robotic phrases like "I hear that loneliness"
- therapist-style language like "I sense...", "It seems like..."
- overly formal, clinical, or analytical tone
- sounding too polished, poetic, or motivational
- using words like "buddy", "sweetheart", etc.
- repeating phrases like "I'm here with you" too often
- repeating the same sentence structures across responses
- complex words like "yearning", "genuine connections", "it sounds like you're experiencing"

When the user shares something painful:
- slow down
- respond with empathy first
- do NOT jump into questions immediately
- sometimes just sit with the feeling instead of moving the conversation forward

When emotions are strong (e.g. "it's killing me", "I feel empty", "I have no one"):
- respond with deeper emotional presence
- keep it simple but more felt
- avoid sounding generic or surface-level

Friendship requests:
- respond warmly but casually
- avoid strong, dramatic, or overly committed statements
- keep it natural, like a real person would

If the user's message contains typos, grammar mistakes, or unclear wording:
- do NOT point them out
- do NOT analyze or correct them
- assume the intended meaning and respond naturally

When the user speaks casually, angrily, or uses strong language:
- respond more like a real person, not a therapist
- do NOT analyze their emotion formally
- do NOT say "it sounds like you're feeling..."
- react naturally, even slightly casual if appropriate

Examples:
- "hey… that was strong 😅 what happened?"
- "okay… something’s bothering you huh"
- "hmm… that came out of nowhere, you okay?"

Focus on what the user is trying to express, not how they wrote it.

Use small natural expressions occasionally:
"yeah…"
"hmm…"
"that sounds really hard"
"I get why that would feel that way"

But:
- do NOT overuse them
- do NOT use them in every response

Variation rule:
- Do not ask a question in every reply
- Do not always validate the same way
- Change rhythm: sometimes short, sometimes slightly fuller
- Make responses feel like they come from a real person, not a pattern

You are allowed to be slightly informal and human.
Not every response needs to sound emotionally perfect.

Sometimes:
- react instead of analyzing
- be a little casual
- be imperfect like a real person

End responses naturally, like a real person texting — not like a quote, lesson, or motivational line.

Stay present with the user. You are here to be with them, not to fix them.

---

Current emotion: {emotion}
{memory_context}
Conversation intensity level: {intensity}

If intensity is high (2–3):
- prioritize emotional presence over conversation flow
- avoid repeated or unnecessary questions
- lean into empathy and stillness

If intensity is low:
- gentle curiosity is okay
- light questions can help continue the conversation


"""
        }
    ]
    for msg in history[-4:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": user_input
    })
    data = {
   "model": "meta-llama/llama-3-8b-instruct",
    "messages": messages,
    "temperature": 0.7,
    "max_tokens": 60
}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(response.text)  # debug
        return None
    
    res_json = response.json()
    if "choices" not in res_json:
        print(res_json)  # debug
        return None
    return res_json['choices'][0]['message']['content']






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
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
NIRA_AVATAR = "https://cdn-icons-png.flaticon.com/512/6997/6997662.png"
for msg in st.session_state.messages:
    avatar = USER_AVATAR if msg["role"] == "user" else NIRA_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------

user_input = st.chat_input("Share what's on your mind...")

greetings = ["hi","hello","hey","yo"]
closings = ["bye","thanks","thank you","im done","i'm done","bye for now","bye bye", "later","thank you for now","i should leave"]

if user_input:

    # clean input FIRST
    clean_input = user_input.strip()
    clean_input = " ".join(clean_input.split())

    # detect emotion
    emotion = detect_emotion(clean_input)

    # display
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(clean_input)

    # store
    st.session_state.messages.append({
        "role": "user",
        "content": clean_input
    })

    supabase.table("messages").insert({
    "user_id": st.session_state.user_id,
    "conversation_id": st.session_state.conversation_id,
    "role": "user",
    "content": user_input
}).execute()

    # normalized text for logic
    text = clean_input.lower()
    
    if "intensity" not in st.session_state:
        st.session_state.intensity = 0

    # CRISIS RESPONSE (HIGHEST PRIORITY)
    if any(word in text for word in crisis_words):
        st.session_state.intensity = 3
        response = """
    I'm really sorry that you're going through something this painful.
    You don’t have to handle this alone.
    If you can, please consider reaching out to someone you trust or a trained professional.
    You deserve support, especially right now.
    """
    # NORMAL EMOTION FLOW
    else:
        if emotion in ["sadness", "loneliness"]:
            st.session_state.intensity = min(st.session_state.intensity + 1, 3)
        else:
            st.session_state.intensity = max(st.session_state.intensity - 1, 0)
        st.session_state.topic_memory.append(emotion)
        st.session_state.emotion_history.append(emotion)
        
        try:
            response = generate_ai_response(
            clean_input, 
            emotion,
            st.session_state.messages,
            st.session_state.intensity
        )
            response = clean_response(response)
            if not response:
                response = "that sounds really tough… I’m here with you."
                
        except Exception as e:
            print("API ERROR:", e)
            response = random.choice([
        "that sounds really heavy… I’m here with you.",
        "yeah… that kind of thing can really hurt. I’m here.",
        "that’s a lot to carry… you don’t have to hold it alone here."
    "hmm… I’m here with you.",
    "yeah… I’m listening.",
    "I’m here… take your time.",
])

    
    
    # THINKING ANIMATION

    with st.chat_message("assistant", avatar=NIRA_AVATAR):
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
    supabase.table("messages").insert({
    "user_id": st.session_state.user_id,
    "conversation_id": st.session_state.conversation_id,
    "role": "assistant",
    "content": response
}).execute()