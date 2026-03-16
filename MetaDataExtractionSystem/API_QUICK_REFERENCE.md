# MetaExtract API - Quick Reference Card

## 🚀 Start Server
```bash
cd backend && python main.py
```
**API Base URL:** http://localhost:8000  
**Interactive Docs:** http://localhost:8000/docs

---

## 📋 Endpoints Cheat Sheet

### 1️⃣ Health Check
```bash
curl http://localhost:8000/health
```

### 2️⃣ Get Provider Info
```bash
curl http://localhost:8000/provider
```

### 3️⃣ Extract from Single File
```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@path/to/document.docx"
```

### 4️⃣ Batch Extract (Test Set)
```bash
curl -X POST "http://localhost:8000/batch-extract" \
  -H "Content-Type: application/json" \
  -d '{"folder": "test"}'
```

### 5️⃣ Evaluate with Recall
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"folder": "test"}'
```

### 6️⃣ Download Test Predictions CSV
```bash
curl -X POST "http://localhost:8000/predict-test-csv" \
  -o test_predictions.csv
```

---

## 🐍 Python One-Liners

```python
import requests

# Health check
requests.get("http://localhost:8000/health").json()

# Extract from file
requests.post("http://localhost:8000/extract", 
              files={"file": open("document.docx", "rb")}).json()

# Batch extract
requests.post("http://localhost:8000/batch-extract", 
              json={"folder": "test"}).json()

# Evaluate
requests.post("http://localhost:8000/evaluate", 
              json={"folder": "test"}).json()
```

---

## 📊 Response Format

### Extraction Response
```json
{
  "filename": "document.docx",
  "status": "success",
  "metadata": {
    "agreement_value": "12000",
    "agreement_start_date": "01.04.2008",
    "agreement_end_date": "31.03.2009",
    "renewal_notice_days": "60",
    "party_one": "Party Name 1",
    "party_two": "Party Name 2"
  },
  "provider": "OpenAI"
}
```

### Evaluation Response
```json
{
  "overall_recall": 0.875,
  "per_field_recall": [
    {
      "field": "Aggrement Value",
      "recall": 1.0,
      "true_count": 4,
      "total": 4
    }
  ]
}
```

---

## 🔧 Supported File Types
- `.docx` - Microsoft Word documents
- `.png`, `.jpg`, `.jpeg` - Scanned images (OCR)

---

## ⚡ Quick Test

```bash
# 1. Start server
cd backend && python main.py

# 2. Test health (in new terminal)
curl http://localhost:8000/health

# 3. Extract from test file
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx"

# 4. Get all test predictions
curl -X POST "http://localhost:8000/predict-test-csv" \
  -o predictions.csv
```

---

## 📚 Full Documentation
- **Detailed Guide:** `API_USAGE_GUIDE.md`
- **README:** `README.md`
- **Interactive Docs:** http://localhost:8000/docs
