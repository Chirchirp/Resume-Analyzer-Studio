"""ATS Resume Studio v3 - Home Page"""
import streamlit as st


def render_home():
    st.markdown("""
    <div class="hero-banner">
        <div style='font-size:52px;margin-bottom:8px'>🎯</div>
        <h1>ATS Resume Studio</h1>
        <p>AI-powered resume coaching — get past the bots, land interviews.</p>
        <p style='font-size:14px;margin-top:8px;opacity:0.85'>
            ⚡ Groq FREE · 🖥️ Ollama LOCAL FREE · Token-smart · No data stored
        </p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.api_key_verified:
        st.info(
            "⚡ **Get started free:** Select **Groq** or **Ollama (local)** in the sidebar and connect. "
            "[Get Groq key free →](https://console.groq.com/keys) · "
            "[Install Ollama free →](https://ollama.ai)",
            icon="🔑",
        )

    # Stats
    cols = st.columns(4)
    for col, (val, label) in zip(cols, [
        ("100%","Free Option Available"),("10x","Fewer Tokens Used"),
        ("5 min","Full Analysis"),("8","AI-Powered Tools"),
    ]):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Free options callout
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(16,185,129,0.08));
                border:1px solid rgba(99,102,241,0.25);border-radius:14px;padding:20px 24px;margin-bottom:24px'>
        <div style='font-size:16px;font-weight:700;color:#3730a3;margin-bottom:12px'>
            💸 Zero-Cost Options — No Credit Card Needed
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:14px'>
            <div>
                <b style='color:#6366f1'>⚡ Groq Cloud (FREE)</b><br>
                <span style='color:#475569'>Best cloud option. Fast Llama 3.3 70B.
                <a href='https://console.groq.com/keys' target='_blank'>Get key →</a></span>
            </div>
            <div>
                <b style='color:#059669'>🖥️ Ollama (LOCAL FREE)</b><br>
                <span style='color:#475569'>Runs on your machine. Zero API cost. 100% private.
                <a href='https://ollama.ai' target='_blank'>Install →</a></span>
            </div>
        </div>
        <div style='font-size:12px;color:#64748b;margin-top:10px'>
            Using paid providers? v3 uses 60–80% fewer tokens than v2 — saving real money.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Everything you need to land the job</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Eight AI tools, one seamless workflow — start with ATS Analyzer.</div>', unsafe_allow_html=True)

    features = [
        ("🔍","ATS Analyzer","Get an ATS score, keyword gaps, section feedback, and Marcus Reid's honest coaching.","🔍 ATS Analyzer"),
        ("🏗️","Resume Builder","Build a polished ATS-ready resume from scratch.","🏗️ Resume Builder"),
        ("✨","Resume Optimizer","Paste resume + JD, get a fully rewritten optimized version.","✨ Resume Optimizer"),
        ("✉️","Cover Letter","Generate a tailored, compelling cover letter.","✉️ Cover Letter"),
        ("📝","Study Q&A","Generate interview questions with STAR model answers.","🎯 Interview Prep"),
        ("🎤","Practice Coach","AI asks questions, you answer, AI grades with STAR scoring.","🎯 Interview Prep"),
        ("🏆","Shortlist Accelerator","Surgical gap analysis to break into the top 10 shortlist.","🚀 Cool Features"),
        ("🎯","Match %","Precise role match percentage with gap breakdown.","🚀 Cool Features"),
    ]

    for row in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, desc, page) in zip(cols, features[row:row+3]):
            with col:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Open {title}", key=f"home_{title}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
