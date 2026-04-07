from google import genai
import os
from dotenv import load_dotenv
from geminiparser import extract_json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# 🔥 Combined function (score + summary only)
def semantic_score(resume_data, jd_text):

    prompt = f"""
    You are an expert recruiter.

    Compare the resume with the job description.

    Evaluate:
    - Skill relevance (semantic understanding, not exact match)
    - Experience depth (VERY IMPORTANT)
    - Role alignment

    Prioritize depth of experience over mere mentions of a skill.

    Tasks:
    1. Give a compatibility score (0-100)
    2. Give a 2-sentence "Summary of Fit"

    Return STRICT JSON ONLY:
    {{
      "score": number,
      "summary": ""
    }}

    Resume:
    {resume_data}

    Job Description:
    {jd_text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        parsed = extract_json(response.text)

        # 🔥 fallback
        if not parsed:
            return {
                "score": 0,
                "summary": ""
            }

        return {
            "score": parsed.get("score", 0),
            "summary": parsed.get("summary", "")
        }

    except Exception as e:
        print("Gemini Error:", e)
        return {
            "score": 0,
            "summary": ""
        }