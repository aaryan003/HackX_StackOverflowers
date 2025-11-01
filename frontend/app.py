import streamlit as st
import requests
from datetime import datetime
import uuid
import json
from pathlib import Path
import time

# ============================================================================
# CONFIGURATION
# ============================================================================
API_BASE_URL = "http://localhost:8000"
PAGE_TITLE = "UniVerse - Intelligent Communication, Reimagined"
PAGE_ICON = ""

LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "gu": "Gujarati (ગુજરાતી)",
    "mr": "Marathi (मराठी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)"
}

DEMO_QUERIES = {
    "en": [
        "Tell me about the admission process",
        "What scholarships are available?",
        "When do placements start?",
        "What are the hostel facilities?"
    ],
    "hi": [
        "प्रवेश प्रक्रिया के बारे में बताएं",
        "कौन सी छात्रवृत्तियां उपलब्ध हैं?",
        "प्लेसमेंट कब शुरू होते हैं?"
    ],
    "gu": [
        "પ્રવેશ પ્રક્રિયા વિશે જણાવો",
        "કઈ શિષ્યવૃત્તિઓ ઉપલબ્ધ છે?"
    ]
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    """Load external CSS (no fallbacks or gradients)."""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if not css_path.exists():
        st.error(f"CSS not found at: {css_path}")
        return
    ts = int(time.time())  # cache buster each run
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style id='universe-css-{ts}'>\n{css}\n</style>", unsafe_allow_html=True)

load_css()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "en"
    if "backend_status" not in st.session_state:
        st.session_state.backend_status = None
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    if "show_demo_helper" not in st.session_state:
        st.session_state.show_demo_helper = True

# ============================================================================
# API FUNCTIONS
# ============================================================================
def check_backend_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, "🟢 Backend Connected"
        else:
            return False, f"🔴 Backend Error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "🔴 Backend Offline - Start backend on port 8000"
    except requests.exceptions.Timeout:
        return False, "🔴 Backend Timeout"
    except Exception as e:
        return False, f"🔴 Error: {str(e)}"

def send_message_to_backend(query, language):
    try:
        payload = {
            "query": query,
            "session_id": st.session_state.session_id,
            "language": language
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Backend error: {response.status_code}"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Backend took too long to respond."}
    except Exception as e:
        return False, {"error": f"Error: {str(e)}"}

def get_conversation_history():
    try:
        response = requests.get(
            f"{API_BASE_URL}/conversations/{st.session_state.session_id}",
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except Exception:
        return False, None

# ============================================================================
# UI HELPERS
# ============================================================================
def get_confidence_color(confidence):
    if confidence >= 0.7:
        return "🟢", "confidence-high", "#16a34a"
    elif confidence >= 0.5:
        return "🟡", "confidence-medium", "#d97706"
    else:
        return "🔴", "confidence-low", "#dc2626"

def format_sources(sources):
    if not sources:
        return ""
    tags = []
    for s in sources:
        t = s.get("type", "Unknown")
        c = s.get("category", "")
        label = f"{t}: {c}" if c else t
        tags.append(f'<span class="source-badge">{label}</span>')
    return f'<div class="source-badges">{" ".join(tags)}</div>'

def format_timestamp(ts):
    try:
        return datetime.fromisoformat(ts).strftime("%I:%M %p")
    except Exception:
        return ""

def export_conversation():
    conversation_data = {
        "session_id": st.session_state.session_id,
        "session_start": st.session_state.session_start_time.isoformat(),
        "language": st.session_state.selected_language,
        "total_messages": len(st.session_state.messages),
        "messages": st.session_state.messages
    }
    return json.dumps(conversation_data, indent=2, ensure_ascii=False)

# ============================================================================
# SIDEBAR
# ============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="uv-sidebrand">
            <div class="uv-sidebrand-title">UniVerse</div>
            <div class="uv-sidebrand-sub">Intelligent Communication</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📊 Session")
        st.markdown(f"**ID:** `{st.session_state.session_id[:12]}...`")
        st.markdown(f"**Language:** {LANGUAGES[st.session_state.selected_language]}")
        st.markdown(f"**Started:** {st.session_state.session_start_time.strftime('%I:%M %p')}")
        st.markdown("---")

        st.markdown("### 📈 Stats")
        total = len(st.session_state.messages)
        user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        bot_count = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        c1, c2 = st.columns(2)
        with c1: st.metric("Messages", total)
        with c2: st.metric("Queries", user_count)

        if bot_count > 0:
            avg_conf = sum([m.get("confidence", 0) for m in st.session_state.messages if m["role"] == "assistant"]) / bot_count
            emoji, _, _ = get_confidence_color(avg_conf)
            st.metric("Confidence", f"{emoji} {avg_conf:.0%}")

        st.markdown("---")
        st.markdown("### 💬 Messages")
        if total == 0:
            st.info("No messages yet")
        else:
            for message in list(reversed(st.session_state.messages))[:5]:
                role = message["role"]
                content = message["content"]
                ts = format_timestamp(message.get("timestamp", ""))
                display = content[:80] + "..." if len(content) > 80 else content
                if role == "user":
                    st.markdown(f"**👤** *{ts}*  \n{display}")
                else:
                    conf = message.get("confidence", 0)
                    emoji, _, _ = get_confidence_color(conf)
                    st.markdown(f"**🤖** *{ts}* {emoji}  \n{display}")
                st.markdown("<hr class='uv-hr'>", unsafe_allow_html=True)

        st.markdown("### ⚙️ Actions")
        a1, a2 = st.columns(2)
        with a1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with a2:
            if st.button("🔄 New", use_container_width=True):
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.session_start_time = datetime.now()
                st.rerun()

        if len(st.session_state.messages) > 0:
            st.download_button(
                label="📥 Export",
                data=export_conversation(),
                file_name=f"universe_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )

# ============================================================================
# MAIN AREA
# ============================================================================
def render_header():
    st.markdown("""
    <div class="uv-header">
      <h1 class="uv-title">UniVerse</h1>
      <p class="uv-subtitle">Intelligent Communication, Reimagined for the Modern Campus</p>
    </div>
    """, unsafe_allow_html=True)

    ok, msg = check_backend_health()
    st.session_state.backend_status = ok
    if ok:
        st.success(msg, icon="✅")
    else:
        st.error(msg, icon="❌")
        st.info("💡 **Start backend:** `cd backend && python main.py`")
        st.stop()

def render_branding_banner():
    st.markdown("""
    <div class="uv-banner">
      <span>🌐 10 Languages</span>
      <span>•</span>
      <span>🤖 RAG-Powered</span>
      <span>•</span>
      <span>⚡ Real-time Translation</span>
      <span>•</span>
      <span>🎯 Confidence Scoring</span>
    </div>
    """, unsafe_allow_html=True)

def render_message(message, idx):
    role = message["role"]
    content = message["content"]

    if role == "user":
        st.markdown(
            f"""
            <div class="uv-msg-row uv-right">
              <div class="message user-message">{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        confidence = message.get("confidence", 0)
        sources = message.get("sources", [])
        needs_handoff = message.get("needs_human_handoff", False)
        emoji, css_class, _ = get_confidence_color(confidence)

        st.markdown(
            f"""
            <div class="uv-msg-row">
              <div class="message bot-message">{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        m1, m2, _ = st.columns([1, 3, 1])
        with m1:
            st.markdown(
                f"<span class='confidence-pill {css_class}'>{emoji} {confidence:.0%}</span>",
                unsafe_allow_html=True
            )
        with m2:
            if sources:
                st.markdown(format_sources(sources), unsafe_allow_html=True)

        if needs_handoff:
            st.warning("⚠️ Low confidence - Consider human support", icon="⚠️")
            if st.button("🙋 Request Support", key=f"support_{idx}"):
                st.success("✅ Support notified!")

def render_chat_interface():
    st.markdown("---")
    chat_container = st.container()
    with chat_container:
        if len(st.session_state.messages) == 0:
            st.markdown("""
            <div class="uv-welcome">
              <h2>👋 Welcome to UniVerse!</h2>
              <p class="lead">Intelligent Communication, Reimagined for the Modern Campus</p>
              <p>I can help you with:</p>
              <p>📚 <b>Admissions</b> • 💰 <b>Fees & Scholarships</b> • 🏢 <b>Placements</b><br>
                 🏠 <b>Hostels</b> • 📅 <b>Events</b> • ℹ️ <b>Campus Info</b></p>
              <p class="muted">Available in 10 Indian languages • Powered by AI</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, message in enumerate(st.session_state.messages):
                render_message(message, idx)
    st.markdown("<br>", unsafe_allow_html=True)

def render_demo_helper():
    if st.session_state.show_demo_helper and len(st.session_state.messages) == 0:
        with st.expander("🎯 Quick Demo Queries", expanded=False):
            st.markdown("<div class='quick-start-title'>Click to test</div>", unsafe_allow_html=True)
            demo_lang = st.session_state.selected_language
            queries = DEMO_QUERIES.get(demo_lang, DEMO_QUERIES["en"])
            cols = st.columns(2)
            for idx, query in enumerate(queries):
                with cols[idx % 2]:
                    if st.button(f"💬 {query[:40]}...", key=f"demo_{idx}", use_container_width=True):
                        handle_send_message(query)

def render_input_section():
    st.markdown("---")
    c1, c2 = st.columns([4, 1])
    with c1:
        selected = st.selectbox(
            "🌐 Language:",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.selected_language),
            key="language_selector",
            label_visibility="collapsed"
        )
        st.session_state.selected_language = selected
    with c2:
        st.markdown(f"**{LANGUAGES[selected].split('(')[0].strip()}**")

    render_demo_helper()

    i1, i2 = st.columns([6, 1])
    with i1:
        user_input = st.text_input(
            "Message:",
            placeholder=f"Ask in {LANGUAGES[st.session_state.selected_language]}...",
            key="user_input",
            label_visibility="collapsed",
            disabled=st.session_state.is_processing
        )
    with i2:
        send_button = st.button(
            "Send" if not st.session_state.is_processing else "⏳",
            use_container_width=True,
            disabled=st.session_state.is_processing,
            type="primary",
            help="Send message"
        )

    if send_button and user_input.strip():
        handle_send_message(user_input.strip())

    st.caption("💡 Tip: Press Enter to send")

def handle_send_message(user_message):
    st.session_state.is_processing = True
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })

    with st.spinner("🤔 Processing..."):
        success, data = send_message_to_backend(user_message, st.session_state.selected_language)
        if success:
            st.session_state.messages.append({
                "role": "assistant",
                "content": data.get("response", "No response generated."),
                "confidence": data.get("confidence", 0),
                "sources": data.get("sources", []),
                "needs_human_handoff": data.get("needs_human_handoff", False),
                "timestamp": datetime.now().isoformat()
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error: {data.get('error', 'Unknown error')}",
                "confidence": 0,
                "sources": [],
                "needs_human_handoff": True,
                "timestamp": datetime.now().isoformat()
            })

    st.session_state.is_processing = False
    st.rerun()

# ============================================================================
# MAIN
# ============================================================================
def main():
    initialize_session_state()
    render_sidebar()
    render_header()
    render_branding_banner()
    render_chat_interface()
    render_input_section()

    st.markdown("---")
    st.markdown("""
    <div class="footer">
      <div class="footer-brand">UniVerse</div>
      <div class="footer-sub">Intelligent Communication, Reimagined for the Modern Campus</div>
      <div class="footer-small">🏆 HackX 2025 • Team StackOverflowers — Built with Streamlit • FastAPI • LLaMA 3.3 • ChromaDB</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()