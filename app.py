import sys, os
if __name__ == "__main__" and not os.environ.get("_TC_LAUNCHED"):
    import subprocess
    env = {**os.environ, "_TC_LAUNCHED": "1"}
    sys.exit(subprocess.run([
        sys.executable, "-m", "streamlit", "run", __file__,
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
    ] + sys.argv[1:], env=env).returncode)

import streamlit as st
from claude_client import ClaudeClient, DEMO_MODE
from prompts import get_system_prompt

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TerrapinCompass – UMD AI Guide",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── UMD brand colours ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* UMD red + gold accent */
    [data-testid="stSidebar"] { background-color: #1a1a1a; }
    [data-testid="stSidebar"] * { color: #f5f5f5 !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #FFD200 !important; font-weight: 700; }
    .umd-header {
        background: linear-gradient(135deg, #E21833 0%, #9b0000 100%);
        border-left: 6px solid #FFD200;
        padding: 18px 24px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
    }
    .umd-header h1 { margin: 0; font-size: 1.6rem; }
    .umd-header p  { margin: 4px 0 0; opacity: .85; font-size: 0.95rem; }
    .tip-box {
        background: #fff8e1;
        border-left: 4px solid #FFD200;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state initialisation ──────────────────────────────────────────────
def _init():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "profile" not in st.session_state:
        st.session_state.profile = {}
    if "mode" not in st.session_state:
        st.session_state.mode = "navigator"
    if "client" not in st.session_state:
        st.session_state.client = ClaudeClient()
    if "profile_saved" not in st.session_state:
        st.session_state.profile_saved = False

_init()

# ── Sidebar ───────────────────────────────────────────────────────────────────
MODES = {
    "navigator": "🧭  Campus Navigator",
    "tutor":     "🎓  Academic Tutor",
    "career":    "💼  Career Prep Coach",
    "financial": "💰  Financial Literacy",
}

PLACEHOLDERS = {
    "navigator": "Ask about scholarships, FAFSA, first-gen programs, emergency funds…",
    "tutor":     "Ask me to help with CMSC131, MATH140, BSCI170, or any UMD course…",
    "career":    "Paste your resume, ask about interview prep, internships, or networking…",
    "financial": "Ask about budgeting, student loans, understanding your first paycheck…",
}

SUBTITLES = {
    "navigator": "Connecting you to UMD resources you might not know exist.",
    "tutor":     "Adaptive tutoring personalised to your UMD courses.",
    "career":    "Resume, interviews, and career strategy for every background.",
    "financial": "Real money skills for college and the workforce.",
}

with st.sidebar:
    st.markdown("## 🐢 TerrapinCompass")
    st.markdown("*AI-powered campus guide for UMD students*")
    st.divider()

    st.markdown("### Mode")
    selected = st.selectbox(
        "What do you need help with?",
        options=list(MODES.keys()),
        format_func=lambda k: MODES[k],
        index=list(MODES.keys()).index(st.session_state.mode),
    )
    if selected != st.session_state.mode:
        st.session_state.mode = selected
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Student profile
    st.markdown("### Your Profile")
    st.caption("Personalises every response to your situation.")

    with st.form("profile_form"):
        year = st.selectbox(
            "Year",
            ["(not set)", "Freshman", "Sophomore", "Junior", "Senior", "Graduate", "Transfer", "Non-Degree"],
        )
        major = st.text_input("Major / Program", placeholder="e.g. Computer Science")
        first_gen = st.checkbox("First-generation college student")
        transfer = st.checkbox("Transfer student")
        background = st.text_area(
            "Anything else I should know?",
            placeholder="e.g. working 20 hrs/week, undocumented, veteran, international student…",
            height=80,
        )
        if st.form_submit_button("Save Profile", use_container_width=True):
            st.session_state.profile = {
                "year": year if year != "(not set)" else None,
                "major": major or None,
                "first_gen": first_gen,
                "transfer": transfer,
                "background": background or None,
            }
            st.session_state.messages = []
            st.session_state.profile_saved = True
            st.rerun()

    if st.session_state.profile_saved:
        st.success("Profile saved – responses are now personalised.")

    st.divider()

    # Quick resource links
    st.markdown("### Quick Links")
    links = [
        ("🏛️ Financial Aid Office", "https://financialaid.umd.edu"),
        ("💼 University Career Center", "https://careers.umd.edu"),
        ("📚 Free Tutoring (LAS)", "https://tutoring.umd.edu"),
        ("✍️ Writing Center", "https://writing.umd.edu"),
        ("🌟 First-Gen Programs", "https://firstgeneration.umd.edu"),
        ("🍎 Campus Pantry", "https://campuspantry.umd.edu"),
        ("🧠 Counseling Center", "https://counseling.umd.edu"),
    ]
    for label, url in links:
        st.markdown(f"[{label}]({url})")

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main content area ──────────────────────────────────────────────────────────
mode = st.session_state.mode

st.markdown(
    f"""
    <div class="umd-header">
        <h1>{MODES[mode]}</h1>
        <p>{SUBTITLES[mode]}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Demo mode banner
if DEMO_MODE:
    st.warning(
        "**Demo Mode** — Running with curated UMD-specific responses. "
        "Set `ANTHROPIC_API_KEY` in your environment to enable live AI.",
        icon="🔑",
    )

# Profile onboarding nudge (shown only until first message)
if not st.session_state.messages and not st.session_state.profile_saved:
    st.info(
        "**Tip:** Fill out Your Profile in the sidebar so I can give you personalised, "
        "UMD-specific advice — especially if you're first-gen, a transfer student, or "
        "have a specific background.",
        icon="👋",
    )

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input(PLACEHOLDERS[mode]):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    system = get_system_prompt(mode, st.session_state.profile)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            for chunk in st.session_state.client.stream_chat(
                messages=st.session_state.messages,
                system=system,
                max_tokens=1500,
                mode=mode,
            ):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"⚠️ Something went wrong: {e}"
            response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
