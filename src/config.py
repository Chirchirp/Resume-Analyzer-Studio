"""ATS Resume Studio v3 - Configuration"""
import streamlit as st


def configure_page():
    st.set_page_config(
        page_title="ATS Resume Studio",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": "# ATS Resume Studio v3\nToken-smart AI resume coaching.",
        },
    )
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html,body,[class*="css"]{font-family:'Inter',sans-serif;color:#0f172a!important}
    p,span,div,label,h1,h2,h3,h4,h5,h6{color:#0f172a!important}
    #MainMenu,footer,header{visibility:hidden}
    [data-testid="stSidebar"]{background:linear-gradient(180deg,#0f172a 0%,#1e293b 100%);border-right:1px solid #334155}
    [data-testid="stSidebar"] *{color:#e2e8f0!important}
    .studio-card{background:white;border-radius:12px;padding:24px;
        box-shadow:0 1px 3px rgba(0,0,0,0.08),0 4px 16px rgba(0,0,0,0.04);
        border:1px solid #f1f5f9;margin-bottom:20px}
    .score-badge{display:inline-flex;align-items:center;justify-content:center;
        width:80px;height:80px;border-radius:50%;font-size:22px;font-weight:700;color:white}
    .score-high{background:linear-gradient(135deg,#10b981,#059669)}
    .score-medium{background:linear-gradient(135deg,#f59e0b,#d97706)}
    .score-low{background:linear-gradient(135deg,#ef4444,#dc2626)}
    .tag-found{display:inline-block;background:#dcfce7;color:#166534;border:1px solid #bbf7d0;
        border-radius:20px;padding:3px 12px;font-size:13px;margin:3px;font-weight:500}
    .tag-missing{display:inline-block;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;
        border-radius:20px;padding:3px 12px;font-size:13px;margin:3px;font-weight:500}
    .section-title{font-size:22px;font-weight:700;color:#0f172a;margin-bottom:4px}
    .section-subtitle{font-size:14px;color:#64748b;margin-bottom:24px}
    .hero-banner{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:16px;
        padding:48px 40px;color:white;text-align:center;margin-bottom:32px}
    .hero-banner h1{font-size:42px;font-weight:800;margin-bottom:12px;color:white!important}
    .hero-banner p{font-size:18px;opacity:0.9;color:white!important}
    .metric-card{background:linear-gradient(135deg,#f8fafc,#f1f5f9);border-radius:12px;
        padding:20px;text-align:center;border:1px solid #e2e8f0}
    .metric-value{font-size:32px;font-weight:800;color:#6366f1}
    .metric-label{font-size:13px;color:#64748b;font-weight:500;text-transform:uppercase;letter-spacing:0.5px}
    .feature-card{background:white;border-radius:12px;padding:28px 24px;border:2px solid #e2e8f0;
        text-align:center;transition:all 0.2s ease;cursor:pointer;height:100%}
    .feature-card:hover{border-color:#6366f1;box-shadow:0 8px 24px rgba(99,102,241,0.12);transform:translateY(-2px)}
    .feature-icon{font-size:36px;margin-bottom:12px}
    .feature-title{font-size:17px;font-weight:700;color:#0f172a;margin-bottom:8px}
    .feature-desc{font-size:14px;color:#64748b;line-height:1.6}
    .stButton>button{border-radius:8px;font-weight:600;transition:all 0.2s ease}
    .stProgress>div>div{border-radius:8px}
    .stTabs [data-baseweb="tab-list"]{gap:8px}
    .stTabs [data-baseweb="tab"]{border-radius:8px;font-weight:500}
    textarea{border-radius:8px!important;font-family:'Inter',sans-serif!important}
    hr{border-color:#e2e8f0;margin:24px 0}
    </style>""", unsafe_allow_html=True)


def init_session_state():
    defaults = {
        "api_provider": "groq",
        "api_key": "",
        "model": "llama-3.3-70b-versatile",
        "current_page": "🏠 Home",
        "resume_text": "",
        "job_description": "",
        "analysis_result": None,
        "optimized_resume": "",
        "cover_letter": "",
        "interview_qa": [],
        "built_resume": {},
        "api_key_verified": False,
        # Practice coach
        "practice_state": "idle",
        "practice_question": {},
        "practice_history": [],
        "practice_score_total": 0,
        "practice_count": 0,
        "practice_asked": [],
        # Cool features
        "match_result": None,
        "shortlist_result": None,
        "custom_qa_history": [],
        "interview_chat_history": [],
        "temp_chat": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
