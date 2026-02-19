"""
ATS Resume Studio - Cover Letter Generator Page
"""

import streamlit as st
from src.core.llm import generate_cover_letter
from src.utils.file_parser import extract_text_from_file, clean_text
from src.utils.exporters import text_to_docx_bytes, create_download_filename


def render_cover_letter():
    st.markdown(
        """
        <div class="section-title">✉️ Cover Letter Generator</div>
        <div class="section-subtitle">Generate a tailored, compelling cover letter that complements your optimized resume.</div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.api_key_verified:
        st.warning("🔑 Please connect your OpenAI API key in the sidebar.")
        return

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("#### 📄 Resume")
        upload_tab, paste_tab = st.tabs(["📁 Upload", "📝 Paste"])

        with upload_tab:
            uploaded = st.file_uploader(
                "Upload Resume", type=["pdf", "docx", "txt"],
                key="cl_upload", label_visibility="collapsed",
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
                "Resume", value=st.session_state.resume_text, height=220,
                placeholder="Paste your resume...", label_visibility="collapsed",
            )
            st.session_state.resume_text = resume_input

        st.markdown("#### 🏢 Job Description")
        jd = st.text_area(
            "Job Description", value=st.session_state.job_description, height=220,
            placeholder="Paste the job description...", label_visibility="collapsed",
        )
        st.session_state.job_description = jd

    with col_right:
        st.markdown("#### ⚙️ Customization")

        tone = st.selectbox(
            "Writing Tone",
            ["Professional", "Enthusiastic", "Confident", "Conversational", "Formal"],
            help="Choose the tone that best matches the company culture.",
        )

        extra_notes = st.text_area(
            "Personal Notes (Optional)",
            height=120,
            placeholder="E.g., 'Mention I was referred by John Smith', 'Highlight my startup experience', 'I'm relocating to NYC'...",
            help="Any specific points you want included in the letter.",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="studio-card" style="background:#f8fafc;">
                <div style="font-size:13px; font-weight:700; color:#475569; margin-bottom:8px;">✨ What makes this great:</div>
                <div style="font-size:13px; color:#64748b;">
                • Tailored to the specific job<br>
                • Uses your actual experience<br>
                • Avoids generic filler phrases<br>
                • ATS keyword optimized<br>
                • Under 400 words — perfect length
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        generate_clicked = st.button(
            "✉️ Generate Cover Letter",
            type="primary",
            use_container_width=True,
            disabled=(not st.session_state.resume_text or not st.session_state.job_description),
        )

    if generate_clicked:
        with st.spinner("✍️ Writing your tailored cover letter..."):
            try:
                letter = generate_cover_letter(
                    st.session_state.api_key,
                    st.session_state.api_provider,
                    st.session_state.model,
                    st.session_state.resume_text,
                    st.session_state.job_description,
                    tone=tone,
                    extra_notes=extra_notes,
                )
                st.session_state.cover_letter = letter
                st.success("✅ Cover letter generated!")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                return

    if st.session_state.cover_letter:
        st.markdown("---")
        st.markdown("### 📬 Your Cover Letter")

        editable_letter = st.text_area(
            "cover_letter_output",
            value=st.session_state.cover_letter,
            height=450,
            label_visibility="collapsed",
        )
        if editable_letter != st.session_state.cover_letter:
            st.session_state.cover_letter = editable_letter

        word_count = len(st.session_state.cover_letter.split())
        st.caption(f"Word count: {word_count} words")

        st.markdown("#### ⬇️ Download Cover Letter")
        dl1, dl2, dl3 = st.columns(3)

        with dl1:
            st.download_button(
                "📄 Download TXT",
                data=st.session_state.cover_letter.encode("utf-8"),
                file_name=create_download_filename("cover_letter", "txt"),
                mime="text/plain",
                use_container_width=True,
            )

        with dl2:
            try:
                docx_bytes = text_to_docx_bytes(st.session_state.cover_letter, "Cover Letter")
                st.download_button(
                    "📝 Download DOCX",
                    data=docx_bytes,
                    file_name=create_download_filename("cover_letter", "docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception:
                st.info("Install python-docx for DOCX export.")

        with dl3:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.cover_letter = ""
                st.rerun()
