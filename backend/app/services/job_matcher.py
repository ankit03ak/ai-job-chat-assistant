import re
from dataclasses import dataclass

from app.schemas.job import Job
from app.schemas.matching import JobMatch
from app.schemas.resume import ResumeProfile


@dataclass(frozen=True)
class MatchWeights:
    skills: float = 0.50
    designation: float = 0.25
    experience: float = 0.15
    location: float = 0.10


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", value.casefold()).strip()


class JobMatcher:
    def __init__(self, weights: MatchWeights = MatchWeights()) -> None:
        if abs(sum((weights.skills, weights.designation, weights.experience, weights.location)) - 1) > 0.001:
            raise ValueError("Match weights must sum to 1")
        self.weights = weights

    def score(self, profile: ResumeProfile, job: Job) -> JobMatch:
        profile_skills = {_normalize(skill) for skill in profile.skills}
        job_skills = {_normalize(skill) for skill in job.skills}
        matched = sorted(skill for skill in job.skills if _normalize(skill) in profile_skills)
        missing = sorted(skill for skill in job.skills if _normalize(skill) not in profile_skills)
        skill_score = len(matched) / len(job_skills) if job_skills else 0

        designations = profile.target_designations + (
            [profile.current_designation] if profile.current_designation else []
        )
        title = _normalize(job.title)
        designation_score = 1 if any(_normalize(item) in title or title in _normalize(item) for item in designations) else 0
        experience_score = 0.5 if profile.total_experience_years is not None and job.experience_required else 0
        location_score = 1 if job.work_mode.casefold() == "remote" else 0
        score = round(
            100
            * (
                self.weights.skills * skill_score
                + self.weights.designation * designation_score
                + self.weights.experience * experience_score
                + self.weights.location * location_score
            ),
            2,
        )
        reasons = []
        if matched:
            reasons.append(f"Matches {', '.join(matched)}")
        if designation_score:
            reasons.append("Role title aligns with your target or current designation")
        if location_score:
            reasons.append("This role is remote")
        return JobMatch(
            job=job,
            match_score=score,
            matched_skills=matched,
            missing_or_unmatched_skills=missing,
            match_reasons=reasons,
        )

    def rank(self, profile: ResumeProfile, jobs: list[Job], minimum_score: float = 0) -> list[JobMatch]:
        return sorted(
            (match for match in (self.score(profile, job) for job in jobs) if match.match_score >= minimum_score),
            key=lambda match: (-match.match_score, match.job.job_id),
        )
