"""
Main document processing pipeline.
Orchestrates text extraction (DOCX/OCR) and LLM-based metadata extraction.
Falls back to LLM vision for images when Tesseract OCR is unavailable.
"""

import logging
from pathlib import Path

from docx_parser import extract_text_from_docx
from ocr import extract_text_from_image
from llm_extractor import extract_metadata_with_llm, extract_metadata_from_image, get_provider_name
from models import ExtractionResult, ExtractionResponse
from config import ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)


def get_file_type(file_path: Path) -> str:
    """Determine file type from extension."""
    name_lower = file_path.name.lower()

    # Handle compound extensions like .pdf.docx
    if name_lower.endswith(".pdf.docx"):
        return "docx"

    suffix = file_path.suffix.lower()
    if suffix == ".docx":
        return "docx"
    elif suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return "image"
    elif suffix == ".pdf":
        return "pdf"
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def extract_text(file_path: Path) -> str:
    """Extract text from a document based on its type."""
    file_type = get_file_type(file_path)

    if file_type == "docx":
        logger.info(f"Extracting text from DOCX: {file_path.name}")
        return extract_text_from_docx(file_path)
    elif file_type == "image":
        logger.info(f"Extracting text from image via OCR: {file_path.name}")
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type for extraction: {file_type}")


def process_document(file_path: Path) -> ExtractionResponse:
    """
    Full pipeline: extract text → extract metadata via LLM.
    Returns an ExtractionResponse with either results or an error_message.
    Never raises — errors are captured in the response.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return ExtractionResponse(
            filename=file_path.name,
            status="error",
            error_message=f"File not found: {file_path}",
            metadata=ExtractionResult(),
        )

    # Validate extension
    name_lower = file_path.name.lower()
    suffix_ok = any(name_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS)
    if not suffix_ok:
        return ExtractionResponse(
            filename=file_path.name,
            status="error",
            error_message=f"Unsupported file extension: {file_path.suffix}",
            metadata=ExtractionResult(),
        )

    # Step 1: Text extraction
    file_type = get_file_type(file_path)
    text = None
    try:
        text = extract_text(file_path)
    except Exception as e:
        logger.warning(f"Text extraction failed for {file_path.name}: {e}")
        # For images, fall back to LLM vision instead of failing
        if file_type == "image":
            logger.info(f"Falling back to LLM vision for {file_path.name}")
            try:
                metadata = extract_metadata_from_image(file_path)
                filled = sum(1 for v in metadata.model_dump().values() if v is not None)
                confidence = "high" if filled >= 5 else "medium" if filled >= 3 else "low"
                return ExtractionResponse(
                    filename=file_path.name,
                    status="success",
                    extracted_text_preview="[Extracted via LLM vision — no OCR]",
                    metadata=metadata,
                    confidence=confidence,
                    provider=get_provider_name(),
                )
            except Exception as ve:
                logger.error(f"Vision fallback also failed for {file_path.name}: {ve}")
                return ExtractionResponse(
                    filename=file_path.name,
                    status="error",
                    error_message=f"Both OCR and vision extraction failed: {ve}",
                    metadata=ExtractionResult(),
                )
        else:
            return ExtractionResponse(
                filename=file_path.name,
                status="error",
                error_message=f"Text extraction failed: {e}",
                metadata=ExtractionResult(),
            )

    if not text or len(text.strip()) < 10:
        return ExtractionResponse(
            filename=file_path.name,
            status="warning",
            error_message="Very little text extracted from document",
            extracted_text_preview="[Insufficient text extracted]",
            metadata=ExtractionResult(),
            confidence="low",
        )

    logger.info(f"Extracted {len(text)} characters from {file_path.name}")

    # Step 2: LLM metadata extraction
    try:
        metadata = extract_metadata_with_llm(text, filename=file_path.name)
    except Exception as e:
        logger.error(f"LLM extraction failed for {file_path.name}: {e}")
        return ExtractionResponse(
            filename=file_path.name,
            status="error",
            error_message=str(e),
            extracted_text_preview=text[:500] + ("..." if len(text) > 500 else ""),
            metadata=ExtractionResult(),
            confidence="low",
        )

    # Determine confidence
    filled = sum(1 for v in metadata.model_dump().values() if v is not None)
    if filled >= 5:
        confidence = "high"
    elif filled >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    return ExtractionResponse(
        filename=file_path.name,
        status="success",
        extracted_text_preview=text[:500] + ("..." if len(text) > 500 else ""),
        metadata=metadata,
        confidence=confidence,
        provider=get_provider_name(),
    )
