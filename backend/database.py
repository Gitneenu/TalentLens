from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase credentials!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_resume(filename: str, content: str, file_url: str, job_role: str):
    try:
        data = {
            "filename": filename,
            "content": content,
            "file_url": file_url,
            "job_role": job_role
        }

        response = supabase.table("resumes").insert(data).execute()

        return {"success": True, "data": response.data}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_resumes():
    try:
        response = supabase.table("resumes").select("*").execute()
        return {"success": True, "data": response.data}

    except Exception as e:
        return {"success": False, "error": str(e)}