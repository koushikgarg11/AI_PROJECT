# 🤖 AI Hire — Resume Shortlister & Interview Form Generator

An AI-powered hiring automation tool built with **Streamlit** and **Google Gemini**. Upload resumes, let AI shortlist the best candidates, and automatically generate personalized interview question forms — including video responses for communication skills assessment.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔑 **One-time Gemini Key** | Enter your Google Gemini API key once per session — never stored |
| 📄 **Batch Resume Upload** | Upload multiple PDF/DOCX resumes at once |
| 🧠 **AI Shortlisting** | Gemini scores and ranks candidates against your custom criteria |
| 📝 **Personalized Forms** | Auto-generates skill, project & communication questions per candidate |
| 🎥 **Video Responses** | Candidates upload 2 video answers for communication skills |
| 👁️ **Response Viewer** | Review all answers and play back video responses |
| 📥 **Export** | Download results as CSV or JSON |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-hire.git
cd ai-hire
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

### 4. Open in Browser
Navigate to `http://localhost:8501`

---

## 📁 Project Structure

```
ai-hire/
├── app.py                        # Home page — API key setup
├── requirements.txt
├── .gitignore
├── README.md
│
├── pages/
│   ├── 1_Recruiter_Dashboard.py  # Upload resumes, shortlist, generate forms
│   ├── 2_Candidate_Form.py       # Candidate answers + video upload
│   └── 3_View_Responses.py       # Review all submissions
│
├── backend/
│   ├── gemini_client.py          # Google Gemini API wrapper
│   ├── resume_parser.py          # PDF/DOCX text extraction
│   ├── shortlister.py            # AI resume scoring
│   ├── question_generator.py     # AI question generation
│   └── storage.py                # JSON + file persistence
│
├── .streamlit/
│   └── config.toml               # Dark theme configuration
│
├── data/                         # Auto-created: JSON data files
└── uploads/                      # Auto-created: resumes & videos
    ├── resumes/
    └── videos/
```

---

## 🌐 Deploy to Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo and set **Main file path** to `app.py`
5. Click **Deploy!**

> ⚠️ **Note**: On Streamlit Cloud, uploaded files are stored in temporary session memory and won't persist between deployments. For production use, replace the `storage.py` layer with cloud storage (S3, GCS, etc.).

---

## 🔑 Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy and paste it into the app's Home page

The API key is stored only in your browser session — it is **never written to disk**.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend + Backend | Streamlit (Python) |
| AI Engine | Google Gemini 1.5 Flash |
| PDF Parsing | PyMuPDF (fitz) |
| DOCX Parsing | python-docx |
| Data Storage | JSON files (local) |
| Styling | Custom CSS injected via Streamlit |


