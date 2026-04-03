from google import genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# 🔷 Initialize client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# 🔷 Extract JSON safely
def extract_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("JSON ERROR:", e)
    return None


# 🔷 Main function
def parse_with_gemini(resume_text):

    if not resume_text:
        return {
            "skills": [],
            "total_experience_years": 0,
            "experience_breakdown": []
        }

    resume_text = resume_text[:4000]

    prompt = f"""
    You are an expert resume parser.

    Extract:

    1. Technical skills
    2. Total years of experience
    3. Experience breakdown

    RULES:
    - Extract skills like Python, JavaScript, HTML, CSS, SQL
    - Ignore soft skills
    - If fresher → experience = 0

    OUTPUT (STRICT JSON ONLY):

    {{
      "skills": [],
      "total_experience_years": number,
      "experience_breakdown": []
    }}

    Resume:
    {resume_text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text

        parsed = extract_json(raw_text)

        if not parsed:
            raise ValueError("Invalid JSON")

        return {
            "skills": list(set(parsed.get("skills", []))),
            "total_experience_years": int(parsed.get("total_experience_years", 0)),
            "experience_breakdown": parsed.get("experience_breakdown", [])
        }

    except Exception as e:
        print("ERROR:", e)

        return {
            "skills": [],
            "total_experience_years": 0,
            "experience_breakdown": []
        }