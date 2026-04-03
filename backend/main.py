from fastapi import FastAPI, Request
from parser import extract_text, extract_skills, extract_experience
from geminiparser import parse_with_gemini
from config import supabase

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Resume Parser API"}


@app.post("/parse-bulk")
async def parse_bulk(request: Request):
    data = await request.json()
    files = data.get("files", [])

    results = []

    for file in files:
        file_url = file.get("file_url")

        # TEMP (Day 1)
        #file_path = "sample.pdf"

        text = extract_text(file_url)

        skills = extract_skills(text)
        experience = extract_experience(text)

        parsed_data = {
            "skills": skills,
            "experience": experience
        }

        supabase.table("resumes").insert({
            "file_url": file_url,
            "raw_text": text,
            "parsed_json": parsed_data
        }).execute()

        results.append({
            "file": file_url,
            "status": "parsed"
        })

    return {"results": results}