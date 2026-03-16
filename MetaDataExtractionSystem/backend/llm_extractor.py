"""
LLM-based metadata extraction with multi-provider support.
Tries providers in order: OpenAI → Groq → Ollama.
Uses the OpenAI-compatible API for all three.
Supports vision-based extraction for images (no Tesseract needed).
"""

import base64
import json
import logging
import httpx
from pathlib import Path
from openai import OpenAI, AzureOpenAI
from config import (
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL,
    GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
)
from models import ExtractionResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert document analyst specializing in rental and lease agreements.
Your task is to extract specific metadata from the provided document text.

You must extract the following fields:
1. **Agreement Value**: The monthly rent or agreement monetary value (just the number, no currency symbols)
2. **Agreement Start Date**: The start date of the agreement in DD.MM.YYYY format
3. **Agreement End Date**: The end date of the agreement in DD.MM.YYYY format
4. **Renewal Notice (Days)**: The number of days required for renewal notice (just the number)
5. **Party One**: The first party (typically the landlord/owner). Include their full name exactly as written.
6. **Party Two**: The second party (typically the tenant/renter). Include their full name exactly as written.

IMPORTANT RULES:
- Return dates strictly in DD.MM.YYYY format (e.g., 01.04.2008). Always use two digits for day and month.
- For Agreement Value, return only the numeric value (e.g., 12000), no commas, no currency.
- For Renewal Notice, return only the number of days (e.g., 60).
- For Party names, return the full names exactly as they appear. Preserve case and punctuation.
- If a field cannot be determined from the text, return null for that field.
- Do NOT invent or guess values that are not clearly stated in the document.
- Pay close attention to who is the owner/landlord (Party One) vs. tenant (Party Two).
  The owner/landlord is the person who owns the property. The tenant is the person renting it.
- The agreement value usually refers to the monthly rent amount.
- Look for phrases like "rent", "monthly rent", "consideration", "rental fee" for the value.
- Look for "commencing", "effective from", "beginning from" for start dates.
- Look for "expiring", "ending on", "terminating" for end dates.
- Look for "notice period", "days notice", "advance notice" for renewal days.

Respond ONLY with a valid JSON object:
{
    "agreement_value": "<value or null>",
    "agreement_start_date": "<DD.MM.YYYY or null>",
    "agreement_end_date": "<DD.MM.YYYY or null>",
    "renewal_notice_days": "<days or null>",
    "party_one": "<name or null>",
    "party_two": "<name or null>"
}"""


def _check_ollama_available() -> bool:
    """Check if Ollama is running and reachable."""
    try:
        base = OLLAMA_BASE_URL.replace("/v1", "")
        r = httpx.get(f"{base}/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


def detect_provider() -> tuple[str, str, str, str, str | None] | None:
    """
    Auto-detect available LLM provider.
    Returns (name, api_key, base_url, model, endpoint) or None.
    For Azure, endpoint is the Azure endpoint; for others it's None.
    """
    if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
        return ("Azure OpenAI", AZURE_OPENAI_API_KEY, "", AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_ENDPOINT)
    if OPENAI_API_KEY:
        return ("OpenAI", OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, None)
    if GROQ_API_KEY:
        return ("Groq", GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, None)
    if _check_ollama_available():
        return ("Ollama", "ollama", OLLAMA_BASE_URL, OLLAMA_MODEL, None)
    return None


def get_provider_name() -> str | None:
    """Return the name of the active provider, or None."""
    p = detect_provider()
    return p[0] if p else None


def extract_metadata_with_llm(document_text: str, filename: str = "") -> ExtractionResult:
    """
    Use an LLM to extract metadata from document text.
    Automatically selects the first available provider.
    """
    provider = detect_provider()
    if provider is None:
        raise ValueError(
            "No LLM provider configured. Set one of: "
            "AZURE_OPENAI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, or run Ollama locally."
        )

    name, api_key, base_url, model, endpoint = provider
    logger.info(f"Using LLM provider: {name} ({model})")

    # Create appropriate client based on provider
    if name == "Azure OpenAI":
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=AZURE_OPENAI_API_VERSION,
        )
    else:
        client = OpenAI(api_key=api_key, base_url=base_url)

    user_message = f"""Extract the metadata from the following rental agreement document.

Document filename: {filename}

--- DOCUMENT TEXT START ---
{document_text[:6000]}
--- DOCUMENT TEXT END ---

Extract: Agreement Value, Agreement Start Date, Agreement End Date, Renewal Notice (Days), Party One, Party Two.
Return ONLY the JSON object."""

    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.0,
        "max_tokens": 500,
        "timeout": 60.0,
    }

    # Azure OpenAI, OpenAI and Groq support response_format; Ollama may not
    if name in ("Azure OpenAI", "OpenAI", "Groq"):
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content.strip()
        logger.info(f"LLM response for {filename}: {content}")

        # Extract JSON from response (handle models that wrap in markdown)
        json_str = content
        if "```" in json_str:
            # Strip markdown code fences
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start != -1 and end > start:
                json_str = json_str[start:end]

        parsed = json.loads(json_str)

        return ExtractionResult(
            agreement_value=_clean_value(parsed.get("agreement_value")),
            agreement_start_date=_clean_value(parsed.get("agreement_start_date")),
            agreement_end_date=_clean_value(parsed.get("agreement_end_date")),
            renewal_notice_days=_clean_value(parsed.get("renewal_notice_days")),
            party_one=_clean_value(parsed.get("party_one")),
            party_two=_clean_value(parsed.get("party_two")),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON for {filename}: {e}")
        logger.error(f"Raw response: {content}")
        raise ValueError(f"LLM returned invalid JSON: {e}")
    except Exception as e:
        logger.error(f"LLM extraction failed for {filename}: {e}")
        raise


def _clean_value(value) -> str | None:
    """Clean an extracted value, converting to string and handling nulls."""
    if value is None:
        return None
    value = str(value).strip()
    if value.lower() in ("null", "none", "n/a", "na", ""):
        return None
    return value


def extract_metadata_from_image(image_path: Path) -> ExtractionResult:
    """
    Extract metadata directly from an image using LLM vision capabilities.
    Used as fallback when Tesseract OCR is not available.
    Sends the image as base64 to GPT-4o's vision API.
    """
    provider = detect_provider()
    if provider is None:
        raise ValueError(
            "No LLM provider configured. Set one of: "
            "AZURE_OPENAI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, or run Ollama locally."
        )

    name, api_key, base_url, model, endpoint = provider
    logger.info(f"Using LLM vision for {image_path.name} via {name} ({model})")

    # Read and encode image
    image_data = image_path.read_bytes()
    b64 = base64.b64encode(image_data).decode("utf-8")

    # Detect MIME type
    suffix = image_path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".tiff": "image/tiff", ".bmp": "image/bmp"}
    mime = mime_map.get(suffix, "image/png")

    # Create appropriate client based on provider
    if name == "Azure OpenAI":
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=AZURE_OPENAI_API_VERSION,
        )
    else:
        client = OpenAI(api_key=api_key, base_url=base_url)

    # Use a vision-capable model — GPT-4o supports vision
    vision_model = model
    if name in ("Azure OpenAI", "OpenAI") and "gpt" in model.lower():
        vision_model = model  # gpt-4o already supports vision

    user_content = [
        {
            "type": "text",
            "text": (
                "This is a scanned rental/lease agreement document. "
                "Extract the following metadata from this image:\n"
                "1. Agreement Value (monthly rent, numeric only)\n"
                "2. Agreement Start Date (DD.MM.YYYY)\n"
                "3. Agreement End Date (DD.MM.YYYY)\n"
                "4. Renewal Notice Days (number only)\n"
                "5. Party One (landlord/owner full name)\n"
                "6. Party Two (tenant full name)\n\n"
                "Return ONLY a JSON object with these keys: "
                "agreement_value, agreement_start_date, agreement_end_date, "
                "renewal_notice_days, party_one, party_two. "
                "Use null for fields you cannot determine."
            ),
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
        },
    ]

    kwargs: dict = {
        "model": vision_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.0,
        "max_tokens": 500,
        "timeout": 90.0,
    }

    if name in ("Azure OpenAI", "OpenAI", "Groq"):
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content.strip()
        logger.info(f"Vision LLM response for {image_path.name}: {content}")

        json_str = content
        if "```" in json_str:
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start != -1 and end > start:
                json_str = json_str[start:end]

        parsed = json.loads(json_str)

        return ExtractionResult(
            agreement_value=_clean_value(parsed.get("agreement_value")),
            agreement_start_date=_clean_value(parsed.get("agreement_start_date")),
            agreement_end_date=_clean_value(parsed.get("agreement_end_date")),
            renewal_notice_days=_clean_value(parsed.get("renewal_notice_days")),
            party_one=_clean_value(parsed.get("party_one")),
            party_two=_clean_value(parsed.get("party_two")),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse vision LLM JSON for {image_path.name}: {e}")
        raise ValueError(f"LLM returned invalid JSON: {e}")
    except Exception as e:
        logger.error(f"Vision LLM extraction failed for {image_path.name}: {e}")
        raise
    return value
