import html
import re
from datetime import datetime, timezone
from html.parser import HTMLParser


class _HTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    parser = _HTMLTextParser()
    parser.feed(html.unescape(value))
    return " ".join("".join(parser.parts).split())


def parse_datetime(value: str | int | float | None) -> datetime | None:
    if not value:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def infer_work_mode(text: str) -> str:
    lowered = text.casefold()
    if re.search(r"\b(remote|work from home|wfh)\b", lowered):
        return "remote"
    if "hybrid" in lowered:
        return "hybrid"
    if re.search(r"\b(on[- ]site|onsite|in office)\b", lowered):
        return "on-site"
    return "unspecified"


def infer_experience(text: str) -> str | None:
    match = re.search(
        r"\b(\d+\s*(?:\+|plus)\s*years?|\d+\s*(?:-|to)\s*\d+\s*years?)\b",
        text.casefold(),
    )
    return " ".join(match.group(1).split()) if match else None


def infer_skills(text: str) -> list[str]:
    known_skills = (
        "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js",
        "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB",
        "AWS", "Azure", "Docker", "Kubernetes", "Go", "C#", ".NET",
        "Machine Learning", "Data Science", "GraphQL", "REST APIs",
    )
    lowered = text.casefold()
    return [skill for skill in known_skills if skill.casefold() in lowered]
