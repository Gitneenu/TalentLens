from google import genai
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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


# 🔷 Clean skills
def clean_skills(skills):
    return list({
        s.strip().title()
        for s in skills
        if isinstance(s, str) and len(s.strip()) > 1
    })


# 🔥 MONTH MAP
MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


# 🔥 PARSE DATE STRING
def parse_date(date_str):
    date_str = date_str.lower()

    # Handle "Present"
    if "present" in date_str:
        return datetime.now()

    # Extract year
    year_match = re.search(r'(20\d{2})', date_str)
    year = int(year_match.group()) if year_match else None

    # Extract month
    month = 1
    for key in MONTHS:
        if key in date_str:
            month = MONTHS[key]
            break

    if year:
        return datetime(year, month, 1)

    return None


# 🔥 CALCULATE EXPERIENCE FROM BREAKDOWN
def calculate_experience(experiences):
    total_months = 0

    for exp in experiences:
        duration = exp.get("duration", "")

        # split range
        parts = re.split(r'-|to', duration)

        if len(parts) < 2:
            continue

        start = parse_date(parts[0].strip())
        end = parse_date(parts[1].strip())

        if start and end:
            diff = (end.year - start.year) * 12 + (end.month - start.month)
            if diff > 0:
                total_months += diff

    # convert to years
    return round(total_months / 12, 1)


# 🔷 Main function
def parse_with_gemini(resume_text):

    if not resume_text:
        return {
            "name": "",
            "skills": [],
            "total_experience_years": 0,
            "experience_breakdown": []
        }

    resume_text = resume_text[:4000]

    prompt = f"""
    You are an expert resume parser.

    Extract:
    1. Candidate full name
    2. Technical skills
    3. Experience breakdown (IMPORTANT)
    
    RULES:
    - DO NOT calculate total experience
    - Just extract duration clearly (e.g., April 2019 - September 2019)
    - Include all roles
    - Extract only technical skills
    - Ignore soft skills

    OUTPUT FORMAT:

    {{
      "name": "",
      "skills": [],
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

        experiences = parsed.get("experience_breakdown", [])

        # 🔥 Calculate experience ourselves
        total_experience = calculate_experience(experiences)

        return {
            "name": parsed.get("name", "").strip(),
            "skills": clean_skills(parsed.get("skills", [])),
            "total_experience_years": total_experience,
            "experience_breakdown": experiences
        }

    except Exception as e:
        print("ERROR:", e)

        return {
            "name": "",
            "skills": [],
            "total_experience_years": 0,
            "experience_breakdown": []
        }