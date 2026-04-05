from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from parser import extract_text
from geminiparser import parse_with_gemini
from database import supabase
from datetime import datetime
from ranking import semantic_score, generate_summary

app = FastAPI()


# 🔷 Request Models
class FileItem(BaseModel):
    file_url: str


class BulkRequest(BaseModel):
    job_role: str
    batch_id: Optional[str] = None
    files: List[FileItem]


# 🔥 Use job_id for ranking
class JDRequest(BaseModel):
    job_id: str


class JobRequest(BaseModel):
    title: str
    description: str


# 🔷 Allowed file types
ALLOWED_TYPES = (".pdf", ".docx", ".png", ".jpg", ".jpeg")


def is_valid_file(file_url):
    return file_url.lower().endswith(ALLOWED_TYPES)


# 🔷 Root
@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Parser API"}


# 🚀 CREATE JOB
@app.post("/create-job")
async def create_job(request: JobRequest):

    response = supabase.table("jobs").insert({
        "title": request.title,
        "description": request.description
    }).execute()

    return {
        "message": "Job created successfully",
        "job": response.data
    }


# 🚀 BULK UPLOAD (RESUME + CANDIDATE)
@app.post("/parse-bulk")
async def parse_bulk(request: BulkRequest):

    results = []
    batch_id = request.batch_id or datetime.now().strftime("%Y-%m-%d")

    for file in request.files:
        file_url = file.file_url

        result_item = {
            "file_url": file_url,
            "status": "processing",
            "progress": 0,
            "job_role": request.job_role,
            "batch_id": batch_id
        }

        # ❌ Unsupported file
        if not is_valid_file(file_url):
            result_item.update({
                "status": "failed",
                "error": "Unsupported file type"
            })
            results.append(result_item)
            continue

        try:
            # 🔹 Extract text
            text = extract_text(file_url)
            result_item["progress"] = 40

            # ❌ Corrupt file
            if not text or len(text.strip()) < 50:
                result_item.update({
                    "status": "failed",
                    "error": "Corrupt or unreadable file"
                })
                results.append(result_item)
                continue

            # 🔹 Gemini parse
            parsed_data = parse_with_gemini(text)
            result_item["progress"] = 80

            # 🔹 Insert into resumes
            resume_res = supabase.table("resumes").insert({
                "file_url": file_url,
                "raw_text": text,
                "parsed_json": parsed_data,
                "job_role": request.job_role,
                "batch_id": batch_id
            }).execute()

            resume_id = resume_res.data[0]["id"]

            # 🔹 Insert into candidates
            candidate_res = supabase.table("candidates").insert({
                "name": parsed_data.get("name", "Unknown"),
                "resume_id": resume_id
            }).execute()

            candidate_id = candidate_res.data[0]["id"]

            result_item.update({
                "status": "completed",
                "progress": 100,
                "candidate_id": candidate_id,
                "parsed": parsed_data
            })

        except Exception as e:
            result_item.update({
                "status": "failed",
                "error": str(e)
            })

        results.append(result_item)

    return {"results": results}


# 🚀 RANK CANDIDATES (WITH SCORES TABLE)
@app.post("/rank-candidates")
async def rank_candidates(request: JDRequest):

    # 🔹 Get job details
    job = supabase.table("jobs")\
        .select("*")\
        .eq("id", request.job_id)\
        .single()\
        .execute().data

    job_role = job["title"]
    jd_text = job["description"]

    # 🔹 Get resumes for that role
    resumes = supabase.table("resumes")\
        .select("*")\
        .eq("job_role", job_role)\
        .execute().data

    ranked = []

    for r in resumes:
        parsed = r.get("parsed_json", {})

        # 🔹 Get candidate linked to resume
        candidate = supabase.table("candidates")\
            .select("*")\
            .eq("resume_id", r["id"])\
            .single()\
            .execute().data

        candidate_id = candidate["id"]

        # 🔹 AI scoring
        ai_result = semantic_score(parsed, jd_text)
        score = ai_result.get("score", 0)
        reason = ai_result.get("reason", "")

        ranked.append({
            "candidate_id": candidate_id,
            "file_url": r["file_url"],
            "score": score,
            "reason": reason,
            "parsed": parsed
        })

        # 🔥 Store in scores table
        supabase.table("scores").insert({
            "candidate_id": candidate_id,
            "job_id": request.job_id,
            "score": score
        }).execute()

    # 🔥 Sort
    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    # 🔥 Add summary for top 5
    for i in range(min(5, len(ranked))):
        ranked[i]["summary"] = generate_summary(
            ranked[i]["parsed"],
            jd_text
        )

    return {"ranked_candidates": ranked}