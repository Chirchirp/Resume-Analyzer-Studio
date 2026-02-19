# 🎯 ATS Resume Studio v3

**Token-smart AI resume coaching** — built for job seekers who want real impact, not just generic feedback.

---

## 🆕 What's New in v3

### 🎤 Interview Practice Coach (NEW)
The AI asks you interview questions one at a time. You answer in your own words.
The AI then **grades your answer** using STAR method scoring:
- **Score out of 100** with A–F grade
- **STAR breakdown**: Situation/Task/Action/Result each scored out of 25
- **Specific strengths** from your actual answer
- **Specific improvements** with coaching notes
- **Model answer** built from your real background
- **Session score** accumulates across questions
- **Download your session report** as PDF/TXT

### 🏆 Shortlist Accelerator (NEW)
Surgical gap analysis: tells you the **exact probability** you'll be shortlisted (0–100%)
and what to fix to break into the **top 10 candidates**:
- Knockout / Major / Minor gap classification
- Ranked accelerators by priority
- Keywords to add immediately
- Your unique differentiator

### 🖥️ Ollama Local Models (NEW — 100% FREE)
Run AI **entirely on your own machine**. Zero API cost. 100% private. No data leaves your device.
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (pick one)
ollama pull llama3.1        # Recommended — 8B, great quality
ollama pull llama3.2        # Fast 3B model
ollama pull mistral         # Excellent quality
ollama pull phi3            # Lightweight

# In the app: select "Ollama — Local FREE", leave URL blank, click Connect
```

### 💸 Token Efficiency (60–80% fewer tokens)
All prompts have been rewritten to be lean and precise:
- Compact JSON schemas (no verbose field names)
- Resume + JD text truncated before sending (not the whole document)
- Per-feature `max_tokens` caps prevent 402 errors on limited accounts
- No redundant instructions or lengthy examples in prompts

---

## 🚀 Quick Start

### Option A: Groq Cloud (Free)
```bash
pip install -r requirements.txt
streamlit run app.py
# Get free API key: https://console.groq.com/keys
# Select Groq, paste key, select "Llama 3.3 70B", click Connect
```

### Option B: Ollama Local (Free, Private)
```bash
pip install -r requirements.txt
ollama pull llama3.1
streamlit run app.py
# Select "Ollama — Local FREE", leave URL blank, click Connect
```

### Option C: OpenRouter Budget
```bash
# Free tier available at https://openrouter.ai
# Select "Llama 3.3 70B (Free tier)" model — no cost
```

---

## 📁 Project Structure

```
ats_resume_studio/
├── app.py                     # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── config.py              # Page config, CSS, session state
│   ├── core/
│   │   └── llm.py             # All AI functions (token-efficient)
│   ├── ui/
│   │   ├── sidebar.py         # Provider selection incl. Ollama
│   │   ├── home.py            # Home page
│   │   ├── analyzer.py        # ATS analysis
│   │   ├── builder.py         # Resume builder
│   │   ├── optimizer.py       # Resume optimizer
│   │   ├── cover_letter.py    # Cover letter generator
│   │   ├── interview_prep.py  # Q&A + Practice Coach + Chatbot
│   │   └── cool_features.py   # Match % + Shortlist + Custom Query
│   └── utils/
│       ├── file_parser.py     # PDF/DOCX/TXT extraction
│       └── exporters.py       # Download helpers
```

---

## 🛠️ Token Budget Reference

| Feature | Max Output Tokens | ~Cost on GPT-4o Mini |
|---------|------------------|----------------------|
| ATS Analysis | 1,800 | ~$0.001 |
| Resume Optimizer | 2,000 | ~$0.001 |
| Cover Letter | 800 | <$0.001 |
| Interview Q&A (8 Qs) | 1,500 | ~$0.001 |
| Practice Question | 250 | <$0.001 |
| Grade Answer | 500 | <$0.001 |
| Shortlist Analysis | 1,200 | ~$0.001 |
| Chat Response | 600 | <$0.001 |

---

## 🐳 Deploy with Docker

```bash
docker-compose up -d
# Visit http://localhost:8501
```

Or deploy to:
- **Streamlit Cloud**: Connect GitHub repo, deploy free
- **Railway**: `railway up`
- **Render**: Deploy as web service

---

## ❓ FAQ

**Q: I get a 402 error on OpenRouter**
A: You've hit your free credit limit. Switch to Groq (free) or install Ollama (free local).

**Q: Ollama is slow**
A: Use `llama3.2` (3B) for faster responses. GPU recommended for 8B+ models.

**Q: Can I use this with Claude API?**
A: Yes — select "Anthropic" and use `claude-3-haiku-20240307` (cheapest Claude model).

**Q: Is my resume data stored?**
A: Never. Data only exists in your browser session and is sent to your chosen API provider.
