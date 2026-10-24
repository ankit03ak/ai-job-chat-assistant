from langchain_core.prompts import ChatPromptTemplate

from app.schemas.resume import ResumeProfile


class ResumeProfileError(RuntimeError):
    """Raised when structured resume extraction cannot be completed."""


class ResumeProfileService:
    def __init__(self, api_key: str | None, model: str | None) -> None:
        self.api_key = api_key
        self.model = model

    def extract_profile(self, text: str) -> ResumeProfile:
        if not self.api_key or not self.model:
            raise ResumeProfileError(
                "Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL to parse resumes."
            )
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=0,
            ).with_structured_output(ResumeProfile)
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "Extract only facts present in the resume. Use null or empty lists when absent. "
                        "Do not infer contact details or experience.",
                    ),
                    ("human", "{resume_text}"),
                ]
            )
            result = (prompt | llm).invoke({"resume_text": text})
            profile = result if isinstance(result, ResumeProfile) else ResumeProfile.model_validate(result)
        except ResumeProfileError:
            raise
        except Exception as exc:
            raise ResumeProfileError("Gemini could not produce a valid resume profile.") from exc
        profile.raw_text_available = True
        return profile
