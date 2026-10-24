export type EducationItem = {
  institution: string | null;
  degree: string | null;
  field_of_study: string | null;
  graduation_year: number | null;
};

export type ProjectItem = {
  name: string;
  description: string | null;
  technologies: string[];
};

export type ResumeProfile = {
  name: string | null;
  email: string | null;
  phone: string | null;
  current_designation: string | null;
  target_designations: string[];
  skills: string[];
  experience_summary: string | null;
  total_experience_years: number | null;
  education: EducationItem[];
  projects: ProjectItem[];
  raw_text_available: boolean;
  warnings: string[];
};

export type Job = {
  job_id: string;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  experience_required: string | null;
  skills: string[];
  description: string;
  source_name: string;
  source_url: string;
  posted_at: string | null;
  employment_type: string | null;
  salary: string | null;
  scraped_at: string;
};

export type JobMatch = {
  job: Job;
  match_score: number;
  matched_skills: string[];
  missing_or_unmatched_skills: string[];
  match_reasons: string[];
};

export type Application = {
  id: number;
  job_id: string;
  job_title_snapshot: string;
  company_snapshot: string;
  applied_at: string;
  status: string;
  application_method: string;
  notes: string | null;
};

export type ChatResponse = {
  conversation_id: string;
  reply: string;
  intent: string;
  jobs: JobMatch[];
  resume_profile: ResumeProfile | null;
  applications: Application[];
  errors: string[];
};
