import { useEffect, useState } from "react";
import API from "../api";

export default function Rank() {
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState("");

  const [jobTitle, setJobTitle] = useState("");
  const [jobDesc, setJobDesc] = useState("");

  const [candidates, setCandidates] = useState([]);
  const [names, setNames] = useState({});
  const [loading, setLoading] = useState(false);

  // 🔹 Fetch jobs
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await API.get("/dashboard");
        const flatJobs = res.data.jobs.flatMap(j => j.jobs || []);
        setJobs(flatJobs);
      } catch (err) {
        console.error(err);
      }
    };

    fetchJobs();
  }, []);

  // 🔹 Fetch candidate names
  const fetchNames = async (list) => {
    try {
      const requests = list.map(c =>
        API.get(`/candidate/${c.candidate_id}`)
      );

      const responses = await Promise.all(requests);

      const map = {};
      responses.forEach((res, i) => {
        map[list[i].candidate_id] = res.data?.name || "Unknown";
      });

      setNames(map);

    } catch (err) {
      console.error(err);
    }
  };

  // 🔹 Ranking logic
  const handleRanking = async () => {
    try {
      setLoading(true);

      let finalJobId = jobId;

      // ❗ Prevent mixing inputs
      if ((jobTitle || jobDesc) && jobId) {
        alert("Use either dropdown OR manual input");
        return;
      }

      // 🔥 Manual job creation
      if (jobTitle.trim() && jobDesc.trim()) {
        const createRes = await API.post("/create-job", {
          title: jobTitle,
          description: jobDesc,
        });

        finalJobId = createRes.data.job[0].id;

        // ✅ NEW: Show success message for demo
        alert("Job added successfully. Now upload resumes to start ranking.");
      }

      if (!finalJobId) {
        alert("Enter job details or select a job");
        return;
      }

      // 🔹 Ranking
      const res = await API.post("/rank-candidates", {
        job_id: finalJobId,
      });

      const ranked = res.data.ranked_candidates;

      // ✅ NEW: Handle empty resumes
      if (!ranked || ranked.length === 0) {
        setCandidates([]);
        alert("No resumes found. Please upload resumes to see ranking.");
        return;
      }

      setCandidates(ranked);
      await fetchNames(ranked);

    } catch (err) {
      console.error(err);

      // ✅ NEW: Better error handling
      if (err.response?.data?.message?.includes("No resumes")) {
        alert("No resumes uploaded yet. Please upload resumes first.");
      } else {
        alert("Something went wrong. Please try again.");
      }

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white px-10 py-8">

      <h1 className="text-3xl font-bold mb-8">
        JD-Based Candidate Ranking
      </h1>

      {/* 🔹 Dropdown */}
      <div className="mb-6">
        <label className="block mb-2 text-gray-400">
          Select Existing Job
        </label>

        <select
          className="bg-gray-900 p-3 rounded w-full"
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
        >
          <option value="">-- Select Job --</option>

          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title}
            </option>
          ))}
        </select>
      </div>

      {/* OR */}
      <p className="text-center text-gray-500 mb-4">OR</p>

      {/* 🔹 Job Title */}
      <div className="mb-4">
        <label className="block mb-2 text-gray-400">
          Job Title
        </label>

        <input
          type="text"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
          placeholder="Enter job title..."
          className="w-full p-3 rounded bg-gray-900"
        />
      </div>

      {/* 🔹 Job Description */}
      <div className="mb-6">
        <label className="block mb-2 text-gray-400">
          Job Description
        </label>

        <textarea
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          placeholder="Enter job description..."
          className="w-full h-40 p-4 rounded bg-gray-900"
        />
      </div>

      {/* 🔹 Button */}
      <button
        onClick={handleRanking}
        className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg"
      >
        {loading ? "Analyzing..." : "Ranked Candidates"}
      </button>

      {/* 🔹 Results */}
      <div className="mt-10 space-y-5">

        {candidates.map((c, index) => (
          <div
            key={index}
            className={`p-5 rounded-lg ${
              index < 5 ? "bg-[#1a2b4c]" : "bg-gray-900"
            }`}
          >

            {/* Name */}
            <div className="flex justify-between">
              <h2 className="text-lg font-bold">
                #{index + 1} {names[c.candidate_id] || "Loading..."}
              </h2>

              {index < 3 && (
                <span className="text-yellow-400">
                  ⭐ Top {index + 1}
                </span>
              )}
            </div>

            {/* Score */}
            <p className="text-green-400 mt-2">
              Compatibility Score: {c.score}%
            </p>

            <div className="w-full bg-gray-700 h-2 mt-1 rounded">
              <div
                className="bg-green-500 h-2 rounded"
                style={{ width: `${c.score}%` }}
              />
            </div>


            {/* Summary */}
            {c.summary && (
              <p className="mt-3 text-blue-400">
                <strong>Summary:</strong> {c.summary}
              </p>
            )}

            {/* File */}
            <p className="text-sm text-gray-500 mt-2 break-all">
              {c.file_url}
            </p>

          </div>
        ))}

      </div>
    </div>
  );
}