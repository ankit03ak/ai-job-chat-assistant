"use client";

import { ChangeEvent, FormEvent, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  FileText,
  LoaderCircle,
  Send,
} from "lucide-react";
import JobCard from "../components/JobCard";
import { listApplications, parseResume, sendChat } from "../lib/api";
import type { JobMatch, ResumeProfile } from "../lib/types";

type Message = { role: "user" | "assistant"; text: string };
const JOBS_PER_PAGE = 25;

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Hi! Upload a resume for personalized recommendations, or ask me to find jobs such as “show remote Python roles”.",
    },
  ]);
  const [input, setInput] = useState("");
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const totalPages = Math.max(1, Math.ceil(jobs.length / JOBS_PER_PAGE));
  const pageStart = (currentPage - 1) * JOBS_PER_PAGE;
  const visibleJobs = jobs.slice(pageStart, pageStart + JOBS_PER_PAGE);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((current) => [...current, { role: "user", text }]);
    setLoading(true);
    setError(null);
    try {
      const response = await sendChat(
        text,
        conversationId,
        profile,
        visibleJobs.map((item) => item.job.job_id),
        pageStart,
      );
      setConversationId(response.conversation_id);
      setJobs(response.jobs);
      setCurrentPage(1);
      setMessages((current) => [
        ...current,
        { role: "assistant", text: response.reply },
      ]);
      if (response.errors.length > 0) setError(response.errors.join(", "));
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "The assistant is unavailable.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const parsedProfile = await parseResume(file);
      const response = await sendChat(
        "Show matching jobs",
        conversationId,
        parsedProfile,
        [],
      );
      setProfile(parsedProfile);
      setConversationId(response.conversation_id);
      setJobs(response.jobs);
      setCurrentPage(1);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: `${response.reply} I also extracted your resume profile and displayed the details beside the conversation.`,
        },
      ]);
      if (response.errors.length > 0) setError(response.errors.join(", "));
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Resume parsing or job matching failed.",
      );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function showApplications() {
    setError(null);
    try {
      const applications = await listApplications();
      if (applications.length === 0) {
        setMessages((current) => [
          ...current,
          { role: "assistant", text: "You have no recorded applications yet." },
        ]);
        return;
      }
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: applications
            .map(
              (application, index) =>
                `${index + 1}. ${application.job_title_snapshot} at ${application.company_snapshot} - ${application.status.replace("_", " ")}`,
            )
            .join("\n"),
        },
      ]);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Could not load applications.",
      );
    }
  }

  return (
    <div className="page-container">
      <div className="eyebrow">AI job assistant</div>
      <h1>Find work that fits your story.</h1>
      <p className="subtle">
        A transparent workspace for resume-aware job discovery and locally
        simulated applications.
      </p>
      <div className="chat-layout">
        <section className="chat-panel" aria-label="Job assistant conversation">
          <div className="messages">
            {messages.map((message, index) => (
              <div
                className={`message ${message.role}`}
                key={`${message.role}-${index}`}
              >
                {message.text}
              </div>
            ))}
            {loading && (
              <div className="message assistant">
                <LoaderCircle className="spin" size={16} /> Thinking...
              </div>
            )}
          </div>
          <form className="composer" onSubmit={submit}>
            <textarea
              aria-label="Message"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about jobs or applications..."
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void submit();
                }
              }}
            />
            <button
              className="primary-button"
              type="submit"
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              <Send size={17} />
            </button>
          </form>
        </section>
        <aside>
          <div className="side-card">
            <h2>Your resume</h2>
            <div className="upload-zone">
              <FileText size={20} />
              <span className="subtle">PDF or DOCX, up to 5 MB</span>
              <input
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={upload}
                disabled={uploading}
              />
              {uploading && <span className="subtle">Parsing securely...</span>}
            </div>
            {profile && (
              <div className="profile-grid">
                <strong>{profile.name ?? "Profile extracted"}</strong>
                <span>
                  {profile.current_designation ?? "Designation not listed"}
                </span>
                {(profile.email || profile.phone) && (
                  <div className="profile-contact">
                    {profile.email && <span>{profile.email}</span>}
                    {profile.phone && <span>{profile.phone}</span>}
                  </div>
                )}
                {profile.total_experience_years !== null && (
                  <span>
                    {profile.total_experience_years} years of experience
                  </span>
                )}
                <div className="tag-list">
                  {profile.skills.slice(0, 8).map((skill) => (
                    <span className="tag" key={skill}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          <button
            className="secondary-button"
            type="button"
            onClick={() => void showApplications()}
          >
            View my applications
          </button>
          {error && (
            <div className="error-box" role="alert">
              {error}
            </div>
          )}
        </aside>
      </div>
      {profile && (
        <section
          className="profile-details"
          aria-label="Extracted resume details"
        >
          <div className="section-heading">
            <div>
              <div className="eyebrow">Resume insights</div>
              <h2>Extracted profile details</h2>
            </div>
            <span className="profile-badge">Ready for matching</span>
          </div>
          <div className="profile-details-grid">
            {profile.experience_summary && (
              <article className="profile-detail-card profile-detail-wide">
                <h3>Experience</h3>
                <p className="subtle">{profile.experience_summary}</p>
              </article>
            )}
            {profile.education.length > 0 && (
              <article className="profile-detail-card">
                <h3>Education</h3>
                {profile.education.map((education, index) => (
                  <div
                    className="profile-item"
                    key={`${education.institution}-${index}`}
                  >
                    <strong>{education.degree ?? "Education"}</strong>
                    <span>
                      {[education.field_of_study, education.institution]
                        .filter(Boolean)
                        .join(" · ")}
                    </span>
                    {education.graduation_year && (
                      <span>{education.graduation_year}</span>
                    )}
                  </div>
                ))}
              </article>
            )}
            {profile.projects.length > 0 && (
              <article className="profile-detail-card">
                <h3>Projects</h3>
                <div className="project-list">
                  {profile.projects.map((project) => (
                    <div className="profile-item" key={project.name}>
                      <strong>{project.name}</strong>
                      {project.description && (
                        <span>{project.description}</span>
                      )}
                      {project.technologies.length > 0 && (
                        <div className="tag-list">
                          {project.technologies.map((technology) => (
                            <span className="tag" key={technology}>
                              {technology}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </article>
            )}
          </div>
        </section>
      )}
      {jobs.length > 0 && (
        <section className="jobs-section">
          <div className="jobs-heading">
            <div>
              <h2>Recommended jobs</h2>
              <p className="subtle">
                Showing {pageStart + 1}-
                {Math.min(pageStart + JOBS_PER_PAGE, jobs.length)} of{" "}
                {jobs.length} jobs
              </p>
            </div>
          </div>
          {visibleJobs.map((match, index) => (
            <JobCard
              key={match.job.job_id}
              match={match}
              position={pageStart + index + 1}
              onApplied={() => undefined}
            />
          ))}
          {totalPages > 1 && (
            <div
              className="pagination pagination-bottom"
              aria-label="Job results pagination"
            >
              <button
                className="pagination-button"
                type="button"
                onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                disabled={currentPage === 1}
                aria-label="Previous jobs page"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="pagination-label">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="pagination-button"
                type="button"
                onClick={() =>
                  setCurrentPage((page) => Math.min(totalPages, page + 1))
                }
                disabled={currentPage === totalPages}
                aria-label="Next jobs page"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
