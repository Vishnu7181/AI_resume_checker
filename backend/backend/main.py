from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from parsers import extract_text, validate_file

app = FastAPI(title="Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze(
    job_description: str = Form(...),
    resume_text: str = Form(...),
):
    # --- your existing scoring logic goes here ---
    # Example placeholder:
    jd_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())
    matched = jd_words & resume_words
    score = int(len(matched) / max(len(jd_words), 1) * 100)

    return {
        "score": score,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(jd_words - resume_words),
    }


@app.post("/analyze-file")
async def analyze_file(
    job_description: str = Form(...),
    file: UploadFile = File(...),
):
    content = await file.read()

    try:
        validate_file(file.filename, content)
        resume_text = extract_text(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read the resume file. Please re-upload it.",
        )

    return await analyze(job_description=job_description, resume_text=resume_text)
