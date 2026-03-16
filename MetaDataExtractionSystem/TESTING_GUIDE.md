# MetaExtract API Testing Guide

This guide shows you how to test the RESTful API using different methods.

---

## Method 1: Automated Test Script (Easiest) ⭐

### Step 1: Start the API Server

Open a terminal and run:

```bash
cd backend
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal open!**

### Step 2: Run the Test Script

Open a **new terminal** and run:

```bash
python3 test_api.py
```

This will automatically test all 6 API endpoints and show you the results.

**Expected Output:**
```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
  MetaExtract API Test Suite
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
  TEST 1: Health Check
============================================================
Status Code: 200
Response: {
  "status": "healthy",
  "message": "MetaExtract API is running (LLM: OpenAI)",
  "provider": "OpenAI"
}

... (more tests)

============================================================
  TEST SUMMARY
============================================================
✅ PASS  Health Check
✅ PASS  Provider Info
✅ PASS  Single File Extraction
✅ PASS  Batch Extraction
✅ PASS  Evaluation
✅ PASS  Download CSV

📊 Results: 6/6 tests passed

🎉 All tests passed! API is working correctly.
```

---

## Method 2: Interactive Swagger UI (Visual) 🎨

### Step 1: Start the API Server

```bash
cd backend
python3 main.py
```

### Step 2: Open Swagger UI

Open your browser and go to:
```
http://localhost:8000/docs
```

### Step 3: Test Each Endpoint

1. **Click on any endpoint** (e.g., `GET /health`)
2. **Click "Try it out"**
3. **Fill in parameters** (if needed)
4. **Click "Execute"**
5. **View the response** below

**Example: Testing `/extract` endpoint**

1. Click on `POST /extract`
2. Click "Try it out"
3. Click "Choose File" and select a file from `data/test/`
4. Click "Execute"
5. See the extracted metadata in the response

**Screenshot of what you'll see:**
```
POST /extract
▼ Try it out

file* [Choose File] 156155545-Rental-Agreement-Kns-Home.pdf.docx

[Execute]

Response:
{
  "filename": "156155545-Rental-Agreement-Kns-Home.pdf.docx",
  "status": "success",
  "metadata": {
    "agreement_value": "12000",
    "agreement_start_date": "15.12.2012",
    ...
  }
}
```

---

## Method 3: Using cURL (Command Line) 💻

### Prerequisites
Make sure the API server is running!

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "message": "MetaExtract API is running (LLM: OpenAI)",
  "provider": "OpenAI"
}
```

### Test 2: Get Provider Info
```bash
curl http://localhost:8000/provider
```

### Test 3: Extract from Single File
```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx"
```

**Expected Output:**
```json
{
  "filename": "156155545-Rental-Agreement-Kns-Home.pdf.docx",
  "status": "success",
  "metadata": {
    "agreement_value": "12000",
    "agreement_start_date": "15.12.2012",
    "agreement_end_date": "15.11.2013",
    "renewal_notice_days": "30",
    "party_one": "V.K.NATARAJ",
    "party_two": "SRI VYSHNAVI DAIRY SPECIALITIES Private Ltd."
  },
  "provider": "OpenAI"
}
```

### Test 4: Batch Extract
```bash
curl -X POST "http://localhost:8000/batch-extract" \
  -H "Content-Type: application/json" \
  -d '{"folder": "test"}'
```

### Test 5: Evaluate
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"folder": "test"}'
```

### Test 6: Download CSV
```bash
curl -X POST "http://localhost:8000/predict-test-csv" \
  -o test_predictions.csv
```

---

## Method 4: Using Python Requests 🐍

### Create a test file: `my_api_test.py`

```python
import requests

# Test health check
response = requests.get("http://localhost:8000/health")
print("Health:", response.json())

# Test extraction
with open("data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/extract", files=files)
    result = response.json()
    print("\nExtracted Metadata:")
    print(f"  Agreement Value: {result['metadata']['agreement_value']}")
    print(f"  Start Date: {result['metadata']['agreement_start_date']}")
    print(f"  Party One: {result['metadata']['party_one']}")
```

### Run it:
```bash
python3 my_api_test.py
```

---

## Method 5: Using Postman 📮

### Step 1: Import API

1. Open Postman
2. Click "Import"
3. Enter URL: `http://localhost:8000/openapi.json`
4. Click "Import"

### Step 2: Test Endpoints

1. Select an endpoint from the collection
2. Click "Send"
3. View the response

---

## Troubleshooting 🔧

### Error: "Connection refused"

**Problem:** API server is not running

**Solution:**
```bash
cd backend
python3 main.py
```

### Error: "No LLM provider available"

**Problem:** OpenAI API key not configured

**Solution:**
Check your `.env` file has:
```
OPENAI_API_KEY=sk-proj-...
```

### Error: "File not found"

**Problem:** Test file path is incorrect

**Solution:**
Make sure you're running commands from the project root directory where `data/` folder exists.

### Error: "Module not found"

**Problem:** Python dependencies not installed

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

---

## Quick Verification Checklist ✅

Run these commands to verify everything works:

```bash
# 1. Check server is running
curl http://localhost:8000/health

# 2. Check provider is configured
curl http://localhost:8000/provider

# 3. Test extraction (replace with actual file path)
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx"

# 4. Run automated tests
python3 test_api.py
```

If all commands work, your API is ready! ✅

---

## What to Expect

### Successful Response
```json
{
  "status": "success",
  "metadata": {
    "agreement_value": "12000",
    ...
  }
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

---

## Next Steps

- ✅ Test all endpoints using the automated script
- ✅ Try the interactive Swagger UI
- ✅ Test with your own documents
- ✅ Check the evaluation metrics
- ✅ Download the CSV predictions

**Happy Testing!** 🎉
