
import json
import re
import time
from pathlib import Path
from typing import Any

from .config import GEMINI_API_KEY, GEMINI_MODEL


PROMPT = """
Extract facts from the business text into one JSON object.

Rules:
- Never invent identity, tax, bank, financial, employee or address facts.
- Use null for absent or unclear values.
- Preserve activity descriptions.
- Include missing_or_unclear and conflicts arrays.
- Return valid JSON only.

Use these keys:
entrepreneur_name, date_of_birth, enterprise_name, organisation_type,
social_category, gender, differently_abled, commencement_date,
office_address, units, email, mobile, major_activity,
activity_descriptions, existing_nic_codes, employees, investment,
turnover, export_turnover, financial_year, pan_available,
gstin_status, itr_filed, previous_udyam, missing_or_unclear, conflicts.
"""


def read_input(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    return path.read_text(encoding="utf-8")


def _parse_json(text: str) -> dict[str, Any]:
    text = text.strip()

    # Remove optional Markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    result = json.loads(text)

    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object.")

    return result


def extract_business_data(text: str) -> dict[str, Any]:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY missing. Copy .env.example to .env and add a key."
        )

    from google import genai
    from google.genai import errors

    client = genai.Client(api_key=GEMINI_API_KEY)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    PROMPT,
                    "SOURCE BUSINESS TEXT:\n" + text
                ],
                config={
                    "response_mime_type": "application/json"
                },
            )

            return _parse_json(response.text or "")

        except errors.ServerError as error:
            if attempt == 2:
                raise RuntimeError(
                    "Gemini is temporarily unavailable after 3 attempts. "
                    "Please try again later."
                ) from error

            wait_seconds = 5 * (attempt + 1)

            print(
                f"Gemini server unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)
