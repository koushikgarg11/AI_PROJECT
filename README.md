# 🎯 TalentScreen AI — Resume Screening Automation

AI-powered recruitment platform that shortlists resumes and generates personalized assessment forms with video questions — built with **Streamlit** and **Gemini AI**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Resume Screening | Gemini AI reads and scores resumes against your criteria |
| 📋 Personalized Questions | 8 tailored questions per candidate (skills + projects) |
| 🎥 Video Responses | 2 communication questions require video upload |
| 📊 HR Dashboard | Review all submissions, answers, and videos in one place |
| 💾 Persistent Storage | JSON-based storage (swap for a database in production) |

---

## 🗂️ Project Structure

```
AI_PROJECT/
├── app.py                    # Home page
├── requirements.txt
├── .gitignore
├── README.md
├── pages/
│   ├── 1_HR_Portal.py        # Set criteria & upload resumes
│   ├── 2_Candidate_Form.py   # Assessment form for candidates
│   └── 3_Dashboard.py        # View all results
├── utils/
│   ├── __init__.py
│   ├── ai_screener.py        # Gemini AI logic (screening + questions)
│   └── storage.py            # JSON file storage helpers
├── data/                      # Auto-created: stores criteria, candidates, submissions
├── uploads/                   # Auto-created: temp resume storage
└── submissions/                # Auto-created: candidate video uploads
```

> ⚠️ **Important:** the `pages/` and `utils/` folders are required exactly as shown.
> Streamlit only auto-discovers multipage routes inside a folder literally named `pages/`
> next to `app.py`, and the page scripts import from `utils.ai_screener` / `utils.storage`,
> so those two files must live inside a `utils/` folder for the imports to resolve.

---

## 🚀 Setup & Run Locally

### 1. Clone & Install
```bash
git clone https://github.com/koushikgarg11/AI_PROJECT.git
cd AI_PROJECT
pip install -r requirements.txt
```

### 2. Set Your Gemini API Key
The app reads `GEMINI_API_KEY` (see `utils/ai_screener.py`).

```bash
# Option A: Environment variable
export GEMINI_API_KEY="your-gemini-key"

# Option B: Create a .env file (requires python-dotenv if you want it auto-loaded)
echo "GEMINI_API_KEY=your-gemini-key" > .env
```

> 🔒 **Never commit `.env` to GitHub.** It's already listed in `.gitignore` — keep it that way.
> If a real key was ever pushed to a public repo, treat it as compromised: regenerate it in the
> Google AI Studio console immediately, even after removing the file.

### 3. Run the App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub (with `pages/` and `utils/` structure intact).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click **New app** → select your repo → set main file: `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your-gemini-key"
   ```
5. Click **Deploy** 🎉

---

## 🔄 HR Workflow

```
HR sets job criteria
       ↓
Upload resumes (PDF/DOCX)
       ↓
AI scores & shortlists candidates
       ↓
HR shares assessment link with shortlisted candidates
       ↓
Candidates fill personalized form (skills + project + 2 video questions)
       ↓
HR reviews all responses on the Dashboard
```

---

## ⚙️ Configuration

Edit job criteria directly in the **HR Portal** tab — no code changes needed.

| Field | Description |
|---|---|
| Must-Have Skills | Hard requirements; missing these lowers score significantly |
| Nice-to-Have Skills | Bonus skills that improve score |
| Score Threshold | % above which candidates are shortlisted (default: 65%) |
| Additional Notes | Free-text guidance sent to the AI |

---

## 🔧 Production Upgrades (Recommended)

- Replace JSON storage with **PostgreSQL** or **SQLite**
- Add **email notifications** (SendGrid / SMTP) for candidate links
- Add **authentication** with `streamlit-authenticator`
- Store videos in **AWS S3** or **Google Cloud Storage**
- Add **ATS integration** (Greenhouse, Lever, etc.)

---

## 📦 Dependencies

- `streamlit` — frontend UI
- `google-genai` — Gemini AI API
- `pdfplumber` — PDF text extraction
- `python-docx` — DOCX text extraction

---

## 🔒 Security Notes

- `.env`, `data/`, `uploads/`, and `submissions/` are excluded via `.gitignore` — they may
  contain API keys, candidate resumes, or personal video responses and should never be
  committed to a public repository.
- If you're deploying publicly, add authentication before exposing the HR Portal or
  Dashboard — as shipped, anyone with the URL can access them.
