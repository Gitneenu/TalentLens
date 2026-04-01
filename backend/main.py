from fastapi import FastAPI, UploadFile, File
from utils.file_handler import upload_to_supabase
from utils.parser import extract_text
from database import save_resume, get_all_resumes

import tempfile

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Smart Talent Engine  🚀"}


@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Save temporarily (needed for parsing)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            temp_path = tmp.name

        # Extract text
        text = extract_text(temp_path)

        # Upload to Supabase Storage
        filename, file_url = upload_to_supabase(file)

        # Save to DB
        save_resume(filename, text[:2000])

        return {
            "status": "success",
            "file_url": file_url,
            "preview": text[:300]
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/resumes/")
def get_resumes():
    return get_all_resumes()