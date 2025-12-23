import streamlit as st
import streamlit.components.v1 as components
import base64
import time
from dotenv import load_dotenv

from rag.retriever import retrieve, filter_chunks
from rag.prompt import build_prompt
from rag.gemini_client import get_client

# -------------------------------------------------
# 1. Config
# -------------------------------------------------
st.set_page_config(page_title="🧙 Harry Potter RAG", layout="wide")
load_dotenv()

# -------------------------------------------------
# 2. Session State
# -------------------------------------------------
# We track if music should be playing so we don't reset the timer
if "music_started" not in st.session_state:
    st.session_state.music_started = False

if "recent_queries" not in st.session_state:
    st.session_state.recent_queries = [
        "How many Horcruxes were created?",
        "Who was the heir of Slytherin?",
        "What is the Patronus charm?"
    ]

# -------------------------------------------------
# 3. GLOBAL PLACEHOLDERS
# -------------------------------------------------
# spell_placeholder needs to be cleared/filled for sound effects
spell_placeholder = st.empty()

# -------------------------------------------------
# 4. Assets
# -------------------------------------------------
def set_background(path):
    try:
        with open(path, "rb") as f:
            img = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{img}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except: pass

set_background("assets/background.jpeg")

def render_gapless_music():
    """
    Embeds audio in an iframe with aggressive JS to resume playback instantly.
    This creates the illusion of continuous play.
    """
    try:
        with open("assets/Hedwig.mp3", "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        
        # We use components.html because it is an iframe. 
        # It handles the JS lifecycle better than st.markdown.
        components.html(
            f"""
            <audio id="bg-music" loop>
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("bg-music");
                
                // 1. Recover timestamp from session storage immediately
                var savedTime = sessionStorage.getItem("audio_time");
                if (savedTime) {{
                    audio.currentTime = savedTime;
                }}
                
                // 2. Play immediately
                // Note: Browsers block this until the user has clicked at least once on the page.
                // Since the user is typing in a box, that counts as interaction.
                audio.play();

                // 3. Save timestamp every 0.5 seconds
                setInterval(function() {{
                    sessionStorage.setItem("audio_time", audio.currentTime);
                }}, 500);
            </script>
            """,
            height=0, # Invisible player
            width=0
        )
    except: pass

def play_spell_sound():
    # Clear previous sound
    spell_placeholder.empty()
    time.sleep(0.05)
    try:
        with open("assets/Spell.mp3", "rb") as f:
            audio = base64.b64encode(f.read()).decode()
        
        # Unique ID to force re-render
        unique_id = f"spell_{time.time()}"
        
        spell_placeholder.markdown(
            f"""
            <audio autoplay="true">
                <source src="data:audio/mp3;base64,{audio}" type="audio/mp3">
            </audio>
            <div style="display:none">{unique_id}</div>
            """,
            unsafe_allow_html=True
        )
    except: pass

# -------------------------------------------------
# 5. Header
# -------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;color:#f5c26b;font-family:serif;'>🧙 Harry Potter RAG Assistant ✨</h1>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# 🎵 MUSIC LOGIC (Auto-Start)
# -------------------------------------------------
# We render this on every run. The JS inside handles the resume logic.
render_gapless_music()

# -------------------------------------------------
# 6. Input
# -------------------------------------------------
try:
    client = get_client()
except:
    st.error("Check API Key")
    st.stop()

question = st.text_input(
    "Harry Potter Question",
    placeholder="e.g. How many Horcruxes were created?",
    label_visibility="collapsed"
)

# Recent queries buttons
if not question:
    st.markdown("### 📜 Recent Magical Inquiries")
    for q in st.session_state.recent_queries:
        if st.button(q, use_container_width=True):
            question = q

# -------------------------------------------------
# 7. Pipeline
# -------------------------------------------------
if question:
    # Flag that we have started (helps with browser permissions)
    if not st.session_state.music_started:
        st.session_state.music_started = True

    with st.spinner("🔍 Searching..."):
        chunks = retrieve(question)
        chunks = filter_chunks(question, chunks)
    
    if not chunks:
        st.warning("No context found.")
        st.stop()

    prompt = build_prompt(question, chunks)

    with st.spinner("🧠 Thinking..."):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt,
                config={"temperature": 0}
            )
            answer = response.text.strip()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    # 🔊 TRIGGER SPELL SOUND
    play_spell_sound()

    # Update history
    if question not in st.session_state.recent_queries:
        st.session_state.recent_queries.insert(0, question)
        st.session_state.recent_queries = st.session_state.recent_queries[:3]

    # Display Answer
    st.markdown("## 📜 Answer")
    st.markdown(
        f"""
        <div style='background: rgba(255,248,230,0.95); padding: 25px; border-radius: 15px; color: #3a2c1a; font-family: serif; font-size: 18px;'>
            {answer}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sources
    with st.expander("📚 Sources used"):
        seen = set()
        for c in chunks:
            key = (c.get("book"), c.get("chapter"))
            if key in seen:
                continue
            seen.add(key)
            st.markdown(f"**{c.get('book')}** \n{c.get('chapter')}")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown(
    "<hr><p style='text-align:center;color:#f0d9a6;'>⚡ RAG + Gemini + FAISS</p>",
    unsafe_allow_html=True
)