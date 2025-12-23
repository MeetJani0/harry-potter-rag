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
if "music_started" not in st.session_state:
    st.session_state.music_started = False

if "recent_queries" not in st.session_state:
    st.session_state.recent_queries = [
        "How many Horcruxes were created?",
        "Who was the heir of Slytherin?",
        "What is the Patronus charm?"
    ]

# -------------------------------------------------
# 3. Global placeholders
# -------------------------------------------------
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
                background:
                  linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.85)),
                  url("data:image/jpeg;base64,{img}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

set_background("assets/background.jpeg")

# -------------------------------------------------
# 🎵 Persistent background music (iframe + JS)
# -------------------------------------------------
def render_gapless_music():
    try:
        with open("assets/Hedwig.mp3", "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        components.html(
            f"""
            <audio id="bg-music" loop>
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>

            <script>
                const audio = document.getElementById("bg-music");

                const savedTime = sessionStorage.getItem("audio_time");
                if (savedTime) {{
                    audio.currentTime = savedTime;
                }}

                audio.play().catch(() => {{}});

                setInterval(() => {{
                    sessionStorage.setItem("audio_time", audio.currentTime);
                }}, 500);
            </script>
            """,
            height=0,
            width=0
        )
    except:
        pass

# -------------------------------------------------
# 🔮 Spell sound (re-trigger safe)
# -------------------------------------------------
def play_spell_sound():
    spell_placeholder.empty()
    time.sleep(0.05)

    try:
        with open("assets/Spell.mp3", "rb") as f:
            audio = base64.b64encode(f.read()).decode()

        unique_id = f"spell_{time.time()}"

        spell_placeholder.markdown(
            f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio}" type="audio/mp3">
            </audio>
            <div style="display:none">{unique_id}</div>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

# -------------------------------------------------
# 5. Header
# -------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;color:#f5c26b;font-family:serif;'>🧙 Harry Potter RAG Assistant ✨</h1>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# 🎵 Always render background music
# -------------------------------------------------
render_gapless_music()

# -------------------------------------------------
# 6. Gemini init
# -------------------------------------------------
try:
    genai = get_client()
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    st.error(f"Gemini init failed: {e}")
    st.stop()

# -------------------------------------------------
# 7. Input
# -------------------------------------------------
question = st.text_input(
    "Harry Potter Question",
    placeholder="e.g. How many Horcruxes were created?",
    label_visibility="collapsed"
)

# Recent queries
if not question:
    st.markdown("### 📜 Recent Magical Inquiries")
    for q in st.session_state.recent_queries:
        if st.button(q, use_container_width=True):
            question = q

# -------------------------------------------------
# 8. RAG pipeline
# -------------------------------------------------
if question:
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
            response = model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            st.error(f"Gemini error: {e}")
            st.stop()

    # 🔊 Spell sound ON EVERY ANSWER
    play_spell_sound()

    # Save history
    if question not in st.session_state.recent_queries:
        st.session_state.recent_queries.insert(0, question)
        st.session_state.recent_queries = st.session_state.recent_queries[:3]

    # -------------------------------------------------
    # Answer
    # -------------------------------------------------
    st.markdown("## 📜 Answer")
    st.markdown(
        f"""
        <div style="
            background: rgba(255,248,230,0.95);
            padding: 25px;
            border-radius: 15px;
            font-family: serif;
            font-size: 18px;
            color: #3a2c1a;">
            {answer}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # Sources
    # -------------------------------------------------
    with st.expander("📚 Sources used"):
        seen = set()
        for c in chunks:
            key = (c.get("book"), c.get("chapter"))
            if key in seen:
                continue
            seen.add(key)
            st.markdown(f"**{c.get('book')}**  \n{c.get('chapter')}")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown(
    "<hr><p style='text-align:center;color:#f0d9a6;'>⚡ RAG + Gemini + FAISS</p>",
    unsafe_allow_html=True
)