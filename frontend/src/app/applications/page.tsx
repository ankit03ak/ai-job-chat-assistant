"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { listApplications } from "../../lib/api";
import type { Application } from "../../lib/types";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setApplications(await listApplications());
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Could not load applications.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <div className="eyebrow">Workspace</div>
          <h1>Applications</h1>
          <p className="subtle">
            Local simulated applications only. Nothing is submitted to
            employers.
          </p>
        </div>
        <button
          className="secondary-button"
          onClick={() => void load()}
          disabled={loading}
        >
          <RefreshCw size={15} /> Refresh
        </button>
      </div>
      {error && (
        <div className="error-box" role="alert">
          {error}
        </div>
      )}
      {loading ? (
        <div className="empty-state">Loading applications...</div>
      ) : applications.length === 0 ? (
        <div className="empty-state">
          <h2>No applications yet</h2>
          <p className="subtle">
            When you explicitly record an application, it will appear here.
          </p>
        </div>
      ) : (
        <div className="application-list">
          {applications.map((application) => (
            <article className="application-card" key={application.id}>
              <div>
                <strong>{application.job_title_snapshot}</strong>
                <div className="job-company">
                  {application.company_snapshot}
                </div>
                <div className="job-meta">
                  {new Date(application.applied_at).toLocaleString()}
                </div>
              </div>
              <span className="status">
                {application.status.replace("_", " ")}
              </span>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
