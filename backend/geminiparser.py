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


# 🔷 Safe int conversion
def safe_int(value):
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r'\d+', value)
            if match:
                return int(match.group())
    except:
        pass
    return 0


# 🔷 Clean skills
def clean_skills(skills):
    return list({
        s.strip().title()
        for s in skills
        if isinstance(s, str) and len(s.strip()) > 1
    })


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
    2. Total years of experience (CALCULATE from dates)
    3. Experience breakdown

    IMPORTANT RULES:

    - Identify all work experiences with date ranges
    - Calculate total experience using years mentioned

    Examples:
    - 2020 - 2022 → 2 years
    - 2022 - Present → use current year(which is 2026)
    - Multiple roles → sum durations

    - Internships count as experience (0–1 years)
    - If no dates → leave as 0(don't guess)

    - Ignore soft skills
    - Extract only technical skills (Python, SQL, JavaScript, etc.)

    Think step-by-step but return ONLY JSON.

    OUTPUT FORMAT:

    {{
      "skills": [],
      "total_experience_years": number,
      "experience_breakdown": [
        {{
          "title": "",
          "company": "",
          "duration": ""
        }}
      ]
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
            "skills": clean_skills(parsed.get("skills", [])),
            "total_experience_years": safe_int(parsed.get("total_experience_years", 0)),
            "experience_breakdown": parsed.get("experience_breakdown", [])
        }

    except Exception as e:
        print("ERROR:", e)

        return {
            "skills": [],
            "total_experience_years": 0,
            "experience_breakdown": []
        }
