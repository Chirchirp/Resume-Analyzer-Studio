"""
ATS Resume Studio v3 - Interview Prep
Tab 1: Generate Q&A (study guide)
Tab 2: Practice Coach (AI asks → user answers → AI grades with STAR scoring)
Tab 3: Interview Chatbot (open coaching)
"""
import streamlit as st
from src.core.llm import (
    generate_interview_questions,
    generate_practice_question,
    grade_interview_answer,
    get_interview_chatbot_response,
)
from src.utils.file_parser import extract_text_from_file, clean_text

CAT_COLORS = {
    "Behavioral":  "#6366f1",
    "Technical":   "#0891b2",
    "Situational": "#059669",
    "Culture Fit": "#d97706",
}
GRADE_COLORS = {"A":"#10b981","B":"#22c55e","C":"#f59e0b","D":"#f97316","F":"#ef4444"}


def _require_api():
    if not st.session_state.api_key_verified:
        st.warning("🔑 Connect an API provider in the sidebar first.")
        return False
    return True


def _resume_jd_inputs(key_prefix: str):
    """Shared resume + JD input widget."""
    with st.expander("📋 Resume & Job Description", expanded=not st.session_state.resume_text):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Your Resume**")
            up, pa = st.tabs(["📁 Upload", "📝 Paste"])
            with up:
                f = st.file_uploader("Resume", type=["pdf","docx","txt"],
                                     key=f"{key_prefix}_upload", label_visibility="collapsed")
                if f:
                    t, e = extract_text_from_file(f)
                    if e: st.error(e)
                    else:
                        st.session_state.resume_text = clean_text(t)
                        st.success(f"✅ {f.name}")
            with pa:
                r = st.text_area("Resume", value=st.session_state.resume_text, height=150,
                                 placeholder="Paste resume…", label_visibility="collapsed",
                                 key=f"{key_prefix}_resume_paste")
                st.session_state.resume_text = r
        with c2:
            st.markdown("**Job Description**")
            j = st.text_area("JD", value=st.session_state.job_description, height=180,
                             placeholder="Paste job description…", label_visibility="collapsed",
                             key=f"{key_prefix}_jd")
            st.session_state.job_description = j


def render_interview_prep():
    st.markdown('<div class="section-title">🎯 Interview Prep</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Three tools: generate a study guide, practice with live AI coaching, or chat with your coach.</div>', unsafe_allow_html=True)

    if not _require_api():
        return

    # Session defaults
    for k, v in [("interview_qa", []), ("interview_chat_history", []),
                 ("practice_state", "idle"), ("practice_question", {}),
                 ("practice_history", []), ("practice_score_total", 0),
                 ("practice_count", 0), ("practice_asked", [])]:
        if k not in st.session_state:
            st.session_state[k] = v

    tab1, tab2, tab3 = st.tabs(["📝 Study Q&A", "🎤 Practice Coach", "💬 Chatbot"])

    # ═══════════════════════════════════════════════════════════════
    # TAB 1 — GENERATE STUDY Q&A
    # ═══════════════════════════════════════════════════════════════
    with tab1:
        _resume_jd_inputs("t1")

        col_l, col_r = st.columns([3, 2], gap="large")
        with col_l:
            num_q = st.slider("Number of questions", 5, 15, 8, key="t1_nq")
        with col_r:
            focus = st.multiselect("Categories", ["Behavioral","Technical","Situational","Culture Fit"],
                                   default=["Behavioral","Technical","Situational"], key="t1_focus")

        if st.button("🎯 Generate Q&A", type="primary", use_container_width=True,
                     disabled=not (st.session_state.resume_text and st.session_state.job_description)):
            with st.spinner(f"Generating {num_q} questions…"):
                try:
                    qa = generate_interview_questions(
                        st.session_state.api_key, st.session_state.api_provider,
                        st.session_state.model, st.session_state.resume_text,
                        st.session_state.job_description, num_q)
                    if focus:
                        qa = [q for q in qa if q.get("category") in focus] or qa
                    st.session_state.interview_qa = qa
                    st.success(f"✅ {len(qa)} questions ready!")
                except Exception as e:
                    st.error(f"Failed: {e}")

        if st.session_state.interview_qa:
            st.markdown("---")
            from collections import Counter
            cats = Counter(q.get("category","Other") for q in st.session_state.interview_qa)
            cols = st.columns(len(cats))
            for col, (cat, cnt) in zip(cols, cats.items()):
                c = CAT_COLORS.get(cat, "#6366f1")
                with col:
                    st.markdown(f"""
                    <div style='background:{c}15;border:1px solid {c}40;border-radius:8px;
                                padding:10px;text-align:center'>
                        <div style='font-size:20px;font-weight:800;color:{c}'>{cnt}</div>
                        <div style='font-size:12px;color:#475569'>{cat}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            for i, qa in enumerate(st.session_state.interview_qa, 1):
                cat = qa.get("category","General")
                cc = CAT_COLORS.get(cat, "#6366f1")
                with st.expander(f"Q{i}: {qa.get('question','')}", expanded=(i==1)):
                    st.markdown(f"""
                    <span style='background:{cc}20;color:{cc};border:1px solid {cc}40;
                                 border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600'>{cat}</span>
                    """, unsafe_allow_html=True)
                    st.markdown("**🗣️ Model Answer (STAR):**")
                    st.markdown(f"""
                    <div style='background:#f8fafc;border-radius:8px;padding:14px;
                                border-left:3px solid {cc};font-size:14px;color:#1e293b;line-height:1.7'>
                        {qa.get('model_answer','')}
                    </div>""", unsafe_allow_html=True)
                    if qa.get("tip"):
                        st.markdown(f"""
                        <div style='background:#fffbeb;border:1px solid #fde68a;border-radius:8px;
                                    padding:10px 14px;font-size:13px;color:#92400e;margin-top:8px'>
                            💡 <b>Tip:</b> {qa['tip']}
                        </div>""", unsafe_allow_html=True)

            guide = "\n\n".join([
                f"Q{i}: {q.get('question','')}\n[{q.get('category','')}]\n\n"
                f"Model Answer:\n{q.get('model_answer','')}\n\nTip: {q.get('tip','')}\n{'─'*60}"
                for i, q in enumerate(st.session_state.interview_qa, 1)])
            st.download_button("📚 Download Study Guide", guide.encode(), "study_guide.txt", "text/plain")

    # ═══════════════════════════════════════════════════════════════
    # TAB 2 — PRACTICE COACH (AI asks → user answers → AI grades)
    # ═══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🎤 Live Interview Practice")
        st.info(
            "The AI will ask you interview questions one at a time. "
            "You answer in your own words. The AI then grades you using the STAR method "
            "and gives you a score, specific feedback, and a model answer. "
            "Build up your session score!"
        )

        _resume_jd_inputs("t2")

        if not (st.session_state.resume_text and st.session_state.job_description):
            st.warning("⚠️ Add your resume and job description above to start.")
            return

        # ── Controls row ─────────────────────────────────────────
        cc1, cc2, cc3 = st.columns([2, 2, 2])
        with cc1:
            cat_filter = st.selectbox("Question type", ["Any","Behavioral","Technical","Situational","Culture Fit"],
                                      key="practice_cat")
        with cc2:
            if st.session_state.practice_count > 0:
                avg = st.session_state.practice_score_total / st.session_state.practice_count
                grade = "A" if avg>=90 else "B" if avg>=75 else "C" if avg>=60 else "D" if avg>=50 else "F"
                gc = GRADE_COLORS.get(grade,"#6366f1")
                st.markdown(f"""
                <div style='background:{gc}15;border:1px solid {gc}40;border-radius:10px;
                            padding:10px;text-align:center;margin-top:20px'>
                    <div style='font-size:22px;font-weight:800;color:{gc}'>{avg:.0f}/100</div>
                    <div style='font-size:11px;color:#64748b'>SESSION SCORE ({st.session_state.practice_count} Qs)</div>
                </div>""", unsafe_allow_html=True)
        with cc3:
            if st.button("🔄 Reset Session", use_container_width=True, key="reset_practice"):
                for k in ["practice_state","practice_question","practice_history",
                          "practice_score_total","practice_count","practice_asked"]:
                    st.session_state[k] = [] if k in ["practice_history","practice_asked"] else (0 if "total" in k or "count" in k else "idle" if k=="practice_state" else {})
                st.rerun()

        st.markdown("---")

        # ── State machine ─────────────────────────────────────────
        state = st.session_state.practice_state

        # IDLE → ask for first question
        if state == "idle":
            if st.button("🚀 Start Practice Session", type="primary", use_container_width=True):
                with st.spinner("Getting your first question…"):
                    try:
                        q = generate_practice_question(
                            st.session_state.api_key, st.session_state.api_provider,
                            st.session_state.model, st.session_state.resume_text,
                            st.session_state.job_description,
                            st.session_state.practice_asked, cat_filter)
                        st.session_state.practice_question = q
                        st.session_state.practice_state = "answering"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to get question: {e}")

        # ANSWERING — show question, accept answer
        elif state == "answering":
            q = st.session_state.practice_question
            qcat = q.get("category","")
            qcc = CAT_COLORS.get(qcat,"#6366f1")

            # Progress bar
            if st.session_state.practice_count > 0:
                st.progress(min(st.session_state.practice_count / 10, 1.0),
                            f"Question {st.session_state.practice_count + 1} of your session")

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{qcc}18,{qcc}08);border:1.5px solid {qcc}50;
                        border-radius:14px;padding:20px 22px;margin-bottom:16px'>
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
                    <span style='background:{qcc}25;color:{qcc};border-radius:100px;
                                 padding:3px 12px;font-size:12px;font-weight:700'>{qcat}</span>
                    <span style='color:#64748b;font-size:12px'>Question {st.session_state.practice_count + 1}</span>
                </div>
                <div style='font-size:18px;font-weight:700;color:#0f172a;line-height:1.5'>
                    {q.get("question","")}</div>
                <div style='font-size:13px;color:#64748b;margin-top:10px;font-style:italic'>
                    💡 They want to hear: {q.get("what_they_look_for","")}</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("**✍️ Your Answer** — use the STAR method (Situation → Task → Action → Result)")
            user_ans = st.text_area("Your answer", height=180, placeholder="Type your answer here…",
                                    label_visibility="collapsed", key="practice_user_answer")

            ca1, ca2 = st.columns([3, 1])
            with ca1:
                submit = st.button("✅ Submit Answer", type="primary", use_container_width=True,
                                   disabled=not user_ans.strip())
            with ca2:
                skip = st.button("⏭️ Skip", use_container_width=True)

            if submit and user_ans.strip():
                with st.spinner("Grading your answer…"):
                    try:
                        grade_result = grade_interview_answer(
                            st.session_state.api_key, st.session_state.api_provider,
                            st.session_state.model,
                            q.get("question",""), user_ans,
                            st.session_state.resume_text, st.session_state.job_description)
                        st.session_state.practice_history.append({
                            "question": q, "answer": user_ans, "grade": grade_result
                        })
                        st.session_state.practice_asked.append(q.get("question",""))
                        st.session_state.practice_score_total += grade_result.get("score", 0)
                        st.session_state.practice_count += 1
                        st.session_state.practice_state = "graded"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Grading failed: {e}")

            if skip:
                st.session_state.practice_asked.append(q.get("question",""))
                st.session_state.practice_state = "idle"
                st.rerun()

        # GRADED — show results, offer next question
        elif state == "graded":
            if not st.session_state.practice_history:
                st.session_state.practice_state = "idle"
                st.rerun()
                return

            last = st.session_state.practice_history[-1]
            g = last["grade"]
            q = last["question"]
            score = g.get("score", 0)
            grade = g.get("grade", "C")
            gc = GRADE_COLORS.get(grade, "#6366f1")

            # Score hero
            star_bd = g.get("star_breakdown", {})
            star_rows = []
            for slbl, skey in [("S - Situation","situation"),("T - Task","task"),
                                ("A - Action","action"),("R - Result","result")]:
                sval = star_bd.get(skey, 0)
                spct = sval * 4
                star_rows.append(
                    f"<div style='display:flex;justify-content:space-between;margin-bottom:6px'>"
                    f"<span style='font-size:13px;color:#334155'>{slbl}</span>"
                    f"<div style='display:flex;align-items:center;gap:8px'>"
                    f"<div style='width:100px;background:#e2e8f0;border-radius:100px;height:6px'>"
                    f"<div style='width:{spct}%;background:{gc};border-radius:100px;height:6px'></div></div>"
                    f"<span style='font-size:12px;font-weight:700;color:{gc}'>{sval}/25</span>"
                    f"</div></div>"
                )
            star_html_str = "".join(star_rows)
            st.markdown(
                f"<div style='display:flex;gap:16px;align-items:stretch;margin-bottom:16px'>"
                f"<div style='background:{gc}15;border:2px solid {gc}40;border-radius:16px;"
                f"padding:20px;text-align:center;min-width:120px'>"
                f"<div style='font-size:44px;font-weight:900;color:{gc}'>{score}</div>"
                f"<div style='font-size:28px;font-weight:800;color:{gc}'>{grade}</div>"
                f"<div style='font-size:11px;color:#64748b;text-transform:uppercase'>Score</div>"
                f"</div>"
                f"<div style='flex:1;background:#f8fafc;border-radius:16px;padding:16px'>"
                f"<div style='font-size:13px;font-weight:700;color:#475569;margin-bottom:10px'>STAR BREAKDOWN</div>"
                + star_html_str +
                "</div></div>",
                unsafe_allow_html=True
            )
            # Verdict
            st.markdown(f"""
            <div style='background:#f0f9ff;border-left:3px solid #0ea5e9;border-radius:0 10px 10px 0;
                        padding:12px 16px;margin-bottom:12px;color:#0c4a6e;font-size:14px'>
                <b>Verdict:</b> {g.get("verdict","")}
            </div>""", unsafe_allow_html=True)

            col_s, col_i = st.columns(2)
            with col_s:
                st.markdown("**✅ What Worked**")
                for s in g.get("strengths", []):
                    st.markdown(f"""
                    <div style='background:#f0fdf4;border-left:3px solid #10b981;border-radius:0 8px 8px 0;
                                padding:8px 12px;margin-bottom:6px;font-size:13px;color:#14532d'>✓ {s}</div>
                    """, unsafe_allow_html=True)
            with col_i:
                st.markdown("**⚡ Improve**")
                for imp in g.get("improvements", []):
                    st.markdown(f"""
                    <div style='background:#fff7ed;border-left:3px solid #f97316;border-radius:0 8px 8px 0;
                                padding:8px 12px;margin-bottom:6px;font-size:13px;color:#7c2d12'>→ {imp}</div>
                    """, unsafe_allow_html=True)

            with st.expander("📖 See Model Answer"):
                st.markdown(f"""
                <div style='background:#faf5ff;border:1px solid #d8b4fe;border-radius:10px;
                            padding:16px;font-size:14px;color:#3b0764;line-height:1.7'>
                    {g.get("model_answer","")}
                </div>""", unsafe_allow_html=True)

            with st.expander("👀 Your Original Answer"):
                st.markdown(f"""
                <div style='background:#f8fafc;border-radius:8px;padding:12px;
                            font-size:13px;color:#334155;line-height:1.6'>{last['answer']}</div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("➡️ Next Question", type="primary", use_container_width=True):
                    with st.spinner("Getting next question…"):
                        try:
                            nq = generate_practice_question(
                                st.session_state.api_key, st.session_state.api_provider,
                                st.session_state.model, st.session_state.resume_text,
                                st.session_state.job_description,
                                st.session_state.practice_asked, cat_filter)
                            st.session_state.practice_question = nq
                            st.session_state.practice_state = "answering"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
            with cb2:
                if st.button("📊 View Session Summary", use_container_width=True):
                    st.session_state.practice_state = "summary"
                    st.rerun()

        # SUMMARY — show full session results
        elif state == "summary":
            history = st.session_state.practice_history
            if not history:
                st.session_state.practice_state = "idle"
                st.rerun()
                return

            avg = st.session_state.practice_score_total / max(st.session_state.practice_count, 1)
            grade = "A" if avg>=90 else "B" if avg>=75 else "C" if avg>=60 else "D" if avg>=50 else "F"
            gc = GRADE_COLORS.get(grade,"#6366f1")

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{gc}20,{gc}05);border:2px solid {gc}40;
                        border-radius:16px;padding:24px;text-align:center;margin-bottom:20px'>
                <div style='font-size:48px;font-weight:900;color:{gc}'>{avg:.0f}</div>
                <div style='font-size:32px;font-weight:800;color:{gc}'>Grade {grade}</div>
                <div style='color:#64748b;margin-top:6px'>{len(history)} questions answered</div>
            </div>""", unsafe_allow_html=True)

            for i, item in enumerate(history, 1):
                g = item["grade"]
                sc = g.get("score",0)
                gr = g.get("grade","C")
                gcc = GRADE_COLORS.get(gr,"#6366f1")
                with st.expander(f"Q{i}: {item['question'].get('question','')[:60]}… — {sc}/100 ({gr})"):
                    st.markdown(f"**Your answer:** {item['answer'][:300]}…")
                    st.markdown(f"**Verdict:** {g.get('verdict','')}")
                    st.markdown(f"**Model answer:** {g.get('model_answer','')}")

            # Download session report
            report_lines = [f"Interview Practice Report\n{'='*50}",
                           f"Session Score: {avg:.0f}/100 (Grade {grade})",
                           f"Questions Answered: {len(history)}\n"]
            for i, item in enumerate(history, 1):
                g = item["grade"]
                report_lines.append(f"\nQ{i}: {item['question'].get('question','')}")
                report_lines.append(f"Your Answer: {item['answer']}")
                report_lines.append(f"Score: {g.get('score',0)}/100 (Grade {g.get('grade','')})")
                report_lines.append(f"Verdict: {g.get('verdict','')}")
                report_lines.append(f"Model Answer: {g.get('model_answer','')}")
                report_lines.append("─"*50)
            st.download_button("📄 Download Session Report", "\n".join(report_lines).encode(),
                               "practice_report.txt", "text/plain")

            if st.button("🔄 Start New Session", type="primary", use_container_width=True):
                for k in ["practice_history","practice_asked"]:
                    st.session_state[k] = []
                st.session_state.practice_score_total = 0
                st.session_state.practice_count = 0
                st.session_state.practice_state = "idle"
                st.rerun()

    # ═══════════════════════════════════════════════════════════════
    # TAB 3 — CHATBOT
    # ═══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 💬 Interview Coach Chatbot")
        st.info("Ask anything about the role, how to answer questions, or how to position yourself. Your coach knows your resume and the job description.")

        _resume_jd_inputs("t3")

        if not (st.session_state.resume_text and st.session_state.job_description):
            st.warning("⚠️ Provide resume & JD above to start chatting.")
            return

        # Display chat history
        if not st.session_state.interview_chat_history:
            st.markdown("""
            <div style='background:#f0f9ff;border-left:3px solid #0ea5e9;border-radius:0 10px 10px 0;
                        padding:16px 18px;font-size:14px;color:#075985'>
                👋 <b>Hi! I'm your interview coach.</b><br><br>
                I know your resume and the job you're applying for. Ask me anything:<br>
                • "How should I answer 'Tell me about yourself'?"<br>
                • "What are my biggest gaps for this role?"<br>
                • "How do I address my career gap?"<br>
                • "What questions should I ask the interviewer?"
            </div>""", unsafe_allow_html=True)
        else:
            for msg in st.session_state.interview_chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style='background:#e0e7ff;border-left:3px solid #6366f1;border-radius:0 10px 10px 0;
                                padding:12px 16px;margin-bottom:10px'>
                        <div style='font-size:11px;font-weight:700;color:#4338ca;margin-bottom:4px'>🧑 You</div>
                        <div style='font-size:14px;color:#1e293b'>{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:#f0fdf4;border-left:3px solid #10b981;border-radius:0 10px 10px 0;
                                padding:12px 16px;margin-bottom:10px'>
                        <div style='font-size:11px;font-weight:700;color:#065f46;margin-bottom:4px'>🤖 Coach</div>
                        <div style='font-size:14px;color:#1e293b;line-height:1.7'>{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)

        # Quick prompts
        prompts = ["How do I answer 'Tell me about yourself'?",
                   "What are my biggest gaps for this role?",
                   "How do I talk about my biggest weakness?",
                   "What questions should I ask the interviewer?",
                   "How can I explain a career gap?"]
        with st.expander("💡 Quick Start Questions"):
            cols = st.columns(2)
            for idx, p in enumerate(prompts):
                with cols[idx % 2]:
                    if st.button(p[:42]+"…" if len(p)>42 else p, key=f"qp_{idx}", use_container_width=True):
                        st.session_state.temp_chat = p

        user_in = st.text_input("Your question", placeholder="e.g. How should I position my experience for this role?",
                                label_visibility="collapsed",
                                value=st.session_state.get("temp_chat",""),
                                key="chat_input_box")

        cs1, cs2 = st.columns([4, 1])
        with cs1:
            send = st.button("💬 Send", type="primary", use_container_width=True)
        with cs2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.interview_chat_history = []
                st.session_state.temp_chat = ""
                st.rerun()

        if send and user_in.strip():
            st.session_state.interview_chat_history.append({"role":"user","content":user_in})
            with st.spinner("Coach is thinking…"):
                try:
                    reply = get_interview_chatbot_response(
                        st.session_state.api_key, st.session_state.api_provider,
                        st.session_state.model, st.session_state.resume_text,
                        st.session_state.job_description, st.session_state.interview_chat_history)
                    st.session_state.interview_chat_history.append({"role":"assistant","content":reply})
                    st.session_state.temp_chat = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"Chat failed: {e}")
