# MetaExtract API Usage Guide

This document provides comprehensive instructions for consuming the MetaExtract RESTful web service API.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Endpoints](#api-endpoints)
3. [Usage Examples](#usage-examples)
4. [Client Libraries](#client-libraries)
5. [Error Handling](#error-handling)
6. [Rate Limits & Best Practices](#rate-limits--best-practices)

---

## Getting Started

### Prerequisites

- MetaExtract backend server running on `http://localhost:8000`
- LLM provider configured (OpenAI, Azure OpenAI, Groq, or Ollama)

### Starting the API Server

```bash
cd backend
python main.py
```

The API will be available at: **http://localhost:8000**

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all available endpoints
- See request/response schemas
- Test endpoints directly in your browser
- Download OpenAPI specification

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Available Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Health check with provider status | No |
| `GET` | `/provider` | Get active LLM provider info | No |
| `POST` | `/extract` | Extract metadata from a single file | No |
| `POST` | `/batch-extract` | Process all files in train/test folder | No |
| `POST` | `/evaluate` | Evaluate with recall metrics | No |
| `POST` | `/predict-test-csv` | Download test predictions as CSV | No |

---

## Usage Examples

### 1. Health Check

**Purpose:** Verify the API is running and check which LLM provider is active.

**cURL:**
```bash
curl http://localhost:8000/health
```

**Python:**
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

**JavaScript:**
```javascript
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Response:**
```json
{
  "status": "healthy",
  "message": "MetaExtract API is running (LLM: OpenAI)",
  "provider": "OpenAI"
}
```

---

### 2. Get Provider Information

**Purpose:** Get detailed information about the active LLM provider.

**cURL:**
```bash
curl http://localhost:8000/provider
```

**Python:**
```python
import requests

response = requests.get("http://localhost:8000/provider")
provider_info = response.json()
print(f"Provider: {provider_info['provider']}")
print(f"Model: {provider_info['model']}")
```

**Response:**
```json
{
  "provider": "OpenAI",
  "model": "gpt-4o",
  "available": true
}
```

---

### 3. Extract Metadata from Single File

**Purpose:** Upload a document and extract all 6 metadata fields.

**Supported File Types:**
- `.docx` - Microsoft Word documents
- `.png`, `.jpg`, `.jpeg` - Scanned images (OCR)

#### Using cURL

```bash
# Extract from DOCX file
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx"

# Extract from PNG image
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/test/24158401-Rental-Agreement.png"
```

#### Using Python

```python
import requests

# Extract from file
url = "http://localhost:8000/extract"
file_path = "data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

result = response.json()

# Access extracted metadata
metadata = result["metadata"]
print(f"Agreement Value: {metadata['agreement_value']}")
print(f"Start Date: {metadata['agreement_start_date']}")
print(f"End Date: {metadata['agreement_end_date']}")
print(f"Renewal Notice: {metadata['renewal_notice_days']} days")
print(f"Party One: {metadata['party_one']}")
print(f"Party Two: {metadata['party_two']}")
```

#### Using JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx'));

axios.post('http://localhost:8000/extract', form, {
  headers: form.getHeaders()
})
.then(response => {
  const metadata = response.data.metadata;
  console.log(`Agreement Value: ${metadata.agreement_value}`);
  console.log(`Start Date: ${metadata.agreement_start_date}`);
  console.log(`End Date: ${metadata.agreement_end_date}`);
  console.log(`Renewal Notice: ${metadata.renewal_notice_days} days`);
  console.log(`Party One: ${metadata.party_one}`);
  console.log(`Party Two: ${metadata.party_two}`);
})
.catch(error => console.error(error));
```

#### Response Format

```json
{
  "filename": "156155545-Rental-Agreement-Kns-Home.pdf.docx",
  "status": "success",
  "error_message": null,
  "extracted_text_preview": "RENTAL AGREEMENT This agreement made on 15th December 2012...",
  "metadata": {
    "agreement_value": "12000",
    "agreement_start_date": "15.12.2012",
    "agreement_end_date": "15.11.2013",
    "renewal_notice_days": "30",
    "party_one": "V.K.NATARAJ",
    "party_two": "SRI VYSHNAVI DAIRY SPECIALITIES Private Ltd."
  },
  "confidence": "high",
  "provider": "OpenAI"
}
```

---

### 4. Batch Extraction

**Purpose:** Process all files in the train or test folder at once.

**cURL:**
```bash
# Process test folder
curl -X POST "http://localhost:8000/batch-extract" \
  -H "Content-Type: application/json" \
  -d '{"folder": "test"}'

# Process train folder
curl -X POST "http://localhost:8000/batch-extract" \
  -H "Content-Type: application/json" \
  -d '{"folder": "train"}'
```

**Python:**
```python
import requests

url = "http://localhost:8000/batch-extract"
data = {"folder": "test"}

response = requests.post(url, json=data)
result = response.json()

print(f"Processed {result['count']} files from {result['folder']} folder")
print(f"Using provider: {result['provider']}")

# Iterate through predictions
for prediction in result['predictions']:
    print(f"\nFile: {prediction['File Name']}")
    print(f"  Value: {prediction['Aggrement Value']}")
    print(f"  Start: {prediction['Aggrement Start Date']}")
    print(f"  End: {prediction['Aggrement End Date']}")
```

**Response:**
```json
{
  "folder": "test",
  "predictions": [
    {
      "File Name": "24158401-Rental-Agreement",
      "Aggrement Value": "12000",
      "Aggrement Start Date": "01.04.2008",
      "Aggrement End Date": "31.03.2009",
      "Renewal Notice (Days)": "60",
      "Party One": "Sri Hanumaiah",
      "Party Two": "Sri Vishal Bhardwaj"
    },
    {
      "File Name": "95980236-Rental-Agreement",
      "Aggrement Value": "9000",
      "Aggrement Start Date": "01.04.2010",
      "Aggrement End Date": "",
      "Renewal Notice (Days)": "30",
      "Party One": "Mrs. S.Sakunthala",
      "Party Two": "V.V Ravi Kian"
    }
    // ... more predictions
  ],
  "count": 4,
  "provider": "OpenAI"
}
```

---

### 5. Evaluate with Recall Metrics

**Purpose:** Evaluate extraction performance against ground truth with per-field recall.

**cURL:**
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"folder": "test"}'
```

**Python:**
```python
import requests

url = "http://localhost:8000/evaluate"
data = {"folder": "test"}

response = requests.post(url, json=data)
result = response.json()

# Print overall recall
print(f"Overall Recall: {result['overall_recall']:.2%}\n")

# Print per-field recall
print("Per-Field Recall:")
print("-" * 60)
for field in result['per_field_recall']:
    print(f"{field['field']:<30} {field['recall']:.2%} ({field['true_count']}/{field['total']})")

# Print detailed matches for each file
print("\nDetailed Results:")
for detail in result['details']:
    print(f"\n{detail['filename']} ({detail['status']})")
    if 'matches' in detail:
        for field_name, info in detail['matches'].items():
            match_icon = "✓" if info['match'] else "✗"
            print(f"  {match_icon} {field_name}")
            print(f"     GT: {info['ground_truth']}")
            print(f"     Pred: {info['predicted']}")
```

**Response:**
```json
{
  "per_field_recall": [
    {
      "field": "Aggrement Value",
      "true_count": 4,
      "false_count": 0,
      "total": 4,
      "recall": 1.0
    },
    {
      "field": "Aggrement Start Date",
      "true_count": 4,
      "false_count": 0,
      "total": 4,
      "recall": 1.0
    }
    // ... more fields
  ],
  "overall_recall": 0.875,
  "details": [
    {
      "filename": "24158401-Rental-Agreement",
      "status": "processed",
      "matches": {
        "Aggrement Value": {
          "ground_truth": "12000",
          "predicted": "12000",
          "match": true
        }
        // ... more fields
      }
    }
    // ... more files
  ]
}
```

---

### 6. Download Test Predictions as CSV

**Purpose:** Generate predictions for the test set and download as CSV file.

**cURL:**
```bash
curl -X POST "http://localhost:8000/predict-test-csv" -o test_predictions.csv
```

**Python:**
```python
import requests

url = "http://localhost:8000/predict-test-csv"
response = requests.post(url)

# Save to file
with open("test_predictions.csv", "wb") as f:
    f.write(response.content)

print("Predictions saved to test_predictions.csv")
```

**JavaScript:**
```javascript
const axios = require('axios');
const fs = require('fs');

axios.post('http://localhost:8000/predict-test-csv', {}, {
  responseType: 'arraybuffer'
})
.then(response => {
  fs.writeFileSync('test_predictions.csv', response.data);
  console.log('Predictions saved to test_predictions.csv');
})
.catch(error => console.error(error));
```

**CSV Output:**
```csv
File Name,Aggrement Value,Aggrement Start Date,Aggrement End Date,Renewal Notice (Days),Party One,Party Two
24158401-Rental-Agreement,12000,01.04.2008,31.03.2009,60,Sri Hanumaiah,Sri Vishal Bhardwaj
95980236-Rental-Agreement,9000,01.04.2010,,30,Mrs. S.Sakunthala,V.V Ravi Kian
156155545-Rental-Agreement-Kns-Home,12000,15.12.2012,15.11.2013,30,V.K.NATARAJ,SRI VYSHNAVI DAIRY SPECIALITIES Private Ltd.
228094620-Rental-Agreement,15000,07.07.2013,06.06.2014,30,Mr. KAPIL MEHROTRA,Mr.B.Kishore
```

---

## Client Libraries

### Python Client Class

```python
import requests
from typing import Dict, List

class MetaExtractClient:
    """Python client for MetaExtract API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict:
        """Check API health and provider status."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_provider_info(self) -> Dict:
        """Get active LLM provider information."""
        response = requests.get(f"{self.base_url}/provider")
        response.raise_for_status()
        return response.json()
    
    def extract_from_file(self, file_path: str) -> Dict:
        """Extract metadata from a single file."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.base_url}/extract", files=files)
        response.raise_for_status()
        return response.json()
    
    def batch_extract(self, folder: str = "test") -> Dict:
        """Extract from all files in a folder."""
        response = requests.post(
            f"{self.base_url}/batch-extract",
            json={"folder": folder}
        )
        response.raise_for_status()
        return response.json()
    
    def evaluate(self, folder: str = "test") -> Dict:
        """Evaluate extraction performance with recall metrics."""
        response = requests.post(
            f"{self.base_url}/evaluate",
            json={"folder": folder}
        )
        response.raise_for_status()
        return response.json()
    
    def download_test_predictions(self, output_path: str = "test_predictions.csv"):
        """Download test predictions as CSV."""
        response = requests.post(f"{self.base_url}/predict-test-csv")
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path

# Usage example
if __name__ == "__main__":
    client = MetaExtractClient()
    
    # Health check
    health = client.health_check()
    print(f"API Status: {health['status']}")
    print(f"Provider: {health['provider']}")
    
    # Extract from single file
    result = client.extract_from_file("data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx")
    print(f"\nExtracted metadata:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")
    
    # Batch extraction
    batch_results = client.batch_extract("test")
    print(f"\nProcessed {batch_results['count']} files")
    
    # Evaluation
    eval_results = client.evaluate("test")
    print(f"\nOverall Recall: {eval_results['overall_recall']:.2%}")
    
    # Download predictions
    csv_path = client.download_test_predictions()
    print(f"\nPredictions saved to: {csv_path}")
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request (wrong file type, missing parameters) |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Server Error | Server error (LLM failure, processing error) |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Example Error Handling (Python)

```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/extract",
        files={"file": open("document.pdf", "rb")}
    )
    response.raise_for_status()
    result = response.json()
    
    # Check if extraction was successful
    if result['status'] == 'error':
        print(f"Extraction failed: {result['error_message']}")
    else:
        print(f"Success! Extracted metadata: {result['metadata']}")
        
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to API. Is the server running?")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Rate Limits & Best Practices

### Rate Limits

- No rate limits currently enforced
- LLM provider may have their own rate limits (check OpenAI/Groq/Azure docs)

### Best Practices

1. **Batch Processing**: Use `/batch-extract` for multiple files instead of calling `/extract` repeatedly
2. **Error Handling**: Always check the `status` field in responses
3. **File Size**: Keep files under 20MB (configurable in `config.py`)
4. **Timeouts**: Set appropriate timeouts for large files (OCR can take 3-5 seconds per image)
5. **Caching**: Cache results if processing the same file multiple times

### Performance Tips

- **DOCX files**: ~1-2 seconds per file
- **PNG images**: ~3-5 seconds per file (OCR + LLM)
- **Batch processing**: Processes files sequentially (not parallel)

---

## Testing the API

### Using Swagger UI

1. Start the API server
2. Open http://localhost:8000/docs
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
7. View the response

### Using Postman

1. Import the OpenAPI spec from http://localhost:8000/openapi.json
2. Set base URL to `http://localhost:8000`
3. Test endpoints with sample files from `data/test/`

---

## Support

For issues or questions:
- Check the main README.md for setup instructions
- Review the interactive docs at http://localhost:8000/docs
- Ensure LLM provider is configured correctly in `.env`

---

## Summary

The MetaExtract API provides a simple, RESTful interface for document metadata extraction:

✅ **6 endpoints** covering health checks, single/batch extraction, evaluation, and CSV export
✅ **Multiple file formats** supported (DOCX, PNG, JPG)
✅ **LLM-based extraction** (non-rule-based approach)
✅ **Interactive documentation** with Swagger UI
✅ **Easy integration** with Python, JavaScript, cURL, and more

Start the server with `python backend/main.py` and begin extracting metadata from your documents!
