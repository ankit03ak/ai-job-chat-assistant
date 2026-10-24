import re
import uuid
from typing import Callable

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.state import AgentState, SearchFilters
from app.agents.tools import (
    apply_to_job,
    list_applications,
    resolve_visible_job,
    search_jobs,
)
from app.repositories.application_repository import DuplicateApplicationError
from app.repositories.job_repository import JobRepository
from app.schemas.chat import ChatResponse
from app.services.application_service import UnknownJobError


def classify_intent(state: AgentState) -> AgentState:
    message = state["message"].casefold()
    if re.search(r"\b(applied|status|applications?)\b", message) and not re.search(
        r"\b(apply|submit)\b", message
    ):
        intent = "application_tracking"
    elif re.search(r"\b(apply|submit|like)\b", message):
        intent = "application"
    elif re.search(r"\b(job|jobs|role|roles|remote|react|python|developer)\b", message):
        intent = "job_search"
    else:
        intent = "general"
    return {**state, "intent": intent}


def interpret_search_preferences(state: AgentState) -> AgentState:
    message = state["message"]
    lowered = message.casefold()
    filters: SearchFilters = {}
    for skill in ("react", "python", "fastapi", "typescript", "javascript", "java"):
        if skill in lowered:
            filters["skill"] = skill
            break
    for mode in ("remote", "hybrid", "on-site", "onsite"):
        if mode in lowered:
            filters["work_mode"] = "on-site" if mode == "onsite" else mode
            break
    experience = re.search(r"\b\d+\s*[-to]+\s*\d+\s*years?\b", lowered)
    if experience:
        filters["experience"] = experience.group(0).replace(" ", "")
    generic = re.sub(r"\b(show|find|jobs?|roles?|please|only|me|requiring|required|that|are|with)\b", " ", lowered)
    if generic.strip() and not filters:
        filters["q"] = generic.strip()
    return {**state, "search_filters": filters}


def filter_and_rank_jobs(
    state: AgentState, repository: JobRepository
) -> AgentState:
    matched_jobs = search_jobs(repository, state.get("search_filters", {}), state.get("resume_profile"))
    return {**state, "matched_jobs": matched_jobs}


def create_application(
    state: AgentState, repository: JobRepository, session: Session
) -> AgentState:
    job_id = resolve_visible_job(state["message"], state.get("visible_job_ids", []), repository)
    if not job_id:
        return {
            **state,
            "reply": "Please specify a displayed job number, for example, 'Apply to job 1'.",
            "errors": ["ambiguous_job_reference"],
        }
    if not re.search(r"\b(apply|submit)\b", state["message"].casefold()):
        return {**state, "reply": "I can show application records, but I need an explicit request to apply."}
    try:
        result = apply_to_job(repository, session, job_id)
        return {
            **state,
            "application_result": result,
            "reply": f"Recorded a simulated application for {result.job_title_snapshot} at {result.company_snapshot}. "
            "This was saved locally and was not sent to the employer.",
        }
    except DuplicateApplicationError:
        return {**state, "reply": "You already have a simulated application recorded for that job.", "errors": ["duplicate_application"]}
    except UnknownJobError:
        return {**state, "reply": "That job no longer exists in the current dataset.", "errors": ["unknown_job"]}


def track_applications(state: AgentState, repository: JobRepository, session: Session) -> AgentState:
    applications = list_applications(repository, session)
    return {
        **state,
        "applications": applications,
        "reply": f"You have {len(applications)} locally recorded simulated application(s).",
    }


def respond(state: AgentState) -> AgentState:
    if state.get("reply"):
        return state
    if state.get("intent") == "general":
        return {
            **state,
            "reply": "I can help parse a resume, find matching jobs, and track simulated applications. "
            "Upload a resume or ask for jobs such as 'show remote Python roles'.",
        }
    jobs = state.get("matched_jobs", [])
    if not jobs:
        return {**state, "reply": "I could not find matching jobs in the current dataset."}
    return {
        **state,
        "reply": (
            f"I found {len(jobs)} matching job(s) with personalized match scores."
            if state.get("resume_profile")
            else f"I found {len(jobs)} matching job(s). Upload a resume to see personalized match scores."
        ),
    }


def build_graph(repository: JobRepository, session_factory: Callable[[], Session]):
    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("interpret_search_preferences", interpret_search_preferences)
    graph.add_node("filter_and_rank_jobs", lambda state: filter_and_rank_jobs(state, repository))
    graph.add_node("create_application", lambda state: create_application(state, repository, session_factory()))
    graph.add_node("track_applications", lambda state: track_applications(state, repository, session_factory()))
    graph.add_node("respond", respond)
    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        lambda state: state["intent"],
        {
            "job_search": "interpret_search_preferences",
            "application": "create_application",
            "application_tracking": "track_applications",
            "general": "respond",
        },
    )
    graph.add_edge("interpret_search_preferences", "filter_and_rank_jobs")
    graph.add_edge("filter_and_rank_jobs", "respond")
    graph.add_edge("create_application", "respond")
    graph.add_edge("track_applications", "respond")
    graph.add_edge("respond", END)
    return graph.compile()


def run_chat(
    repository: JobRepository,
    session_factory: Callable[[], Session],
    *,
    message: str,
    conversation_id: str | None,
    resume_profile,
    visible_job_ids: list[str],
) -> ChatResponse:
    graph = build_graph(repository, session_factory)
    result = graph.invoke(
        {
            "message": message,
            "resume_profile": resume_profile,
            "visible_job_ids": visible_job_ids,
            "errors": [],
        }
    )
    jobs = result.get("matched_jobs", [])
    return ChatResponse(
        conversation_id=conversation_id or str(uuid.uuid4()),
        reply=result.get("reply", ""),
        intent=result.get("intent", "general"),
        jobs=jobs,
        resume_profile=resume_profile,
        applications=result.get("applications", []),
        errors=result.get("errors", []),
    )
