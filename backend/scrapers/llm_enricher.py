"""LLM enrichment layer — wraps Gemini CLI for data cleaning and scoring."""

import subprocess
import json
import logging
import shutil
import platform

logger = logging.getLogger(__name__)


def _find_gemini_cmd() -> str:
    """Find the Gemini CLI executable."""
    if platform.system() == "Windows":
        candidates = ["gemini.cmd", "gemini.exe", "gemini"]
    else:
        candidates = ["gemini"]

    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return "gemini"


GEMINI_CMD = _find_gemini_cmd()


def parse_with_gemini(
    data_dict: dict,
    expected_keys: list[str],
    context: str = "",
    timeout: int = 25,
) -> dict:
    """
    Call Gemini CLI to clean and enrich data.

    Falls back to original data_dict on any error.
    """
    prompt_parts = [
        "You are an expert data analyst. Clean the following data, fix typos, and infer any missing details.",
        f"Return ONLY valid JSON with these exact keys: {expected_keys}",
        "Do NOT use markdown backticks. Return raw JSON only.",
    ]
    if context:
        prompt_parts.append(f"Context: {context}")
    prompt_parts.append(f"Data: {json.dumps(data_dict)}")

    full_prompt = "\n".join(prompt_parts)

    try:
        result = subprocess.run(
            [GEMINI_CMD],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()

        # Strip markdown fences if present
        if output.startswith("```"):
            lines = output.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            output = "\n".join(lines).strip()

        parsed = json.loads(output)

        # Validate expected keys
        for key in expected_keys:
            if key not in parsed:
                parsed[key] = data_dict.get(key, "")

        return parsed

    except subprocess.TimeoutExpired:
        logger.warning("Gemini CLI timed out after %ds", timeout)
        return data_dict
    except json.JSONDecodeError as e:
        logger.warning("Gemini returned invalid JSON: %s", e)
        return data_dict
    except FileNotFoundError:
        logger.error("Gemini CLI not found. Install it or update config.")
        return data_dict
    except Exception as e:
        logger.warning("Gemini enrichment failed: %s", e)
        return data_dict


def enrich_job_lead(
    raw_title: str,
    raw_company: str,
    raw_location: str,
    raw_description: str = "",
) -> dict:
    """Enrich a job posting with LLM."""
    data = {
        "title": raw_title,
        "company": raw_company,
        "location": raw_location,
        "description": raw_description[:500],
    }
    context = (
        "This is a job/freelance posting. Determine:\n"
        "- clean_title: cleaned job title\n"
        "- company: exact company name\n"
        '- country: exact country from location (or "Unknown")\n'
        '- city: exact city from location (or "Unknown")\n'
        "- service_needed: e.g., 3D Animation, Motion Design, Product Render, WebGL\n"
        '- priority: "A+" if mentions 3D/CGI/Unreal/Motion with high urgency, else "A" or "B"'
    )
    keys = ["clean_title", "company", "country", "city", "service_needed", "priority"]
    return parse_with_gemini(data, keys, context)


def enrich_startup_lead(
    raw_headline: str,
    raw_date: str,
    article_url: str = "",
) -> dict:
    """Enrich a startup funding headline with LLM."""
    data = {
        "headline": raw_headline,
        "date": raw_date,
        "url": article_url,
    }
    context = (
        "This is a startup funding news headline, likely from MENA region.\n"
        "Extract:\n"
        "- company: exact startup/company name\n"
        '- country: country (or "Unknown")\n'
        '- city: city (or "Unknown")\n'
        '- demand_signal: e.g., "Raised $5M Seed" or funding summary'
    )
    keys = ["company", "country", "city", "demand_signal"]
    return parse_with_gemini(data, keys, context)
