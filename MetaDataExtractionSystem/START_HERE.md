# 🚀 Quick Start - Testing the RESTful API


Follow these simple steps to test your MetaExtract API:

---

## Step 1: Start the API Server

Open a terminal and run:

```bash
cd backend
python3 main.py
```

**You should see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Keep this terminal window open!** The server needs to stay running.

---

## Step 2: Test the API (Choose ONE method)

### Option A: Automated Test Script (Recommended) ⭐

Open a **NEW terminal** (keep the server running in the first one) and run:

```bash
python3 test_api.py
```

This will test all 6 endpoints automatically and show you the results!

---

### Option B: Interactive Browser Testing 🌐

1. Make sure the server is running (Step 1)
2. Open your browser
3. Go to: **http://localhost:8000/docs**
4. Click on any endpoint (e.g., `GET /health`)
5. Click "Try it out"
6. Click "Execute"
7. See the response!

---

### Option C: Quick Command Line Test 💻

Open a **NEW terminal** and run:

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Test 2: Provider info
curl http://localhost:8000/provider

# Test 3: Extract from a file
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx"
```

---

## What You'll See

### ✅ Successful Health Check:
```json
{
  "status": "healthy",
  "message": "MetaExtract API is running (LLM: OpenAI)",
  "provider": "OpenAI"
}
```

### ✅ Successful Extraction:
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

---

## Troubleshooting

### ❌ "Connection refused"
**Problem:** Server not running  
**Solution:** Go back to Step 1 and start the server

### ❌ "No LLM provider available"
**Problem:** OpenAI key not configured  
**Solution:** Check your `.env` file has `OPENAI_API_KEY=sk-proj-...`

### ❌ "Module not found"
**Problem:** Dependencies not installed  
**Solution:** Run `cd backend && pip install -r requirements.txt`

---

## All Available Endpoints

Once the server is running, you can test:

1. **GET** `/health` - Check if API is running
2. **GET** `/provider` - Get LLM provider info
3. **POST** `/extract` - Extract from single file
4. **POST** `/batch-extract` - Process all test files
5. **POST** `/evaluate` - Get recall metrics
6. **POST** `/predict-test-csv` - Download predictions CSV

---

## Full Documentation

- **Testing Guide:** `TESTING_GUIDE.md`
- **API Reference:** `API_USAGE_GUIDE.md`
- **Quick Reference:** `API_QUICK_REFERENCE.md`
- **Interactive Docs:** http://localhost:8000/docs (when server is running)

---

## Ready to Test?

1. ✅ Start server: `cd backend && python3 main.py`
2. ✅ Run tests: `python3 test_api.py` (in new terminal)
3. ✅ Or visit: http://localhost:8000/docs

**That's it!** 🎉
