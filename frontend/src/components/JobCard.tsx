"use client";

import { useState } from "react";
import { CheckCircle2, MapPin } from "lucide-react";
import { createApplication } from "../lib/api";
import type { JobMatch } from "../lib/types";

export default function JobCard({
  match,
  position,
  onApplied,
}: {
  match: JobMatch;
  position: number;
  onApplied: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const job = match.job;

  async function apply() {
    setBusy(true);
    setFeedback(null);
    try {
      await createApplication(job.job_id);
      setFeedback("Saved as a simulated local application.");
      onApplied();
    } catch (error) {
      setFeedback(
        error instanceof Error ? error.message : "Could not save application.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="job-card">
      <div className="job-head">
        <div>
          <div className="job-title">
            Job {position}: {job.title}
          </div>
          <div className="job-company">{job.company}</div>
        </div>
        <span className="score">{match.match_score.toFixed(0)}% match</span>
      </div>
      <div className="job-meta">
        <MapPin size={13} /> {job.location} · {job.work_mode} ·{" "}
        {job.experience_required ?? "Experience not listed"}
      </div>
      <div className="tag-list">
        {job.skills.slice(0, 6).map((skill) => (
          <span className="tag" key={skill}>
            {skill}
          </span>
        ))}
      </div>
      {match.match_reasons.length > 0 && (
        <div className="subtle">{match.match_reasons.join(" · ")}</div>
      )}
      <div className="job-actions">
        <button className="secondary-button" onClick={apply} disabled={busy}>
          {busy ? "Saving..." : "Record simulated application"}
        </button>
        <a
          className="source-link"
          href={job.source_url}
          target="_blank"
          rel="noreferrer"
        >
          View source
        </a>
      </div>
      {feedback && (
        <div className="subtle">
          <CheckCircle2 size={14} /> {feedback}
        </div>
      )}
    </article>
  );
}
