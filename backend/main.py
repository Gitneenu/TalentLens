from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from parser import extract_text
from geminiparser import parse_with_gemini
from database import supabase
from datetime import datetime

app = FastAPI()


# 🔷 Request Models
class FileItem(BaseModel):
    file_url: str


class BulkRequest(BaseModel):
    job_role: str
    batch_id: Optional[str] = None
    files: List[FileItem]


# 🔷 Allowed file types
ALLOWED_TYPES = (".pdf", ".docx", ".png", ".jpg", ".jpeg")


def is_valid_file(file_url):
    return file_url.lower().endswith(ALLOWED_TYPES)


# 🔷 Root
@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Parser API"}


# 🔷 Bulk Parse Endpoint
@app.post("/parse-bulk")
async def parse_bulk(request: BulkRequest):

    results = []

    # 🔥 Auto-generate batch_id if not provided
    batch_id = request.batch_id or datetime.now().strftime("%Y-%m-%d")

    for file in request.files:
        file_url = file.file_url

        # 🔹 Initialize per-file result
        result_item = {
            "file_url": file_url,
            "status": "processing",
            "progress": 0,
            "job_role": request.job_role,
            "batch_id": batch_id
        }

        # ❌ Unsupported file type
        if not is_valid_file(file_url):
            result_item.update({
                "status": "failed",
                "error": "Unsupported file type"
            })
            results.append(result_item)
            continue

        try:
            # 🔹 Step 1: Extract text
            text = extract_text(file_url)
            result_item["progress"] = 40

            # ❌ Corrupt / unreadable file
            if not text or len(text.strip()) < 50:
                result_item.update({
                    "status": "failed",
                    "error": "Corrupt or unreadable file"
                })
                results.append(result_item)
                continue

            # 🔹 Step 2: Parse with Gemini
            parsed_data = parse_with_gemini(text)
            result_item["progress"] = 80

            # 🔹 Step 3: Store in Supabase (UPDATED)
            insert_data = {
                "file_url": file_url,
                "raw_text": text,
                "parsed_json": parsed_data,
                "job_role": request.job_role,
                "batch_id": batch_id
            }

            db_response = supabase.table("resumes").insert(insert_data).execute()

            # ✅ Success
            result_item.update({
                "status": "completed",
                "progress": 100,
                "parsed": parsed_data,
                "db_response": db_response.data
            })

        except Exception as e:
            result_item.update({
                "status": "failed",
                "error": str(e)
            })

        results.append(result_item)

    return {"results": results}