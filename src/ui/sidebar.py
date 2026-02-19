"""
ATS Resume Studio v3 - Sidebar
Providers: Groq (FREE), OpenAI, Anthropic, OpenRouter, Together AI, Ollama (LOCAL/FREE)
"""
import streamlit as st
from src.core.llm import verify_api_key

PROVIDER_MODELS = {
    "groq": {
        "Llama 3.3 70B (Recommended - FREE)": "llama-3.3-70b-versatile",
        "Llama 3.1 70B": "llama-3.1-70b-versatile",
        "Llama 3.1 8B (Fastest)": "llama-3.1-8b-instant",
        "Mixtral 8x7B": "mixtral-8x7b-32768",
        "Gemma 2 9B": "gemma2-9b-it",
    },
    "openai": {
        "GPT-4o Mini (Budget)": "gpt-4o-mini",
        "GPT-4o (Best)": "gpt-4o",
        "GPT-3.5 Turbo (Economy)": "gpt-3.5-turbo",
    },
    "anthropic": {
        "Claude 3 Haiku (Fastest/Cheapest)": "claude-3-haiku-20240307",
        "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
        "Claude 3 Opus": "claude-3-opus-20240229",
    },
    "openrouter": {
        "Llama 3.3 70B (Free tier)": "meta-llama/llama-3.3-70b-instruct",
        "Mistral 7B (Budget)": "mistralai/mistral-7b-instruct",
        "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
        "GPT-4o Mini": "openai/gpt-4o-mini",
    },
    "together": {
        "Llama 3.3 70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "Mixtral 8x7B": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    },
    "ollama": {
        "Llama 3.2 3B (Fast local)": "llama3.2",
        "Llama 3.1 8B (Balanced)": "llama3.1",
        "Mistral 7B (Good quality)": "mistral",
        "Phi-3 Mini (Lightweight)": "phi3",
        "Gemma 2 9B": "gemma2",
        "DeepSeek R1 7B": "deepseek-r1:7b",
    },
}

HELP_LINKS = {
    "groq":       "https://console.groq.com/keys",
    "openai":     "https://platform.openai.com/api-keys",
    "anthropic":  "https://console.anthropic.com/settings/keys",
    "openrouter": "https://openrouter.ai/keys",
    "together":   "https://api.together.xyz/settings/api-keys",
    "ollama":     "https://ollama.ai/download",
}


def render_sidebar():
    with st.sidebar:
        # Fix: sidebar selectboxes and inputs render with white bg — force dark text so it's readable
        st.markdown("""
        <style>
        /* Selectbox — dropdown button text */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="select"] div {
            color: #f1f5f9 !important;
        }
        /* Dropdown popup list — light background, dark text for readability */
        [data-baseweb="popover"],
        [data-baseweb="popover"] ul,
        [data-baseweb="menu"] {
            background-color: #ffffff !important;
        }
        [data-baseweb="popover"] ul li,
        [data-baseweb="menu"] ul li,
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] [role="option"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        /* Hover state */
        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="menu"] [role="option"]:hover {
            background-color: #e0e7ff !important;
            color: #1e1b4b !important;
        }
        /* Selected / active option */
        [data-baseweb="popover"] [aria-selected="true"],
        [data-baseweb="menu"] [aria-selected="true"],
        [data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background-color: #6366f1 !important;
            color: #ffffff !important;
        }
        /* Text inputs inside sidebar */
        [data-testid="stSidebar"] input {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
            border-color: #334155 !important;
        }
        [data-testid="stSidebar"] input::placeholder {
            color: #64748b !important;
        }
        </style>
        <div style='text-align:center;padding:16px 0 20px'>
            <div style='font-size:40px'>🎯</div>
            <div style='font-size:19px;font-weight:800;color:#e2e8f0;letter-spacing:-0.5px'>ATS Resume Studio</div>
            <div style='font-size:11px;color:#94a3b8;margin-top:3px'>v3 · Token-Smart AI</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Provider ─────────────────────────────────────────────
        st.markdown("<div style='font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>🔑 AI Provider</div>", unsafe_allow_html=True)

        provider_labels = {
            "Groq — FREE ⚡": "groq",
            "Ollama — Local FREE 🖥️": "ollama",
            "OpenAI": "openai",
            "Anthropic (Claude)": "anthropic",
            "OpenRouter": "openrouter",
            "Together AI": "together",
        }
        sel_label = st.selectbox("Provider", list(provider_labels.keys()), label_visibility="collapsed")
        provider = provider_labels[sel_label]

        # Ollama info banner
        if provider == "ollama":
            st.markdown("""
            <div style='background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);
                        border-radius:8px;padding:10px 12px;font-size:12px;color:#34d399;margin-bottom:8px'>
                🖥️ <b>Ollama runs models locally</b><br>
                Zero API cost. Completely private.<br>
                <a href='https://ollama.ai' target='_blank' style='color:#6ee7b7'>Install Ollama →</a>
                then run: <code>ollama pull llama3.1</code>
            </div>""", unsafe_allow_html=True)

        # API Key / Ollama URL input
        placeholder_map = {
            "groq": "gsk_...",
            "openai": "sk-...",
            "anthropic": "sk-ant-...",
            "openrouter": "sk-or-...",
            "together": "...",
            "ollama": "http://localhost:11434 (or leave blank)",
        }
        api_key_input = st.text_input(
            "API Key" if provider != "ollama" else "Ollama URL (optional)",
            value=st.session_state.api_key if st.session_state.get("api_provider") == provider else "",
            type="password" if provider != "ollama" else "default",
            placeholder=placeholder_map.get(provider, ""),
            help="For Ollama, leave blank for http://localhost:11434",
            key=f"key_input_{provider}",
        )

        # Model selection
        models = PROVIDER_MODELS.get(provider, {})
        sel_model_label = st.selectbox("Model", list(models.keys()), label_visibility="collapsed",
                                       help="Select the AI model to use.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Connect", use_container_width=True, type="primary"):
                key_val = api_key_input or ("http://localhost:11434" if provider == "ollama" else "")
                if key_val or provider == "ollama":
                    with st.spinner("Verifying…"):
                        ok, msg = verify_api_key(key_val, provider)
                    if ok:
                        st.session_state.api_key = key_val
                        st.session_state.api_provider = provider
                        st.session_state.model = models[sel_model_label]
                        st.session_state.api_key_verified = True
                        st.success(msg)
                        st.rerun()
                    else:
                        st.session_state.api_key_verified = False
                        st.error(f"❌ {msg}")
                else:
                    st.error("Enter API key first.")
        with col2:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.api_key = ""
                st.session_state.api_key_verified = False
                st.rerun()

        # Status
        if st.session_state.api_key_verified and st.session_state.get("api_provider") == provider:
            pname = sel_label.split("—")[0].strip()
            mname = sel_model_label.split("(")[0].strip()
            st.markdown(f"""
            <div style='background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);
                        border-radius:8px;padding:8px 12px;margin-top:8px'>
                <span style='color:#10b981;font-weight:600;font-size:13px'>
                    ✓ {pname} · {mname}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                        border-radius:8px;padding:8px 12px;margin-top:8px'>
                <span style='color:#f87171;font-size:13px'>⚠ No provider connected</span>
            </div>""", unsafe_allow_html=True)

        if provider in HELP_LINKS:
            link_text = "Install Ollama" if provider == "ollama" else f"Get {sel_label.split('—')[0].strip()} key"
            st.markdown(f"<div style='font-size:11px;color:#94a3b8;text-align:center;margin-top:6px'>"
                        f"<a href='{HELP_LINKS[provider]}' target='_blank' style='color:#6366f1'>{link_text} →</a></div>",
                        unsafe_allow_html=True)

        st.markdown("---")

        # ── Navigation ────────────────────────────────────────────
        st.markdown("<div style='font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px'>Navigation</div>", unsafe_allow_html=True)

        nav_items = [
            ("🏠 Home", "Home & Features"),
            ("🔍 ATS Analyzer", "Score vs job description"),
            ("🏗️ Resume Builder", "Build from scratch"),
            ("✨ Resume Optimizer", "AI rewrite"),
            ("✉️ Cover Letter", "Tailored letters"),
            ("🎯 Interview Prep", "Q&A + Practice Coach"),
            ("🚀 Cool Features", "Match % · Shortlist"),
        ]
        for label, desc in nav_items:
            active = st.session_state.current_page == label
            if st.button(label, key=f"nav_{label}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style='background:rgba(99,102,241,0.1);border-radius:10px;padding:12px;font-size:12px;color:#c7d2fe'>
            <b>💡 Save tokens:</b><br>
            • Groq & Ollama = FREE<br>
            • For OpenRouter: use free Llama tier<br>
            • Shorter resumes = fewer tokens<br>
            • Haiku/8B models are 10x cheaper
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='text-align:center;font-size:11px;color:#475569;margin-top:12px'>ATS Resume Studio v3<br>© 2025</div>", unsafe_allow_html=True)