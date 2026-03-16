"""
Configuration for MetaExtract — Document Metadata Extraction system.
Supports multiple LLM providers with auto-detection.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TRAIN_DIR = DATA_DIR / "train"
TEST_DIR = DATA_DIR / "test"
TRAIN_CSV = DATA_DIR / "train.csv"
TEST_CSV = DATA_DIR / "test.csv"
PREDICTIONS_DIR = BASE_DIR / "predictions"

# Tesseract OCR path (Windows default; adjust if needed)
TESSERACT_CMD = "/opt/homebrew/bin/tesseract"  # Change to r"C:\Program Files\Tesseract-OCR\tesseract.exe" on Windows

# ── LLM Provider Configuration ─────────────────────────────────────
# The system auto-detects available providers in this priority order:
#   1. Azure OpenAI  (needs AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT)
#   2. OpenAI  (needs OPENAI_API_KEY)
#   3. Groq    (needs GROQ_API_KEY — free at console.groq.com)
#   4. Ollama  (needs local Ollama running on port 11434)
#
# All use the OpenAI-compatible chat completions API.

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")

# Standard OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = "https://api.openai.com/v1"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Upload settings
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_FILE_SIZE_MB = 20
ALLOWED_EXTENSIONS = {".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".pdf"}

# CORS origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
]
