"""
OCR module for extracting text from scanned images.
Uses pytesseract (Tesseract OCR) with image preprocessing for better accuracy.
"""

from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
from config import TESSERACT_CMD

# Set tesseract command path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR accuracy.
    Applies grayscale conversion, contrast enhancement, sharpening, and binarization.
    """
    # Convert to grayscale
    if image.mode != "L":
        image = image.convert("L")
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)
    
    # Upscale small images for better OCR
    width, height = image.size
    if width < 1500:
        scale = 1500 / width
        new_size = (int(width * scale), int(height * scale))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Binarize using a threshold
    threshold = 140
    image = image.point(lambda p: 255 if p > threshold else 0)
    
    return image


def extract_text_from_image(file_path: str | Path) -> str:
    """
    Extract text from an image file using Tesseract OCR.
    
    Args:
        file_path: Path to the image file.
        
    Returns:
        Extracted text from the image.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    image = Image.open(str(file_path))
    
    # Preprocess for better accuracy
    processed = preprocess_image(image)
    
    # Run OCR with optimized configuration
    custom_config = r"--oem 3 --psm 6 -l eng"
    text = pytesseract.image_to_string(processed, config=custom_config)
    
    # Also try with original image and merge if needed
    text_original = pytesseract.image_to_string(image, config=r"--oem 3 --psm 6 -l eng")
    
    # Use whichever extracted more text
    if len(text_original.strip()) > len(text.strip()):
        return text_original.strip()
    
    return text.strip()
