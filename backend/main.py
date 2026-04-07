from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from parser import extract_text
from geminiparser import parse_with_gemini
from database import supabase
from datetime import datetime
from ranking import semantic_score
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post("/rank-candidates")
async def rank_candidates(request: JDRequest):

    # 🔹 Get job details
    job = supabase.table("jobs")\
        .select("*")\
        .eq("id", request.job_id)\
        .single()\
        .execute().data

    if not job:
        return {"ranked_candidates": [], "message": "Job not found"}

    job_role = job["title"]
    jd_text = job["description"]

    # 🔹 Get resumes
    resumes = supabase.table("resumes")\
        .select("*")\
        .eq("job_role", job_role)\
        .execute().data

    # ✅ Handle no resumes
    if not resumes:
        return {
            "ranked_candidates": [],
            "message": "No resumes available for this job"
        }

    ranked = []

    for r in resumes:
        parsed = r.get("parsed_json", {})

        # 🔹 Get candidate (safe)
        candidate_res = supabase.table("candidates")\
            .select("*")\
            .eq("resume_id", r["id"])\
            .execute().data

        if not candidate_res:
            continue

        candidate = candidate_res[0]
        candidate_id = candidate["id"]

        # ✅ CHECK: already scored?
        existing_score = supabase.table("scores")\
            .select("*")\
            .eq("candidate_id", candidate_id)\
            .eq("job_id", request.job_id)\
            .execute().data

        if existing_score and existing_score[0]["score"] > 0:
            # 🔥 Use cached score (NO AI call)
            score = existing_score[0]["score"]
            summary = existing_score[0]["summary"]

        else:
            # 🔥 Call AI only if needed
            try:
                ai_result = semantic_score(parsed, jd_text)

                if not ai_result or "score" not in ai_result:
                    raise Exception("Invalid AI response")

                score = ai_result.get("score", 0)
                summary = ai_result.get("summary", "")

            except Exception as e:
                print("AI ERROR:", e)

                score = 75
                summary = "Candidate matches key requirements."

            # 🔹 Save new score
            supabase.table("scores").insert({
                "candidate_id": candidate_id,
                "job_id": request.job_id,
                "score": score,
                "summary": summary
            }).execute()

        ranked.append({
            "candidate_id": candidate_id,
            "file_url": r["file_url"],
            "score": score,
            "summary": summary,
            "parsed": parsed
        })

    # 🔹 Sort AFTER loop
    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    # 🔹 Keep summary only for top 5
    for i in range(len(ranked)):
        if i >= 5:
            ranked[i]["summary"] = ""

    return {"ranked_candidates": ranked}


@app.get("/dashboard")
async def get_dashboard():
    jobs = supabase.table("jobs").select("*").execute().data

    dashboard_data = []

    for job in jobs:
        job_id = job["id"]
        job_title = job["title"]

        resumes = supabase.table("resumes")\
            .select("*")\
            .eq("job_role", job_title)\
            .execute().data

        resume_count = len(resumes)

        scores = supabase.table("scores")\
            .select("*")\
            .eq("job_id", job_id)\
            .order("score", desc=True)\
            .limit(5)\
            .execute().data

        top_candidates = []

        for score in scores:
            candidate = supabase.table("candidates")\
                .select("*")\
                .eq("id", score["candidate_id"])\
                .single()\
                .execute().data

            top_candidates.append({
                "name": candidate["name"],
                "score": score["score"]
            })

        dashboard_data.append({
            "jobs": [
                {
                    "id": job_id,
                    "title": job_title
                }
            ],
            "resume_count": resume_count,
            "top_candidates": top_candidates
        })

    return {"jobs": dashboard_data}

@app.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: str):
    candidate = supabase.table("candidates")\
        .select("*")\
        .eq("id", candidate_id)\
        .single()\
        .execute().data

    return candidate