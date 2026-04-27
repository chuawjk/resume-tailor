"""JD Extraction Agent.

Calls the LlamaIndex OpenAI wrapper to parse a raw job description into a structured
profile used by the downstream gap-analysis step. Structured output is enforced via
the JDProfile Pydantic model — no manual JSON parsing required.

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

from resume_tailor.agents.jd_extraction.prompts import SYSTEM_PROMPT, build_user_prompt

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


class JDProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role_title: str
    seniority: str
    hard_requirements: list[str]
    nice_to_haves: list[str]
    culture_signals: list[str]


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------


class JDExtractionError(Exception):
    """Base error for the JD extraction agent."""


class JDExtractionParseError(JDExtractionError):
    """Raised when the LLM response cannot be parsed as a valid JD profile."""


class JDExtractionValidationError(JDExtractionError):
    """Raised when the LLM response is valid JSON but does not match the expected schema."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_jd(
    jd_text: str, *, model: str = DEFAULT_MODEL, temperature: float | None = None
) -> dict:
    """Extract a structured JD profile from raw job description text.

    Args:
        jd_text: Raw text of the job description.
        model: OpenAI model identifier to use for extraction.
        temperature: Sampling temperature. Pass 0.0 for deterministic output (e.g. evals).

    Returns:
        A dict with keys: role_title, seniority, hard_requirements,
        nice_to_haves, culture_signals.

    Raises:
        JDExtractionValidationError: If the LLM response does not match the JDProfile schema.
        JDExtractionParseError: If the LLM response cannot be parsed at all.
    """
    logger.info("JD extraction started (model=%s)", model)
    start = time.monotonic()

    user_prompt = build_user_prompt(jd_text)
    logger.debug("Prompt sent:\n%s", user_prompt)

    try:
        llm_kwargs = {"model": model}
        if temperature is not None:
            llm_kwargs["temperature"] = temperature
        llm = OpenAI(**llm_kwargs)
        profile: JDProfile = llm.structured_predict(
            JDProfile,
            _CHAT_TEMPLATE,
            user_prompt=user_prompt,
        )
        logger.debug("Structured result: %s", profile)

    except ValidationError as exc:
        duration = time.monotonic() - start
        logger.info("JD extraction failed after %.2fs: %s", duration, type(exc).__name__)
        raise JDExtractionValidationError(f"LLM response failed schema validation: {exc}") from exc
    except Exception as exc:
        duration = time.monotonic() - start
        logger.info("JD extraction failed after %.2fs: %s", duration, type(exc).__name__)
        raise JDExtractionParseError(f"JD extraction failed: {exc}") from exc

    duration = time.monotonic() - start
    logger.info("JD extraction completed in %.2fs", duration)
    return profile.model_dump()
