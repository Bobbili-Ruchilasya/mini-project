from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os

from ai_utils import get_key_points, get_mind_map, get_mcqs, get_study_plan

app = FastAPI()

# ✅ Store extracted PDF text in memory
stored_text = {"pdf_text": ""}

# ✅ Enable CORS for all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Ensure 'public' directory exists to avoid StaticFiles error
if not os.path.exists("public"):
    os.makedirs("public")

# ✅ Serve static files (frontend, CSS, etc.)
app.mount("/static", StaticFiles(directory="public"), name="static")

# ✅ Upload PDF and generate summary/snippet
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        stored_text["pdf_text"] = text

        key_points = get_key_points(text[:8000])
        return {
            "summary": key_points["summary"],
            "text_snippet": key_points["snippet"]
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ Mind map generation
@app.post("/generate-mindmap/")
async def generate_mind_map(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        stored_text["pdf_text"] = text

        mind_map = get_mind_map(text[:8000])
        return {"mind_map": mind_map}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ MCQ generation
@app.post("/generate-mcqs/")
async def generate_mcqs(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        stored_text["pdf_text"] = text

        mcqs = get_mcqs(text[:8000])
        if isinstance(mcqs, list) and mcqs and "error" in mcqs[0]:
            raise ValueError(mcqs[0]["error"])

        return {"mcqs": mcqs}

    except Exception as e:
        print("❌ MCQ generation error:", str(e))
        return JSONResponse(content={"error": f"MCQ generation failed: {str(e)}"}, status_code=500)

# ✅ Study plan generation
@app.post("/generate-study-plan/")
async def generate_study_plan(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open("temp.pdf", "wb") as f:
            f.write(contents)

        doc = fitz.open("temp.pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        stored_text["pdf_text"] = text

        study_plan = get_study_plan(text[:8000])
        return {"study_plan": study_plan}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
