"""
ATS Resume Studio v3 - Multi-Provider LLM Core
Providers: Groq (FREE), OpenAI, Anthropic, OpenRouter, Together AI, Ollama (LOCAL/FREE)

Token-Efficiency: All prompts lean, max_tokens capped per feature, text truncated before sending.
"""
from __future__ import annotations
import json, re

_RESUME_LIMIT = 3000
_JD_LIMIT     = 2000

def _trim(text: str, limit: int) -> str:
    return text[:limit] + "\n[...truncated]" if len(text) > limit else text

def _extract_json_object(text: str) -> str:
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start_obj, start_arr = text.find("{"), text.find("[")
    if start_obj == -1 and start_arr == -1:
        raise ValueError("No JSON in LLM response.")
    if start_arr == -1 or (start_obj != -1 and start_obj < start_arr):
        start, open_c, close_c = start_obj, "{", "}"
    else:
        start, open_c, close_c = start_arr, "[", "]"
    depth = in_string = escape_next = 0
    in_string = False; escape_next = False
    for i, ch in enumerate(text[start:], start=start):
        if escape_next: escape_next = False; continue
        if ch == "\\" and in_string: escape_next = True; continue
        if ch == '"': in_string = not in_string; continue
        if in_string: continue
        if ch == open_c: depth += 1
        elif ch == close_c:
            depth -= 1
            if depth == 0: return text[start: i + 1]
    return text[start:]

def _safe_json_loads(text: str):
    try:
        return json.loads(_extract_json_object(text))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON parse failed: {exc}\nOutput: {text[:200]}") from exc

# ── Client factory ────────────────────────────────────────────────
def get_client(api_key: str, provider: str):
    from openai import OpenAI
    urls = {
        "groq": "https://api.groq.com/openai/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "together": "https://api.together.xyz/v1",
        "ollama": api_key if api_key.startswith("http") else "http://localhost:11434/v1",
    }
    if provider == "anthropic":
        import anthropic; return anthropic.Anthropic(api_key=api_key)
    key = "ollama" if provider == "ollama" else api_key
    return OpenAI(api_key=key, base_url=urls.get(provider))

def verify_api_key(api_key: str, provider: str) -> tuple[bool, str]:
    try:
        if provider == "ollama":
            c = get_client(api_key, provider); c.models.list()
            return True, "Ollama connected — running locally, zero cost!"
        elif provider == "anthropic":
            import anthropic
            c = anthropic.Anthropic(api_key=api_key)
            c.messages.create(model="claude-3-haiku-20240307", max_tokens=5,
                              messages=[{"role":"user","content":"hi"}])
        else:
            c = get_client(api_key, provider); c.models.list()
        return True, "Connected successfully."
    except Exception as e:
        msg = str(e).lower()
        if "authentication" in msg or "unauthorized" in msg or "invalid" in msg:
            return False, "Invalid API key."
        if "connection" in msg or "timeout" in msg:
            return False, "Connection error — check internet / Ollama running."
        return False, f"Error: {str(e)[:120]}"

# ── Universal call ────────────────────────────────────────────────
def call_llm(api_key, provider, model, prompt,
             system_prompt="", temperature=0.3, max_tokens=1200) -> str:
    if provider == "anthropic":
        import anthropic
        c = anthropic.Anthropic(api_key=api_key)
        r = c.messages.create(model=model, max_tokens=max_tokens, temperature=temperature,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role":"user","content":prompt}])
        return r.content[0].text
    c = get_client(api_key, provider)
    msgs = ([{"role":"system","content":system_prompt}] if system_prompt else [])
    msgs.append({"role":"user","content":prompt})
    r = c.chat.completions.create(model=model, messages=msgs,
                                  temperature=temperature, max_tokens=max_tokens)
    return r.choices[0].message.content.strip()

# ══════════════════════════════════════════════════════════════════
# 1. ATS ANALYSIS  (max 1800 output tokens)
# ══════════════════════════════════════════════════════════════════
_ANA_SYS = "You are a senior recruiter. Return ONLY valid JSON. No markdown, no preamble."
_ANA_PROMPT = """\
Analyze resume vs job description. Return ONLY this JSON:
{"ats_score":<0-100>,
"score_breakdown":{"keyword_match":<0-100>,"format_compatibility":<0-100>,"skills_alignment":<0-100>,"experience_relevance":<0-100>,"education_match":<0-100>},
"matched_keywords":["<up to 10>"],
"missing_keywords":["<up to 10 critical JD keywords absent from resume>"],
"strengths":["<3-5 specific strengths with resume evidence>"],
"weaknesses":["<3-5 specific weaknesses with before/after fix>"],
"recommendations":["<5 ranked actionable rewrites>"],
"section_feedback":{"summary":"<2-3 sentences>","experience":"<2-3 sentences>","skills":"<2 sentences>","education":"<1-2 sentences>","formatting":"<2 sentences>"},
"coffee_chat":"<3-4 sentences honest coaching to candidate>",
"overall_verdict":"<2 sentences Yes/Yes with revisions/Not yet/No + reason>"}
RESUME:
"""

def analyze_resume(api_key, provider, model, resume_text, job_description) -> dict:
    prompt = (_ANA_PROMPT + _trim(resume_text, _RESUME_LIMIT)
              + "\n\nJOB DESCRIPTION:\n" + _trim(job_description, _JD_LIMIT) + "\n\nJSON:")
    raw = call_llm(api_key, provider, model, prompt, system_prompt=_ANA_SYS,
                   temperature=0.3, max_tokens=1800)
    return _safe_json_loads(raw)

# ══════════════════════════════════════════════════════════════════
# 2. RESUME OPTIMIZER  (max 2000 tokens)
# ══════════════════════════════════════════════════════════════════
def optimize_resume(api_key, provider, model, resume_text, job_description) -> str:
    prompt = ("Rewrite this resume for maximum ATS score vs the job below.\n"
              "Rules: integrate JD keywords naturally, action verbs, quantify achievements, "
              "no tables/columns/graphics, keep all sections. Plain text only.\n\n"
              "RESUME:\n" + _trim(resume_text, _RESUME_LIMIT)
              + "\n\nJOB:\n" + _trim(job_description, _JD_LIMIT) + "\n\nOptimized resume:")
    return call_llm(api_key, provider, model, prompt, temperature=0.4, max_tokens=2000)

# ══════════════════════════════════════════════════════════════════
# 3. COVER LETTER  (max 800 tokens)
# ══════════════════════════════════════════════════════════════════
def generate_cover_letter(api_key, provider, model, resume_text,
                          job_description, tone="Professional", extra_notes="") -> str:
    prompt = (f"Write a compelling cover letter (250-320 words). Tone: {tone}.\n"
              f"Notes: {extra_notes or 'None'}.\n"
              "Strong hook, 2 body paragraphs referencing specific achievements, confident close. "
              "No generic filler.\n\nRESUME:\n" + _trim(resume_text, 2000)
              + "\n\nJOB:\n" + _trim(job_description, 1500) + "\n\nCover letter:")
    return call_llm(api_key, provider, model, prompt, temperature=0.6, max_tokens=800)

# ══════════════════════════════════════════════════════════════════
# 4. INTERVIEW QUESTIONS  (max 1500 tokens)
# ══════════════════════════════════════════════════════════════════
_IQ_SYS = "You are a senior hiring manager. Return ONLY a valid JSON array. No markdown."

def generate_interview_questions(api_key, provider, model, resume_text,
                                  job_description, num_questions=8) -> list:
    prompt = (f"Generate {num_questions} interview questions. Return ONLY JSON array:\n"
              '[{"category":"Behavioral|Technical|Situational|Culture Fit",'
              '"question":"<question>","model_answer":"<STAR 3-4 sentences>","tip":"<one tip>"}]\n\n'
              "RESUME:\n" + _trim(resume_text, 2000)
              + "\n\nJOB:\n" + _trim(job_description, 1500) + "\n\nJSON array:")
    raw = call_llm(api_key, provider, model, prompt, system_prompt=_IQ_SYS,
                   temperature=0.5, max_tokens=1500)
    return _safe_json_loads(raw)

# ══════════════════════════════════════════════════════════════════
# 5. COACH CHATBOT  (max 600 tokens per turn)
# ══════════════════════════════════════════════════════════════════
def get_interview_chatbot_response(api_key, provider, model, resume_text,
                                    job_description, chat_history) -> str:
    history_str = ""
    for msg in chat_history[:-1]:
        role = "User" if msg["role"] == "user" else "Coach"
        history_str += f"{role}: {msg['content']}\n\n"
    user_q = chat_history[-1]["content"]
    sys = ("You are an expert interview coach who knows this candidate's resume and the job. "
           "Give specific, direct advice in 2-3 short paragraphs. Reference their actual experience.")
    prompt = ("RESUME:\n" + _trim(resume_text, 1200)
              + "\n\nJOB:\n" + _trim(job_description, 800)
              + "\n\nHISTORY:\n" + history_str
              + "\nUser: " + user_q + "\n\nCoach:")
    return call_llm(api_key, provider, model, prompt, system_prompt=sys,
                    temperature=0.6, max_tokens=600)

# ══════════════════════════════════════════════════════════════════
# 6. PRACTICE MODE — generate question  (max 250 tokens)
# ══════════════════════════════════════════════════════════════════
def generate_practice_question(api_key, provider, model, resume_text,
                                job_description, asked_questions: list,
                                category: str = "Any") -> dict:
    asked_str = "\n".join(f"- {q}" for q in asked_questions[-8:]) or "None yet"
    cat_filter = f"Category: {category}." if category != "Any" else "Mix categories."
    prompt = ("Generate ONE interview question. " + cat_filter
              + " Do NOT repeat these:\n" + asked_str
              + "\n\nReturn ONLY JSON:\n"
              '{"question":"<text>","category":"Behavioral|Technical|Situational|Culture Fit",'
              '"what_they_look_for":"<1-2 sentences>"}'
              + "\n\nRESUME:\n" + _trim(resume_text, 1200)
              + "\n\nJOB:\n" + _trim(job_description, 800) + "\n\nJSON:")
    raw = call_llm(api_key, provider, model, prompt,
                   system_prompt="Return ONLY valid JSON. No markdown.",
                   temperature=0.7, max_tokens=250)
    return _safe_json_loads(raw)

# ══════════════════════════════════════════════════════════════════
# 7. GRADE ANSWER  (max 500 tokens)
# ══════════════════════════════════════════════════════════════════
def grade_interview_answer(api_key, provider, model, question: str,
                            user_answer: str, resume_text: str,
                            job_description: str) -> dict:
    prompt = ('Grade this interview answer. Return ONLY JSON:\n'
              '{"score":<0-100>,"grade":"A|B|C|D|F",'
              '"star_breakdown":{"situation":<0-25>,"task":<0-25>,"action":<0-25>,"result":<0-25>},'
              '"strengths":["<specific strength>","<specific strength>"],'
              '"improvements":["<specific improvement>","<specific improvement>"],'
              '"model_answer":"<strong 3-4 sentence answer using their background>",'
              '"verdict":"<2 sentences honest assessment>"}'
              + "\n\nQUESTION: " + question
              + "\n\nCANDIDATE ANSWER: " + user_answer[:1200]
              + "\n\nRESUME CONTEXT:\n" + _trim(resume_text, 800)
              + "\n\nJOB CONTEXT:\n" + _trim(job_description, 500) + "\n\nJSON:")
    raw = call_llm(api_key, provider, model, prompt,
                   system_prompt="You are a strict but fair interview assessor. Return ONLY valid JSON.",
                   temperature=0.3, max_tokens=500)
    return _safe_json_loads(raw)

# ══════════════════════════════════════════════════════════════════
# 8. SHORTLIST ACCELERATOR  (max 1200 tokens)
# ══════════════════════════════════════════════════════════════════
def get_shortlist_accelerator(api_key, provider, model, resume_text, job_description) -> dict:
    prompt = ('Analyze resume vs JD. Return ONLY JSON:\n'
              '{"shortlist_probability":<0-100>,"tier":"Top 10|Top 25|Reachable|Longshot|Not Competitive",'
              '"executive_summary":"<3 sentences>",'
              '"critical_gaps":[{"gap":"<gap>","severity":"Knockout|Major|Minor","fix":"<exact change>","time":"Today|This Week|Longer"}],'
              '"accelerators":[{"action":"<action>","impact":"<why it helps>","priority":<1-5>}],'
              '"keyword_adds":["<missing keyword>"],'
              '"differentiator":"<1-2 sentences what makes them stand out>",'
              '"if_i_were_you":"<2 sentences direct advice>"}'
              + "\n\nRESUME:\n" + _trim(resume_text, 2500)
              + "\n\nJOB:\n" + _trim(job_description, 1500) + "\n\nJSON:")
    raw = call_llm(api_key, provider, model, prompt,
                   system_prompt="You are a hiring strategy expert. Return ONLY valid JSON.",
                   temperature=0.4, max_tokens=1200)
    return _safe_json_loads(raw)

# ══════════════════════════════════════════════════════════════════
# 9. PERCENTAGE MATCH  (max 600 tokens)
# ══════════════════════════════════════════════════════════════════
def get_percentage_match(api_key, provider, model, resume_text, job_description) -> str:
    prompt = ("Score resume vs JD (0-100): Hard Skills 35%, Experience 25%, "
              "Achievements 20%, Qualifications 15%, Keywords 5%.\n\n"
              "Output:\nATS Match Score: X%\nTop 5 Matched: keyword — context\n"
              "Top 5 Missing: keyword — why\nQuick Win: [one action]\n\n"
              "RESUME:\n" + _trim(resume_text, 2000) + "\n\nJOB:\n" + _trim(job_description, 1500))
    return call_llm(api_key, provider, model, prompt, temperature=0.3, max_tokens=600)

# ══════════════════════════════════════════════════════════════════
# 10. RESUME BUILDER  (max 2000 tokens)
# ══════════════════════════════════════════════════════════════════
def build_resume_from_info(api_key, provider, model, user_info: dict) -> str:
    prompt = ("Build an ATS-optimized resume. Sections: Professional Summary, "
              "Work Experience, Skills, Education. Action verbs, quantify achievements, plain text.\n\n"
              "INFO:\n" + json.dumps(user_info, indent=2) + "\n\nResume:")
    return call_llm(api_key, provider, model, prompt, temperature=0.4, max_tokens=2000)
