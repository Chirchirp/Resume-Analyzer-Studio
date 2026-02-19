"""
ATS Resume Studio - ATS Analyzer Page
"""

import streamlit as st
from src.core.llm import analyze_resume
from src.utils.file_parser import extract_text_from_file, clean_text


def _require_api_key():
    if not st.session_state.api_key_verified:
        st.warning("🔑 Please connect your OpenAI API key in the sidebar to use this feature.")
        return False
    return True


def _score_color(score: int) -> str:
    if score >= 75:
        return "#10b981"
    elif score >= 50:
        return "#f59e0b"
    return "#ef4444"


def _score_class(score: int) -> str:
    if score >= 75:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    return "score-low"


def render_analyzer():
    st.markdown(
        """
        <div class="section-title">🔍 ATS Resume Analyzer</div>
        <div class="section-subtitle">Upload your resume and paste the job description to get a detailed ATS compatibility report.</div>
        """,
        unsafe_allow_html=True,
    )

    if not _require_api_key():
        return

    # ── Input Section ──────────────────────────────────────────────
    with st.container():
        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            st.markdown("#### 📄 Your Resume")
            upload_tab, paste_tab = st.tabs(["📁 Upload File", "📝 Paste Text"])

            with upload_tab:
                uploaded = st.file_uploader(
                    "Upload Resume",
                    type=["pdf", "docx", "txt"],
                    help="Supports PDF, DOCX, and TXT files",
                    label_visibility="collapsed",
                )
                if uploaded:
                    text, err = extract_text_from_file(uploaded)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.resume_text = clean_text(text)
                        st.success(f"✅ Loaded: {uploaded.name} ({len(text.split())} words)")

            with paste_tab:
                pasted = st.text_area(
                    "Paste your resume text",
                    value=st.session_state.resume_text,
                    height=280,
                    placeholder="Paste your full resume text here...",
                    label_visibility="collapsed",
                )
                if pasted != st.session_state.resume_text:
                    st.session_state.resume_text = pasted

        with col_right:
            st.markdown("#### 🏢 Job Description")
            jd = st.text_area(
                "Job Description",
                value=st.session_state.job_description,
                height=320,
                placeholder="Paste the full job description here...\n\nInclude responsibilities, requirements, and qualifications for the most accurate analysis.",
                label_visibility="collapsed",
            )
            st.session_state.job_description = jd

    # Word counts
    col_wc1, col_wc2, col_sp = st.columns([1, 1, 2])
    with col_wc1:
        r_words = len(st.session_state.resume_text.split()) if st.session_state.resume_text else 0
        st.caption(f"Resume: {r_words} words")
    with col_wc2:
        j_words = len(st.session_state.job_description.split()) if st.session_state.job_description else 0
        st.caption(f"Job Description: {j_words} words")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Analyze Button ─────────────────────────────────────────────
    col_btn, col_clr, _ = st.columns([2, 1, 3])
    with col_btn:
        analyze_clicked = st.button(
            "🚀 Analyze My Resume",
            type="primary",
            use_container_width=True,
            disabled=(not st.session_state.resume_text or not st.session_state.job_description),
        )
    with col_clr:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.resume_text = ""
            st.session_state.job_description = ""
            st.session_state.analysis_result = None
            st.rerun()

    if analyze_clicked:
        if not st.session_state.resume_text:
            st.error("Please provide your resume.")
            return
        if not st.session_state.job_description:
            st.error("Please provide the job description.")
            return

        with st.spinner("🤖 Analyzing your resume against the job description..."):
            try:
                result = analyze_resume(
                    st.session_state.api_key,
                    st.session_state.api_provider,
                    st.session_state.model,
                    st.session_state.resume_text,
                    st.session_state.job_description,
                )
                st.session_state.analysis_result = result
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                return

    # ── Results Section ────────────────────────────────────────────
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        st.markdown("---")
        st.markdown("### 📊 Analysis Results")

        # Top Score Row
        score = result.get("ats_score", 0)
        breakdown = result.get("score_breakdown", {})

        col_score, col_breakdown = st.columns([1, 3], gap="large")

        with col_score:
            score_class = _score_class(score)
            score_color = _score_color(score)
            verdict = "Excellent" if score >= 75 else ("Good" if score >= 50 else "Needs Work")

            st.markdown(
                f"""
                <div class="studio-card" style="text-align:center; padding:32px 20px;">
                    <div style="font-size:13px; color:#64748b; font-weight:600; text-transform:uppercase;
                                letter-spacing:1px; margin-bottom:16px;">ATS Score</div>
                    <div class="score-badge {score_class}" style="margin:0 auto 16px auto;">
                        {score}
                    </div>
                    <div style="font-size:16px; font-weight:700; color:{score_color};">{verdict}</div>
                    <div style="font-size:12px; color:#94a3b8; margin-top:4px;">out of 100</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_breakdown:
            st.markdown(
                """<div class="studio-card">
                    <div style="font-size:15px; font-weight:700; color:#0f172a; margin-bottom:16px;">Score Breakdown</div>""",
                unsafe_allow_html=True,
            )
            for label, key in [
                ("Keyword Match", "keyword_match"),
                ("Format Compatibility", "format_compatibility"),
                ("Skills Alignment", "skills_alignment"),
                ("Experience Relevance", "experience_relevance"),
                ("Education Match", "education_match"),
            ]:
                val = breakdown.get(key, 0)
                color = _score_color(val)
                st.markdown(f"**{label}** — {val}/100")
                st.progress(val / 100)

            st.markdown("</div>", unsafe_allow_html=True)

        # Keyword Analysis
        st.markdown("#### 🔤 Keyword Analysis")
        kw_col1, kw_col2 = st.columns(2, gap="large")

        with kw_col1:
            matched = result.get("matched_keywords", [])
            st.markdown(
                f"<div style='font-weight:700; color:#166534; margin-bottom:8px;'>✅ Matched Keywords ({len(matched)})</div>",
                unsafe_allow_html=True,
            )
            if matched:
                tags_html = "".join(f'<span class="tag-found">{k}</span>' for k in matched)
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.info("No matched keywords detected.")

        with kw_col2:
            missing = result.get("missing_keywords", [])
            st.markdown(
                f"<div style='font-weight:700; color:#991b1b; margin-bottom:8px;'>❌ Missing Keywords ({len(missing)})</div>",
                unsafe_allow_html=True,
            )
            if missing:
                tags_html = "".join(f'<span class="tag-missing">{k}</span>' for k in missing)
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
            else:
                st.success("Great! No important keywords missing.")

        # Strengths & Weaknesses
        st.markdown("<br>", unsafe_allow_html=True)
        sw_col1, sw_col2 = st.columns(2, gap="large")

        with sw_col1:
            strengths = result.get("strengths", [])
            st.markdown(
                """<div class="studio-card" style="border-left:4px solid #10b981;">
                    <div style="font-size:15px; font-weight:700; color:#065f46; margin-bottom:12px;">💪 Strengths</div>""",
                unsafe_allow_html=True,
            )
            for s in strengths:
                st.markdown(f"✅ {s}")
            st.markdown("</div>", unsafe_allow_html=True)

        with sw_col2:
            weaknesses = result.get("weaknesses", [])
            st.markdown(
                """<div class="studio-card" style="border-left:4px solid #ef4444;">
                    <div style="font-size:15px; font-weight:700; color:#991b1b; margin-bottom:12px;">⚠️ Gaps & Weaknesses</div>""",
                unsafe_allow_html=True,
            )
            for w in weaknesses:
                st.markdown(f"🔸 {w}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Section Feedback
        st.markdown("#### 📝 Section-by-Section Feedback")
        section_fb = result.get("section_feedback", {})
        if section_fb:
            tabs = st.tabs(["Summary", "Experience", "Skills", "Education", "Formatting"])
            keys = ["summary", "experience", "skills", "education", "formatting"]
            for tab, key in zip(tabs, keys):
                with tab:
                    fb_text = section_fb.get(key, "No feedback available.")
                    st.markdown(
                        f"""<div class="studio-card">{fb_text}</div>""",
                        unsafe_allow_html=True,
                    )

        # Recommendations
        recs = result.get("recommendations", [])
        if recs:
            st.markdown("#### 🎯 Action Recommendations")
            st.markdown(
                """<div class="studio-card" style="border-left:4px solid #6366f1;">
                    <div style="font-size:15px; font-weight:700; color:#4338ca; margin-bottom:12px;">📋 What to fix</div>""",
                unsafe_allow_html=True,
            )
            for i, rec in enumerate(recs, 1):
                st.markdown(f"**{i}.** {rec}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Overall Verdict
        verdict_text = result.get("overall_verdict", "")
        if verdict_text:
            st.markdown("#### 🏆 Overall Verdict")
            st.info(verdict_text)

        # Quick Nav to Optimizer
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ Optimize My Resume Now →", type="primary"):
            st.session_state.current_page = "✨ Resume Optimizer"
            st.rerun()
