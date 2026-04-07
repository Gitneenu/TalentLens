import { useState, useEffect } from "react";
const API = import.meta.env.VITE_API_URL;

export default function Upload() {
  const [input, setInput] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [jobs, setJobs] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // 🔹 Fetch jobs
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await API.get("/dashboard");

        // 🔥 Flatten nested jobs structure
        const flattenedJobs = Array.isArray(res.data.jobs)
          ? res.data.jobs.flatMap((j) => j.jobs || [])
          : [];

        setJobs(flattenedJobs);

      } catch (err) {
        console.error(err);
      }
    };

    fetchJobs();
  }, []);

  // 🔹 Handle upload
  const handleUpload = async () => {
    if (!jobRole) {
      return alert("Select a job role");
    }

    const urls = input
      .split("\n")
      .map((url) => url.trim())
      .filter((url) => url !== "");

    if (urls.length === 0) {
      return alert("Enter at least one URL");
    }

    const files = urls.map((url) => ({
      file_url: url,
    }));

    try {
      setLoading(true);

      const res = await API.post("/parse-bulk", {
        job_role: jobRole,
        files: files,
      });

      setResults(res.data.results);

    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      
      <div className="bg-[#0f1a2b] p-8 rounded-xl w-[600px] shadow-lg">
        
        <h1 className="text-3xl font-bold mb-6">
          Upload & Parsing
        </h1>

        {/* 🔹 Job Dropdown */}
        <select
          className="w-full mb-4 p-3 rounded bg-gray-800"
          value={jobRole}
          onChange={(e) => setJobRole(e.target.value)}
        >
          <option value="">Select Job Role</option>

          {Array.isArray(jobs) &&
            jobs.map((job) => (
              <option key={job.id} value={job.title}>
                {job.title}
              </option>
            ))}
        </select>

        {/* 🔹 Textarea */}
        <textarea
          placeholder="Paste resume URLs (one per line)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full h-40 p-4 rounded bg-gray-800 mb-4"
        />

        {/* 🔹 Button */}
        <button
          onClick={handleUpload}
          className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded text-lg"
        >
          {loading ? "Uploading..." : "Upload"}
        </button>

        {/* 🔹 Results */}
        <div className="mt-6 space-y-3">
          {results.map((r, i) => (
            <div key={i} className="bg-gray-800 p-3 rounded">
              
              <p className="text-sm break-all">
                {r.file_url}
              </p>

              <p className="mt-1">
                Status:{" "}
                <span
                  className={
                    r.status === "completed"
                      ? "text-green-400"
                      : "text-red-400"
                  }
                >
                  {r.status}
                </span>
              </p>

              {r.progress !== undefined && (
                <p className="text-blue-400 text-sm">
                  Progress: {r.progress}%
                </p>
              )}

              {r.error && (
                <p className="text-red-400 text-sm">
                  Error: {r.error}
                </p>
              )}

            </div>
          ))}
        </div>

      </div>
    </div>
  );
}