"""
MetaExtract — FastAPI backend for Document Metadata Extraction.
RESTful API that accepts document uploads and returns extracted metadata.
"""

import csv
import io
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import (
    CORS_ORIGINS,
    UPLOAD_DIR,
    MAX_FILE_SIZE_MB,
    ALLOWED_EXTENSIONS,
    PREDICTIONS_DIR,
)
from models import (
    ExtractionResponse,
    HealthResponse,
    BatchExtractionRequest,
    EvaluationResponse,
)
from extractor import process_document
from evaluate import evaluate_on_dataset, generate_predictions
from llm_extractor import detect_provider, get_provider_name

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: setup and teardown."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    provider = get_provider_name()
    if provider:
        logger.info(f"MetaExtract API started — LLM provider: {provider}")
    else:
        logger.warning(
            "MetaExtract API started — NO LLM provider available! "
            "Set OPENAI_API_KEY, GROQ_API_KEY, or run Ollama."
        )
    yield
    logger.info("Shutting down MetaExtract...")


app = FastAPI(
    title="MetaExtract API",
    description=(
        "AI/ML system to extract metadata (Agreement Value, Start Date, End Date, "
        "Renewal Notice Days, Party One, Party Two) from rental agreement documents. "
        "Supports .docx and scanned image (.png) uploads. "
        "Uses LLM-based extraction (OpenAI / Groq / Ollama)."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ──────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    provider = get_provider_name()
    if provider:
        return HealthResponse(
            status="healthy",
            message=f"MetaExtract API is running (LLM: {provider})",
            provider=provider,
        )
    return HealthResponse(
        status="degraded",
        message=(
            "MetaExtract API is running but NO LLM provider configured. "
            "Set OPENAI_API_KEY, GROQ_API_KEY, or run Ollama locally."
        ),
        provider=None,
    )


# ── Single File Extraction ──────────────────────────────────────────
@app.post("/extract", response_model=ExtractionResponse)
async def extract_metadata(file: UploadFile = File(...)):
    """Upload a document and extract metadata."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB",
        )

    upload_path = UPLOAD_DIR / file.filename
    try:
        with open(upload_path, "wb") as f:
            f.write(contents)
        result = process_document(upload_path)
        return result
    except Exception as e:
        logger.error(f"Error processing upload {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if upload_path.exists():
            upload_path.unlink()


# ── Batch Extraction ────────────────────────────────────────────────
@app.post("/batch-extract")
async def batch_extract(request: BatchExtractionRequest):
    """Run extraction on all files in train/test folder."""
    if request.folder not in ("train", "test"):
        raise HTTPException(status_code=400, detail="Folder must be 'train' or 'test'")

    provider = get_provider_name()
    predictions = generate_predictions(request.folder)
    return {
        "folder": request.folder,
        "predictions": predictions,
        "count": len(predictions),
        "provider": provider,
    }


# ── Evaluate ────────────────────────────────────────────────────────
@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: BatchExtractionRequest):
    """Evaluate extraction performance with per-field recall."""
    if request.folder not in ("train", "test"):
        raise HTTPException(status_code=400, detail="Folder must be 'train' or 'test'")

    result = evaluate_on_dataset(request.folder)
    return result


# ── Predict Test CSV ────────────────────────────────────────────────
@app.post("/predict-test-csv")
async def predict_test_csv():
    """Generate predictions for the test set and return as downloadable CSV."""
    predictions = generate_predictions("test")

    fieldnames = [
        "File Name", "Aggrement Value", "Aggrement Start Date",
        "Aggrement End Date", "Renewal Notice (Days)", "Party One", "Party Two",
    ]

    # Save to disk
    output_path = PREDICTIONS_DIR / "test_predictions.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(predictions)

    # Return as streaming response
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(predictions)

    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=test_predictions.csv"},
    )


# ── Provider Info ───────────────────────────────────────────────────
@app.get("/provider")
async def provider_info():
    """Return info about the active LLM provider."""
    p = detect_provider()
    if p:
        name, _, _, model, _ = p  # Unpack all 5 values (added endpoint)
        return {"provider": name, "model": model, "available": True}
    return {
        "provider": None,
        "model": None,
        "available": False,
        "help": "Set OPENAI_API_KEY, GROQ_API_KEY, or run Ollama locally.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
