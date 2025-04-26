from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from backend.ai_utils import get_key_points, get_mind_map, get_mcqs, get_study_plan

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        text = text[:8000]
        key_points = get_key_points(text)

        return {
            "summary": key_points["summary"],
            "text_snippet": key_points["snippet"]
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/generate-mindmap/")
async def generate_mind_map(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        text = text[:8000]
        mind_map = get_mind_map(text)

        return {"mind_map": mind_map}

    except Exception as e:
        return {"error": str(e)}

@app.post("/generate-mcqs/")
async def generate_mcqs(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        text = text[:8000]
        mcqs = get_mcqs(text)

        # ✅ Handle error from Gemini JSON issues
        if isinstance(mcqs, list) and mcqs and "error" in mcqs[0]:
            raise ValueError(mcqs[0]["error"])

        return {"mcqs": mcqs}

    except Exception as e:
        print("❌ MCQ generation error:", str(e))
        return {"error": f"MCQ generation failed: {str(e)}"}

@app.post("/generate-study-plan/")
async def generate_study_plan(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        text = text[:8000]
        study_plan = get_study_plan(text)

        return {"study_plan": study_plan}

    except Exception as e:
        return {"error": str(e)}

