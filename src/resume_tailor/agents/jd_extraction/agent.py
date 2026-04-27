"""JD Extraction Agent.

Calls an OpenAI LLM (gpt-4o-mini) to parse a raw job description into a structured
profile used by the downstream gap-analysis step.

Note: The backlog listed "gpt-5.4-mini" which is not a real OpenAI model.
gpt-4o-mini has been substituted as the default.
"""

import json
import logging
import time

import openai

from resume_tailor.agents.jd_extraction.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"

REQUIRED_FIELDS: dict[str, type] = {
    "role_title": str,
    "seniority": str,
    "hard_requirements": list,
    "nice_to_haves": list,
    "culture_signals": list,
}


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------


class JDExtractionError(Exception):
    """Base error for the JD extraction agent."""


class JDExtractionParseError(JDExtractionError):
    """Raised when the LLM response cannot be parsed as JSON."""


class JDExtractionValidationError(JDExtractionError):
    """Raised when the LLM response is valid JSON but does not match the expected schema."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_jd(jd_text: str, *, model: str = DEFAULT_MODEL) -> dict:
    """Extract a structured JD profile from raw job description text.

    Args:
        jd_text: Raw text of the job description.
        model: OpenAI model identifier to use for extraction.

    Returns:
        A dict with keys: role_title, seniority, hard_requirements,
        nice_to_haves, culture_signals.

    Raises:
        JDExtractionParseError: If the LLM response cannot be parsed as JSON.
        JDExtractionValidationError: If the response JSON does not match the expected schema.
    """
    logger.info("JD extraction started (model=%s)", model)
    start = time.monotonic()

    user_prompt = build_user_prompt(jd_text)
    logger.debug("Prompt sent:\n%s", user_prompt)

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_content = response.choices[0].message.content
        logger.debug("Raw response:\n%s", raw_content)

        result = _parse_response(raw_content)

    except Exception as exc:
        duration = time.monotonic() - start
        logger.info(
            "JD extraction failed after %.2fs: %s",
            duration,
            type(exc).__name__,
        )
        raise

    duration = time.monotonic() - start
    logger.info("JD extraction completed in %.2fs", duration)
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_response(raw_content: str) -> dict:
    """Parse and validate the raw LLM response string.

    Args:
        raw_content: The raw string returned by the LLM.

    Returns:
        Validated dict matching the JD profile schema.

    Raises:
        JDExtractionParseError: If ``raw_content`` is not valid JSON.
        JDExtractionValidationError: If the JSON does not conform to the expected schema.
    """
    try:
        data = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise JDExtractionParseError(
            f"LLM response is not valid JSON: {exc!r}\nRaw content: {raw_content!r}"
        ) from exc

    if not isinstance(data, dict):
        raise JDExtractionValidationError(
            f"Expected a JSON object at the top level, got {type(data).__name__!r}"
        )

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise JDExtractionValidationError(
            f"LLM response is missing required fields: {missing!r}\nGot keys: {list(data.keys())!r}"
        )

    type_errors = []
    for field, expected_type in REQUIRED_FIELDS.items():
        if not isinstance(data[field], expected_type):
            type_errors.append(
                f"  {field!r}: expected {expected_type.__name__}, "
                f"got {type(data[field]).__name__!r}"
            )
    if type_errors:
        raise JDExtractionValidationError(
            "LLM response has fields with wrong types:\n" + "\n".join(type_errors)
        )

    return {field: data[field] for field in REQUIRED_FIELDS}
