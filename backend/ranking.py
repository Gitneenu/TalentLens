from google import genai
import os
from dotenv import load_dotenv
from geminiparser import extract_json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# 🔷 Semantic scoring
def semantic_score(resume_data, jd_text):

    prompt = f"""
    You are an expert recruiter.

    Compare the resume with the job description.

    Evaluate:
    - Skill relevance (semantic understanding, not exact match)
    - Experience depth
    - Role alignment

    Prioritize depth of experience over mere mentions of a skill

    Return STRICT JSON:
    {{
      "score": number (0-100),
      "reason": ""
    }}

    Resume:
    {resume_data}

    Job Description:
    {jd_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    parsed = extract_json(response.text)

    return parsed or {"score": 0, "reason": ""}


# 🔷 Generate summary
def generate_summary(resume_data, jd_text):

    prompt = f"""
    In 2 sentences, explain why this candidate is a good fit for this job.

    Focus on:
    - relevant skills
    - experience
    - strengths

    Resume:
    {resume_data}

    Job Description:
    {jd_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()