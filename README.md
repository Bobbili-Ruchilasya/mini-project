# 📘 EduMorph – Your Smart PDF Study Assistant

**EduMorph** is an AI-powered mini project designed to help students learn faster and smarter by automatically extracting key information from their study material. Just upload a PDF, and get instant summaries, important snippets, MCQs, a 7-day study plan, and even a visual mind map!

---

## ✨ Features

- 📄 **PDF Upload** – Upload any academic PDF file.
- ✍️ **AI Summary Generator** – Instantly get the key points.
- 🧠 **Snippet Extraction** – See the most important sentences from each page.
- 🧭 **Mind Map Creation** – Visualize concepts with AI-generated mind maps.
- ❓ **MCQ Generator** – Practice with automatically generated multiple-choice questions.
- 🗓️ **7-Day Study Plan** – Get a personalized study roadmap.
- 📋 **Copy & Download** – Copy content to clipboard or download as text files.

---

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3
- JavaScript (Vanilla JS)
- MindElixir.js (for mind maps)

### Backend
- Python 3
- FastAPI
- PyMuPDF (for PDF text extraction)
- Gemini 1.5 Flash (Google AI model via API)

---

## 🚀 How It Works

1. User uploads a PDF on the frontend.
2. The backend extracts text from the PDF using PyMuPDF.
3. Extracted content is sent to the Gemini AI model to generate:
   - Summary
   - Key snippets
   - Mind map structure
   - MCQs
   - Study plan
4. Results are displayed on the frontend with copy and download options.

---

## 📁 Project Structure

edumorph/
│
├── backend/
│ ├── main.py # FastAPI app with all routes
│ ├── ai_utils.py # Gemini API functions
│ └── requirements.txt # Dependencies
│
├── frontend/
│ ├── index.html # Frontend UI
│ ├── styles.css # Custom styles
│ └── script.js # JS logic and API calls
│
└── README.md # You're reading it!

---

## 🧑‍💻 How to Run Locally

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
