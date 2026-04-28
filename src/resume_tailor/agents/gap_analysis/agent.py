"""Gap Analysis Agent.

Calls the LlamaIndex OpenAI wrapper to classify every JD requirement against the
candidate's CV profile into strong_matches, weak_matches, or gaps. Structured output
is enforced via the GapAnalysis Pydantic model.
"""

import logging
import os
import time

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, ConfigDict, ValidationError

from resume_tailor.agents.gap_analysis.prompts import SYSTEM_PROMPT, build_user_prompt

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


class WeakMatch(BaseModel):
    model_config = ConfigDict(extra="ignore")
    requirement: str
    evidence: str
    user_note: str | None = None


class Gap(BaseModel):
    model_config = ConfigDict(extra="ignore")
    requirement: str
    acknowledged: bool = False


class GapAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    strong_matches: list[str]
    weak_matches: list[WeakMatch]
    gaps: list[Gap]


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------


class GapAnalysisError(Exception):
    """Base error for the gap analysis agent."""


class GapAnalysisParseError(GapAnalysisError):
    """Raised when the LLM response cannot be parsed."""


class GapAnalysisValidationError(GapAnalysisError):
    """Raised when the LLM response is valid JSON but does not match the expected schema."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyse_gaps(
    jd_profile: dict,
    cv_profile: dict,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float | None = None,
) -> dict:
    """Classify every JD requirement against the CV profile.

    Args:
        jd_profile: Structured JD profile dict from extract_jd().
        cv_profile: Structured CV profile dict from extract_cv().
        model: OpenAI model identifier.
        temperature: Sampling temperature. Pass 0.0 for deterministic output (evals).

    Returns:
        Dict with keys: strong_matches, weak_matches, gaps.

    Raises:
        GapAnalysisValidationError: LLM response failed schema validation.
        GapAnalysisParseError: LLM response could not be parsed at all.
    """
    logger.info("Gap analysis started (model=%s)", model)
    start = time.monotonic()

    user_prompt = build_user_prompt(jd_profile, cv_profile)
    logger.debug("Prompt sent:\n%s", user_prompt)

    try:
        llm_kwargs = {"model": model}
        if temperature is not None:
            llm_kwargs["temperature"] = temperature
        llm = OpenAI(**llm_kwargs)
        profile: GapAnalysis = llm.structured_predict(
            GapAnalysis,
            _CHAT_TEMPLATE,
            user_prompt=user_prompt,
        )
        logger.debug("Structured result: %s", profile)

    except ValidationError as exc:
        duration = time.monotonic() - start
        logger.info("Gap analysis failed after %.2fs: %s", duration, type(exc).__name__)
        raise GapAnalysisValidationError(f"LLM response failed schema validation: {exc}") from exc
    except Exception as exc:
        duration = time.monotonic() - start
        logger.info("Gap analysis failed after %.2fs: %s", duration, type(exc).__name__)
        raise GapAnalysisParseError(f"Gap analysis failed: {exc}") from exc

    duration = time.monotonic() - start
    logger.info("Gap analysis completed in %.2fs", duration)
    return profile.model_dump()
