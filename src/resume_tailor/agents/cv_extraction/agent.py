"""CV Extraction Agent.

Calls the LlamaIndex OpenAI wrapper to parse raw CV text into a structured
profile used by the downstream gap-analysis step. Structured output is enforced via
the CVProfile Pydantic model — no manual JSON parsing required.

The model is read from the RESUME_TAILOR_MODEL environment variable, falling back
to gpt-5.4-mini if unset.
"""

import logging
import os
import time

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, ConfigDict, ValidationError

from resume_tailor.agents.cv_extraction.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("RESUME_TAILOR_MODEL", "gpt-5.4-mini")

_CHAT_TEMPLATE = ChatPromptTemplate(
    message_templates=[
        ChatMessage(role=MessageRole.SYSTEM, content=SYSTEM_PROMPT),
        ChatMessage(role=MessageRole.USER, content="{user_prompt}"),
    ]
)


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------


class PersonalInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    website: str = ""


class EducationEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    degree: str = ""
    institution: str = ""
    year: str = ""
    gpa: str = ""


class ExperienceEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role: str = ""
    organisation: str = ""
    start_date: str = ""
    end_date: str = ""
    responsibilities: list[str] = []
    achievements: list[str] = []
    skills_demonstrated: list[str] = []


class PublicationEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    venue: str = ""
    year: str = ""
    authors: list[str] = []


class ProjectEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = ""
    description: str = ""
    technologies: list[str] = []
    url: str = ""


class AwardEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    issuer: str = ""
    year: str = ""
    description: str = ""


class SkillsSection(BaseModel):
    model_config = ConfigDict(extra="ignore")

    technical: list[str] = []
    domain: list[str] = []
    soft: list[str] = []


class OtherEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    section: str = ""
    items: list[str] = []


class CVProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    personal: PersonalInfo = PersonalInfo()
    education: list[EducationEntry] = []
    experience: list[ExperienceEntry] = []
    publications: list[PublicationEntry] = []
    projects: list[ProjectEntry] = []
    awards: list[AwardEntry] = []
    skills: SkillsSection = SkillsSection()
    other: list[OtherEntry] = []


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------


class CVExtractionError(Exception):
    """Base error for the CV extraction agent."""


class CVExtractionParseError(CVExtractionError):
    """Raised when the LLM response cannot be parsed as a valid CV profile."""


class CVExtractionValidationError(CVExtractionError):
    """Raised when the LLM response is valid JSON but does not match the expected schema."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_cv(
    cv_text: str, *, model: str = DEFAULT_MODEL, temperature: float | None = None
) -> dict:
    """Extract a structured CV profile from raw CV text.

    Args:
        cv_text: Raw text of the CV.
        model: OpenAI model identifier to use for extraction.
        temperature: Sampling temperature. Pass 0.0 for deterministic output (e.g. evals).

    Returns:
        A dict with keys: personal, education, experience, publications, projects,
        awards, skills, other.

    Raises:
        CVExtractionValidationError: If the LLM response does not match the CVProfile schema.
        CVExtractionParseError: If the LLM response cannot be parsed at all.
    """
    logger.info("CV extraction started (model=%s)", model)
    start = time.monotonic()

    user_prompt = build_user_prompt(cv_text)
    logger.debug("Prompt sent:\n%s", user_prompt)

    try:
        llm_kwargs = {"model": model}
        if temperature is not None:
            llm_kwargs["temperature"] = temperature
        llm = OpenAI(**llm_kwargs)
        profile: CVProfile = llm.structured_predict(
            CVProfile,
            _CHAT_TEMPLATE,
            user_prompt=user_prompt,
        )
        logger.debug("Structured result: %s", profile)

    except ValidationError as exc:
        duration = time.monotonic() - start
        logger.info("CV extraction failed after %.2fs: %s", duration, type(exc).__name__)
        raise CVExtractionValidationError(f"LLM response failed schema validation: {exc}") from exc
    except Exception as exc:
        duration = time.monotonic() - start
        logger.info("CV extraction failed after %.2fs: %s", duration, type(exc).__name__)
        raise CVExtractionParseError(f"CV extraction failed: {exc}") from exc

    duration = time.monotonic() - start
    logger.info("CV extraction completed in %.2fs", duration)
    return profile.model_dump()
