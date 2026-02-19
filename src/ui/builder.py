"""
ATS Resume Studio - Resume Builder Page
Build a resume from scratch using an interactive form.
"""

import streamlit as st
from src.core.llm import build_resume_from_info
from src.utils.exporters import text_to_docx_bytes, create_download_filename


def render_builder():
    st.markdown(
        """
        <div class="section-title">🏗️ Resume Builder</div>
        <div class="section-subtitle">Fill in your details and let AI build a polished, ATS-optimized resume from scratch.</div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.api_key_verified:
        st.warning("🔑 Please connect your OpenAI API key in the sidebar.")
        return

    tab_personal, tab_exp, tab_edu, tab_skills, tab_extra = st.tabs([
        "👤 Personal", "💼 Experience", "🎓 Education", "⚙️ Skills", "➕ Extras"
    ])

    user_info = st.session_state.get("built_resume", {})

    # ── Personal Info ──────────────────────────────────────────────
    with tab_personal:
        st.markdown("#### Personal Information")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            full_name = st.text_input("Full Name *", value=user_info.get("full_name", ""), placeholder="Jane Smith")
            email = st.text_input("Email *", value=user_info.get("email", ""), placeholder="jane@email.com")
            phone = st.text_input("Phone", value=user_info.get("phone", ""), placeholder="+1 (555) 000-0000")
        with p_col2:
            location = st.text_input("Location", value=user_info.get("location", ""), placeholder="New York, NY")
            linkedin = st.text_input("LinkedIn URL", value=user_info.get("linkedin", ""), placeholder="linkedin.com/in/janesmith")
            portfolio = st.text_input("Portfolio/GitHub", value=user_info.get("portfolio", ""), placeholder="github.com/janesmith")

        target_role = st.text_input("Target Job Title *", value=user_info.get("target_role", ""), placeholder="Senior Software Engineer")
        summary = st.text_area(
            "Professional Summary (optional — AI will generate if left blank)",
            value=user_info.get("summary", ""),
            height=100,
            placeholder="Brief overview of your background and key strengths...",
        )

        user_info.update({
            "full_name": full_name, "email": email, "phone": phone,
            "location": location, "linkedin": linkedin, "portfolio": portfolio,
            "target_role": target_role, "summary": summary,
        })

    # ── Work Experience ────────────────────────────────────────────
    with tab_exp:
        st.markdown("#### Work Experience")
        st.info("Add up to 4 positions. Focus on achievements, not just duties.")

        experiences = user_info.get("experiences", [{}] * 3)
        if len(experiences) < 4:
            experiences = experiences + [{}] * (4 - len(experiences))

        updated_exp = []
        for i in range(4):
            with st.expander(f"Position {i + 1}", expanded=(i == 0)):
                e = experiences[i] if i < len(experiences) else {}
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    title = st.text_input("Job Title", value=e.get("title", ""), key=f"exp_title_{i}", placeholder="Software Engineer")
                    company = st.text_input("Company", value=e.get("company", ""), key=f"exp_company_{i}", placeholder="Acme Corp")
                with e_col2:
                    start = st.text_input("Start Date", value=e.get("start", ""), key=f"exp_start_{i}", placeholder="Jan 2021")
                    end = st.text_input("End Date", value=e.get("end", ""), key=f"exp_end_{i}", placeholder="Present")

                achievements = st.text_area(
                    "Key Achievements / Responsibilities",
                    value=e.get("achievements", ""),
                    key=f"exp_ach_{i}",
                    height=100,
                    placeholder="• Led a team of 5 engineers to deliver...\n• Increased system performance by 40%...\n• Built REST APIs serving 1M+ requests/day...",
                )
                updated_exp.append({
                    "title": title, "company": company,
                    "start": start, "end": end, "achievements": achievements,
                })

        # Filter out empty entries
        user_info["experiences"] = [e for e in updated_exp if e.get("title") or e.get("company")]

    # ── Education ─────────────────────────────────────────────────
    with tab_edu:
        st.markdown("#### Education")
        educations = user_info.get("educations", [{}, {}])
        if len(educations) < 2:
            educations += [{}] * (2 - len(educations))

        updated_edu = []
        for i in range(2):
            with st.expander(f"Degree {i + 1}", expanded=(i == 0)):
                e = educations[i] if i < len(educations) else {}
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    degree = st.text_input("Degree", value=e.get("degree", ""), key=f"edu_deg_{i}", placeholder="B.S. Computer Science")
                    institution = st.text_input("Institution", value=e.get("institution", ""), key=f"edu_inst_{i}", placeholder="State University")
                with d_col2:
                    grad_year = st.text_input("Graduation Year", value=e.get("grad_year", ""), key=f"edu_year_{i}", placeholder="2020")
                    gpa = st.text_input("GPA (optional)", value=e.get("gpa", ""), key=f"edu_gpa_{i}", placeholder="3.8/4.0")

                honors = st.text_input("Honors / Activities", value=e.get("honors", ""), key=f"edu_hon_{i}", placeholder="Magna Cum Laude, Dean's List")
                updated_edu.append({
                    "degree": degree, "institution": institution,
                    "grad_year": grad_year, "gpa": gpa, "honors": honors,
                })

        user_info["educations"] = [e for e in updated_edu if e.get("degree") or e.get("institution")]

    # ── Skills ────────────────────────────────────────────────────
    with tab_skills:
        st.markdown("#### Skills")

        s_col1, s_col2 = st.columns(2)
        with s_col1:
            tech_skills = st.text_area(
                "Technical Skills",
                value=user_info.get("tech_skills", ""),
                height=150,
                placeholder="Python, JavaScript, React, Node.js, PostgreSQL, Docker, AWS, Git...",
            )
            certifications = st.text_area(
                "Certifications",
                value=user_info.get("certifications", ""),
                height=100,
                placeholder="AWS Certified Solutions Architect (2023)\nGoogle Cloud Professional (2022)...",
            )
        with s_col2:
            soft_skills = st.text_area(
                "Soft Skills",
                value=user_info.get("soft_skills", ""),
                height=150,
                placeholder="Leadership, Project Management, Cross-functional Collaboration, Communication...",
            )
            languages = st.text_area(
                "Languages",
                value=user_info.get("languages", ""),
                height=100,
                placeholder="English (Native), Spanish (Fluent), Mandarin (Basic)...",
            )

        user_info.update({
            "tech_skills": tech_skills, "soft_skills": soft_skills,
            "certifications": certifications, "languages": languages,
        })

    # ── Extras ────────────────────────────────────────────────────
    with tab_extra:
        st.markdown("#### Additional Sections")

        e_col1, e_col2 = st.columns(2)
        with e_col1:
            projects = st.text_area(
                "Projects (optional)",
                value=user_info.get("projects", ""),
                height=150,
                placeholder="Project Name — Brief description and tech stack used...\nLink: github.com/...",
            )
        with e_col2:
            awards = st.text_area(
                "Awards & Achievements (optional)",
                value=user_info.get("awards", ""),
                height=150,
                placeholder="Employee of the Year 2022 — Acme Corp\nHackathon Winner — TechFest 2021...",
            )

        volunteer = st.text_area(
            "Volunteer / Community Work (optional)",
            value=user_info.get("volunteer", ""),
            height=100,
            placeholder="Mentor, Code.org (2021–Present) — Teaching coding to high school students",
        )

        user_info.update({"projects": projects, "awards": awards, "volunteer": volunteer})

    # Save to session state
    st.session_state.built_resume = user_info

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    col_build, col_clear, _ = st.columns([2, 1, 3])
    with col_build:
        build_clicked = st.button(
            "🏗️ Build My Resume",
            type="primary",
            use_container_width=True,
            disabled=not (user_info.get("full_name") and user_info.get("target_role")),
        )
    with col_clear:
        if st.button("🗑️ Clear Form", use_container_width=True):
            st.session_state.built_resume = {}
            st.session_state.resume_text = ""
            st.rerun()

    if build_clicked:
        with st.spinner("🤖 Building your professional resume..."):
            try:
                built = build_resume_from_info(
                    st.session_state.api_key,
                    st.session_state.api_provider,
                    st.session_state.model,
                    user_info,
                )
                st.session_state.resume_text = built
                st.success("✅ Resume built successfully!")
            except Exception as e:
                st.error(f"Build failed: {str(e)}")
                return

    if st.session_state.resume_text and "built" in dir():
        st.markdown("### 📄 Your Generated Resume")
        editable = st.text_area(
            "generated_resume",
            value=st.session_state.resume_text,
            height=500,
            label_visibility="collapsed",
        )
        st.session_state.resume_text = editable

        st.markdown("#### ⬇️ Download")
        dl1, dl2, dl3, dl4 = st.columns(4)

        with dl1:
            st.download_button(
                "📄 TXT",
                data=st.session_state.resume_text.encode("utf-8"),
                file_name=create_download_filename("resume", "txt"),
                mime="text/plain",
                use_container_width=True,
            )

        with dl2:
            try:
                docx_bytes = text_to_docx_bytes(st.session_state.resume_text, user_info.get("full_name", "Resume"))
                st.download_button(
                    "📝 DOCX",
                    data=docx_bytes,
                    file_name=create_download_filename("resume", "docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception:
                st.caption("Install python-docx for DOCX.")

        with dl3:
            if st.button("🔍 Analyze ATS Score →", use_container_width=True):
                st.session_state.current_page = "🔍 ATS Analyzer"
                st.rerun()

        with dl4:
            if st.button("✨ Optimize Further →", use_container_width=True):
                st.session_state.current_page = "✨ Resume Optimizer"
                st.rerun()
