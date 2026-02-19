"""
ATS Resume Studio v3 - Cool Features
Tab 1: Percentage Match
Tab 2: Shortlist Accelerator (top-10 gap analysis)
Tab 3: Custom Query
"""
import streamlit as st
from src.core.llm import call_llm, get_percentage_match, get_shortlist_accelerator
from src.utils.file_parser import extract_text_from_file, clean_text


def _require_api():
    if not st.session_state.api_key_verified:
        st.warning("🔑 Connect an API provider in the sidebar.")
        return False
    return True


def _input_row(prefix):
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**📄 Resume**")
        u, p = st.tabs(["📁 Upload", "📝 Paste"])
        with u:
            f = st.file_uploader("Resume", type=["pdf","docx","txt"],
                                 key=f"{prefix}_up", label_visibility="collapsed")
            if f:
                t, e = extract_text_from_file(f)
                if e: st.error(e)
                else:
                    st.session_state.resume_text = clean_text(t)
                    st.success(f"✅ {f.name}")
        with p:
            r = st.text_area("Resume", value=st.session_state.resume_text, height=200,
                             placeholder="Paste resume…", label_visibility="collapsed",
                             key=f"{prefix}_rp")
            st.session_state.resume_text = r
    with c2:
        st.markdown("**🏢 Job Description**")
        j = st.text_area("JD", value=st.session_state.job_description, height=230,
                         placeholder="Paste job description…", label_visibility="collapsed",
                         key=f"{prefix}_jd")
        st.session_state.job_description = j


def render_cool_features():
    st.markdown('<div class="section-title">🚀 Advanced Tools</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Precision tools to maximise your shortlist chances.</div>', unsafe_allow_html=True)

    if not _require_api():
        return

    for k in ["match_result","shortlist_result","custom_qa"]:
        if k not in st.session_state:
            st.session_state[k] = None

    tab1, tab2, tab3 = st.tabs(["🎯 Match %", "🏆 Shortlist Accelerator", "💬 Custom Query"])

    # ═══════════════════════════════════════════════════════════════
    # TAB 1 — PERCENTAGE MATCH
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🎯 Role Match Percentage")
        st.info("Get a scored breakdown of how well your resume matches the JD across 5 weighted dimensions.")
        _input_row("match")

        if st.button("🎯 Calculate Match", type="primary", use_container_width=True,
                     disabled=not (st.session_state.resume_text and st.session_state.job_description)):
            with st.spinner("Calculating match…"):
                try:
                    result = get_percentage_match(
                        st.session_state.api_key, st.session_state.api_provider,
                        st.session_state.model, st.session_state.resume_text,
                        st.session_state.job_description)
                    st.session_state.match_result = result
                except Exception as e:
                    st.error(f"Failed: {e}")

        if st.session_state.match_result:
            st.markdown("---")
            st.markdown(f"""
            <div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:20px'>
                <pre style='font-size:14px;color:#1e293b;white-space:pre-wrap;margin:0;font-family:Inter,sans-serif'>
{st.session_state.match_result}
                </pre>
            </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # TAB 2 — SHORTLIST ACCELERATOR
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🏆 Top-10 Shortlist Accelerator")
        st.info(
            "Surgical gap analysis that tells you EXACTLY what to fix to break into the "
            "top 10 shortlisted candidates. Ranked by severity and impact."
        )
        _input_row("sl")

        if st.button("⚡ Run Shortlist Analysis", type="primary", use_container_width=True,
                     disabled=not (st.session_state.resume_text and st.session_state.job_description)):
            with st.spinner("Analysing your shortlist position…"):
                try:
                    result = get_shortlist_accelerator(
                        st.session_state.api_key, st.session_state.api_provider,
                        st.session_state.model, st.session_state.resume_text,
                        st.session_state.job_description)
                    st.session_state.shortlist_result = result
                except Exception as e:
                    st.error(f"Failed: {e}")

        if st.session_state.shortlist_result:
            r = st.session_state.shortlist_result
            prob = r.get("shortlist_probability", 0)
            tier = r.get("tier","")
            pc = "#10b981" if prob>=70 else "#f59e0b" if prob>=45 else "#ef4444"

            st.markdown("---")

            # Probability meter
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{pc}18,{pc}06);border:2px solid {pc}40;
                        border-radius:16px;padding:24px;text-align:center;margin-bottom:20px'>
                <div style='font-size:56px;font-weight:900;color:{pc}'>{prob}%</div>
                <div style='font-size:16px;font-weight:700;color:{pc};margin-bottom:6px'>{tier}</div>
                <div style='color:#64748b;font-size:14px;max-width:500px;margin:0 auto;line-height:1.6'>
                    {r.get("executive_summary","")}
                </div>
            </div>""", unsafe_allow_html=True)

            # Critical gaps
            gaps = r.get("critical_gaps", [])
            if gaps:
                st.markdown("#### 🎯 Critical Gaps")
                for g in gaps:
                    sev = g.get("severity","Minor")
                    sc = "#ef4444" if sev=="Knockout" else "#f59e0b" if sev=="Major" else "#94a3b8"
                    icon = "🔴" if sev=="Knockout" else "🟡" if sev=="Major" else "🟢"
                    with st.expander(f"{icon} {g.get('gap','')} — {sev}"):
                        st.markdown(f"""
                        <div style='background:#fff;border-left:3px solid {sc};border-radius:0 8px 8px 0;padding:12px 16px'>
                            <div style='font-size:13px;color:#334155;margin-bottom:8px'>{g.get('gap','')}</div>
                            <div style='font-size:13px'><b>Fix:</b> {g.get('fix','')}</div>
                            <div style='font-size:12px;color:#64748b;margin-top:4px'>⏱️ {g.get('time','')}</div>
                        </div>""", unsafe_allow_html=True)

            # Accelerators
            accs = sorted(r.get("accelerators",[]), key=lambda x: x.get("priority",99))
            if accs:
                st.markdown("#### ⚡ Shortlist Accelerators")
                for a in accs:
                    p = a.get("priority",5)
                    pc2 = "#6366f1" if p<=2 else "#0891b2" if p<=3 else "#64748b"
                    with st.expander(f"P{p} — {a.get('action','')}"):
                        st.markdown(f"""
                        <div style='background:#f8fafc;border-radius:8px;padding:12px'>
                            <b>Impact:</b> {a.get('impact','')}
                        </div>""", unsafe_allow_html=True)

            # Keywords
            kws = r.get("keyword_adds",[])
            if kws:
                st.markdown("#### 🔑 Keywords to Add")
                pills = " ".join(f"""<span style='display:inline-block;background:#fee2e2;color:#991b1b;
                    border:1px solid #fecaca;border-radius:20px;padding:3px 12px;font-size:13px;margin:3px'>
                    ✗ {k}</span>""" for k in kws)
                st.markdown(pills, unsafe_allow_html=True)

            # Differentiator
            if r.get("differentiator"):
                st.markdown(f"""
                <div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px;margin-top:12px'>
                    🌟 <b>Your Differentiator:</b> {r['differentiator']}
                </div>""", unsafe_allow_html=True)

            # If I were you
            if r.get("if_i_were_you"):
                st.markdown(f"""
                <div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:14px;margin-top:8px'>
                    💡 <b>If I were you:</b> {r['if_i_were_you']}
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════
    # TAB 3 — CUSTOM QUERY
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 💬 Custom Question")
        st.info("Ask anything specific about your resume, the job, or your fit. The AI has context of both.")
        _input_row("cq")

        if "custom_qa_history" not in st.session_state:
            st.session_state.custom_qa_history = []

        query = st.text_area("Your question", height=80,
                             placeholder="e.g. What specific experience am I missing for the senior requirements?",
                             label_visibility="collapsed", key="cq_input")

        if st.button("💬 Ask", type="primary", disabled=not (query.strip() and st.session_state.resume_text and st.session_state.job_description)):
            with st.spinner("Thinking…"):
                try:
                    prompt = (f"Answer this specific question about the candidate's fit for the role.\n\n"
                              f"Question: {query}\n\n"
                              f"RESUME:\n{st.session_state.resume_text[:2500]}\n\n"
                              f"JOB:\n{st.session_state.job_description[:1500]}\n\nAnswer:")
                    reply = call_llm(st.session_state.api_key, st.session_state.api_provider,
                                     st.session_state.model, prompt, temperature=0.4, max_tokens=600)
                    st.session_state.custom_qa_history.append({"q": query, "a": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

        for item in reversed(st.session_state.custom_qa_history):
            st.markdown(f"""
            <div style='background:#e0e7ff;border-left:3px solid #6366f1;border-radius:0 10px 10px 0;
                        padding:10px 14px;margin-bottom:8px;font-size:14px;color:#1e293b'>
                <b>Q:</b> {item['q']}</div>
            <div style='background:#f0fdf4;border-left:3px solid #10b981;border-radius:0 10px 10px 0;
                        padding:12px 16px;margin-bottom:16px;font-size:14px;color:#1e293b;line-height:1.7'>
                <b>A:</b> {item['a']}</div>""", unsafe_allow_html=True)

        if st.session_state.custom_qa_history:
            if st.button("🗑️ Clear History"):
                st.session_state.custom_qa_history = []
                st.rerun()
