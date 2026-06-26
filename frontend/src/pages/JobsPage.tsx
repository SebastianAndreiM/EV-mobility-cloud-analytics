import { useEffect, useState } from "react";
import { getJobs, Job } from "../api/jobsApi";
import { usePolling } from "../hooks/usePolling";
import Loading from "../components/Loading";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    getJobs()
      .then(setJobs)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);
  usePolling(load, 3000, true);

  if (loading) return <Loading />;

  return (
    <div>
      <h1>Jobs</h1>
      <table className="data-table">
        <thead>
          <tr><th>ID</th><th>Type</th><th>Status</th><th>Detail</th><th>Updated</th></tr>
        </thead>
        <tbody>
          {jobs.map((j) => (
            <tr key={j.id}>
              <td>{j.id}</td>
              <td>{j.job_type}</td>
              <td><span className={`badge badge-${j.status}`}>{j.status}</span></td>
              <td>{j.detail}</td>
              <td>{new Date(j.updated_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
