import logging
import os
import re
import tempfile
from pathlib import Path

import pymupdf as fitz
from docx import Document

logger = logging.getLogger(__name__)


class ResumeParseError(ValueError):
    """Raised when a resume cannot be safely extracted."""


_RESUME_MARKERS = (
    "resume",
    "curriculum vitae",
    "professional summary",
    "work experience",
    "employment",
    "education",
    "projects",
    "certifications",
    "technical skills",
    "skills",
)


def validate_resume_text(text: str) -> None:
    normalized = " ".join(text.casefold().split())
    marker_count = sum(marker in normalized for marker in _RESUME_MARKERS)
    has_contact = bool(
        re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE)
        or re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    )
    if marker_count < 2 and not (has_contact and marker_count >= 1):
        raise ResumeParseError(
            "This document does not appear to be a resume. Upload a resume containing "
            "your experience, skills, education, or projects."
        )


def _extract_pdf(path: Path) -> str:
    try:
        with fitz.open(stream=path.read_bytes(), filetype="pdf") as document:
            return "\n".join(page.get_text() for page in document).strip()
    except (OSError, fitz.FileDataError) as exc:
        raise ResumeParseError("The PDF could not be read.") from exc


def _extract_docx(path: Path) -> str:
    try:
        document = Document(path)
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
        return "\n".join(text for text in paragraphs if text).strip()
    except (OSError, ValueError) as exc:
        raise ResumeParseError("The DOCX could not be read.") from exc


def extract_resume_text(content: bytes, filename: str, max_upload_mb: int) -> str:
    suffix = Path(filename).suffix.casefold()
    if suffix not in {".pdf", ".docx"}:
        raise ResumeParseError("Only PDF and DOCX resumes are supported.")
    if len(content) > max_upload_mb * 1024 * 1024:
        raise ResumeParseError(f"Resume exceeds the {max_upload_mb} MB upload limit.")
    if not content:
        raise ResumeParseError("The uploaded resume is empty.")

    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
            temporary_file.write(content)
            temporary_path = temporary_file.name
        path = Path(temporary_path)
        text = _extract_pdf(path) if suffix == ".pdf" else _extract_docx(path)
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except OSError:
                logger.warning("Unable to remove temporary resume file")

    if not text:
        if suffix == ".pdf":
            raise ResumeParseError("This PDF contains no extractable text. An OCR-enabled PDF is required.")
        raise ResumeParseError("The resume contains no extractable text.")
    validate_resume_text(text)
    return text
