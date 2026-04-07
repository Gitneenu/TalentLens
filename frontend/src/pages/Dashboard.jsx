import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await API.get("/dashboard");
        setJobs(res.data.jobs);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white px-10 py-8">
      
      {/* Header */}
      <h1 className="text-4xl font-bold mb-10">
        Recruiter Dashboard
      </h1>

      {/* Job Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
        
        {jobs.length === 0 ? (
          <p className="text-gray-500">
            {loading ? "Fetching jobs..." : "No jobs found"}
          </p>
        ) : (
          jobs.map((job, index) => {
            const jobData = job.jobs?.[0];

            return (
              <div
                key={jobData?.id || index}
                className="bg-gray-900 rounded-xl p-6 shadow-lg"
              >
                {/* Job Title */}
                <h2 className="text-xl font-semibold">
                  {jobData?.title || "Untitled Job"}
                </h2>

                {/* Resume Count */}
                <p className="text-gray-400 mt-2">
                  Resumes Uploaded: {job.resume_count}
                </p>

                {/* Top Candidates */}
                <div className="mt-4">
                  <p className="text-gray-300 font-medium mb-2">
                    Top Talent:
                  </p>

                  {job.top_candidates.length === 0 ? (
                    <p className="text-gray-500 text-sm">
                      No ranking yet
                    </p>
                  ) : (
                    <ul className="text-sm text-gray-400 space-y-1">
                      {job.top_candidates.map((c, i) => (
                        <li key={i}>
                          {c.name} — {c.score}%
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Action */}
  
              </div>
            );
          })
        )}

      </div>
    </div>
  );
}