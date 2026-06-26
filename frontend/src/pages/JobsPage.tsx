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

  if (loading) return <Loading label="Loading jobs..." />;

  return (
    <div className="page">
      <section className="page-hero">
        <p className="eyebrow">RabbitMQ + Celery</p>
        <h1>Jobs</h1>
        <p className="hero-copy">
          Model training is not done inside the request. The API queues a job and the worker updates the status.
        </p>
      </section>
      <section className="card">
        <div className="card-header">
          <div>
            <h2>Training jobs</h2>
            <p>Auto-refresh every 3 seconds.</p>
          </div>
        </div>
        <div className="table-wrap">
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
      </section>
    </div>
  );
}
