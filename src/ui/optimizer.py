"""
ATS Resume Studio - Resume Optimizer Page
"""

import streamlit as st
from src.core.llm import optimize_resume
from src.utils.file_parser import extract_text_from_file, clean_text
from src.utils.exporters import text_to_docx_bytes, create_download_filename


def render_optimizer():
    st.markdown(
        """
        <div class="section-title">✨ Resume Optimizer</div>
        <div class="section-subtitle">AI rewrites your resume to maximize ATS compatibility for a specific job.</div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.api_key_verified:
        st.warning("🔑 Please connect your OpenAI API key in the sidebar.")
        return

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("#### 📄 Your Current Resume")
        upload_tab, paste_tab = st.tabs(["📁 Upload", "📝 Paste"])

        with upload_tab:
            uploaded = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx", "txt"],
                key="optimizer_upload",
                label_visibility="collapsed",
            )
            if uploaded:
                text, err = extract_text_from_file(uploaded)
                if err:
                    st.error(err)
                else:
                    st.session_state.resume_text = clean_text(text)
                    st.success(f"✅ {uploaded.name} loaded.")

        with paste_tab:
            resume_input = st.text_area(
                "Resume",
                value=st.session_state.resume_text,
                height=300,
                placeholder="Paste your resume text here...",
                label_visibility="collapsed",
                key="opt_resume_text",
            )
            if resume_input != st.session_state.resume_text:
                st.session_state.resume_text = resume_input

    with col_right:
        st.markdown("#### 🏢 Target Job Description")
        jd = st.text_area(
            "Job Description",
            value=st.session_state.job_description,
            height=340,
            placeholder="Paste the job description you're targeting...",
            label_visibility="collapsed",
            key="opt_jd_text",
        )
        st.session_state.job_description = jd

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn, _ = st.columns([2, 4])
    with col_btn:
        optimize_clicked = st.button(
            "✨ Optimize Resume",
            type="primary",
            use_container_width=True,
            disabled=(not st.session_state.resume_text or not st.session_state.job_description),
        )

    if optimize_clicked:
        with st.spinner("🤖 Rewriting your resume for maximum ATS impact..."):
            try:
                optimized = optimize_resume(
                    st.session_state.api_key,
                    st.session_state.api_provider,
                    st.session_state.model,
                    st.session_state.resume_text,
                    st.session_state.job_description,
                )
                st.session_state.optimized_resume = optimized
                st.success("✅ Resume optimized!")
            except Exception as e:
                st.error(f"Optimization failed: {str(e)}")
                return

    if st.session_state.optimized_resume:
        st.markdown("---")
        st.markdown("### 🎉 Your Optimized Resume")

        col_orig, col_opt = st.columns(2, gap="large")
        with col_orig:
            st.markdown("**📄 Original**")
            st.text_area(
                "original",
                value=st.session_state.resume_text,
                height=400,
                label_visibility="collapsed",
                disabled=True,
            )

        with col_opt:
            st.markdown("**✨ Optimized (ATS-Ready)**")
            optimized_editable = st.text_area(
                "optimized",
                value=st.session_state.optimized_resume,
                height=400,
                label_visibility="collapsed",
            )
            if optimized_editable != st.session_state.optimized_resume:
                st.session_state.optimized_resume = optimized_editable

        # Downloads
        st.markdown("#### ⬇️ Download Your Optimized Resume")
        dl_col1, dl_col2, dl_col3 = st.columns(3)

        with dl_col1:
            st.download_button(
                "📄 Download as TXT",
                data=st.session_state.optimized_resume.encode("utf-8"),
                file_name=create_download_filename("optimized_resume", "txt"),
                mime="text/plain",
                use_container_width=True,
            )

        with dl_col2:
            try:
                docx_bytes = text_to_docx_bytes(st.session_state.optimized_resume, "Optimized Resume")
                st.download_button(
                    "📝 Download as DOCX",
                    data=docx_bytes,
                    file_name=create_download_filename("optimized_resume", "docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception:
                st.info("Install python-docx for DOCX export.")

        with dl_col3:
            if st.button("🔍 Run ATS Analysis →", use_container_width=True):
                st.session_state.resume_text = st.session_state.optimized_resume
                st.session_state.current_page = "🔍 ATS Analyzer"
                st.rerun()
