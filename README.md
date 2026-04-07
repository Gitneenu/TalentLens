Project Title

TalentLens – AI-Powered Resume Screening System

The Problem

Traditional Applicant Tracking Systems rely heavily on keyword matching, often rejecting qualified candidates who use different but equivalent terminology. With hundreds to thousands of applications per role and only a few seconds spent per resume, recruiters struggle to identify the most suitable candidates accurately. This results in missed talent, biased filtering, and inefficient hiring decisions driven more by keyword optimization than actual skills and experience.

The Solution

TalentLens automates the resume screening process using AI. It extracts skills and experience from resumes, analyzes them using semantic matching, and ranks candidates based on job requirements. This helps recruiters quickly shortlist the best candidates with improved accuracy and efficiency.

Tech Stack

1.Programming Languages
Python
JavaScript

2.Frameworks
React.js
FastAPI

3.Database
Supabase

4.APIs / Third-party Tools
Google Gemini API
Axios
Uvicorn
Git & GitHub

Setup Instructions

Step 1: Clone the Repository
git clone https://github.com/YOUR_USERNAME/talentlens.git
cd talentlens

Step 2: Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate(windows)
source venv/bin/activate(Mac or Linux)
pip install -r requirements.txt
Create a .env file inside the backend folder and add:
        GEMINI_API_KEY=your_gemini_api_key
        SUPABASE_URL=your_supabase_url
        SUPABASE_KEY=your_supabase_key

Step 3: Frontend Setup
cd frontend
npm install
npm run dev

Step 4: Access the Application
Frontend: http://localhost:5173
Backend: http://127.0.0.1:8000