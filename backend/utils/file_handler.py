import os
from uuid import uuid4
from database import supabase

def upload_to_supabase(file):
    file_ext = file.filename.split(".")[-1]
    unique_name = f"{uuid4()}.{file_ext}"

    file_bytes = file.file.read()

    response = supabase.storage.from_("resumes").upload(
        path=unique_name,
        file=file_bytes
    )

    file_url = supabase.storage.from_("resumes").get_public_url(unique_name)

    return unique_name, file_url