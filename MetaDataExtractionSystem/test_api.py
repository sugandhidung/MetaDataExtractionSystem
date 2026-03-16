#!/usr/bin/env python3
"""
Simple script to test the MetaExtract RESTful API.
Run this after starting the backend server with: python backend/main.py
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    """Test 1: Health check endpoint."""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_provider():
    """Test 2: Get provider information."""
    print_section("TEST 2: Provider Information")
    
    try:
        response = requests.get(f"{BASE_URL}/provider")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('available'):
            print(f"✅ Provider active: {data.get('provider')} ({data.get('model')})")
        else:
            print(f"⚠️  No provider available")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_extract_single_file():
    """Test 3: Extract metadata from a single file."""
    print_section("TEST 3: Single File Extraction")
    
    # Try to find a test file
    test_files = [
        "data/test/156155545-Rental-Agreement-Kns-Home.pdf.docx",
        "data/test/228094620-Rental-Agreement.pdf.docx",
        "data/test/24158401-Rental-Agreement.png",
    ]
    
    test_file = None
    for file_path in test_files:
        if Path(file_path).exists():
            test_file = file_path
            break
    
    if not test_file:
        print("⚠️  No test files found in data/test/")
        return False
    
    print(f"Testing with file: {test_file}")
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/extract", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📄 Filename: {data['filename']}")
            print(f"📊 Status: {data['status']}")
            print(f"🤖 Provider: {data.get('provider', 'N/A')}")
            
            if data['status'] == 'success':
                print("\n📋 Extracted Metadata:")
                metadata = data['metadata']
                print(f"  Agreement Value: {metadata.get('agreement_value', 'N/A')}")
                print(f"  Start Date: {metadata.get('agreement_start_date', 'N/A')}")
                print(f"  End Date: {metadata.get('agreement_end_date', 'N/A')}")
                print(f"  Renewal Notice: {metadata.get('renewal_notice_days', 'N/A')} days")
                print(f"  Party One: {metadata.get('party_one', 'N/A')}")
                print(f"  Party Two: {metadata.get('party_two', 'N/A')}")
                print("\n✅ Extraction successful!")
            else:
                print(f"❌ Extraction failed: {data.get('error_message')}")
        else:
            print(f"❌ Request failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_batch_extract():
    """Test 4: Batch extraction on test folder."""
    print_section("TEST 4: Batch Extraction")
    
    try:
        response = requests.post(
            f"{BASE_URL}/batch-extract",
            json={"folder": "test"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📁 Folder: {data['folder']}")
            print(f"📊 Files processed: {data['count']}")
            print(f"🤖 Provider: {data.get('provider', 'N/A')}")
            
            print("\n📋 Predictions:")
            for pred in data['predictions'][:3]:  # Show first 3
                print(f"\n  File: {pred['File Name']}")
                print(f"    Value: {pred.get('Aggrement Value', 'N/A')}")
                print(f"    Start: {pred.get('Aggrement Start Date', 'N/A')}")
                print(f"    End: {pred.get('Aggrement End Date', 'N/A')}")
            
            if data['count'] > 3:
                print(f"\n  ... and {data['count'] - 3} more files")
            
            print("\n✅ Batch extraction successful!")
        else:
            print(f"❌ Request failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_evaluate():
    """Test 5: Evaluate with recall metrics."""
    print_section("TEST 5: Evaluation with Recall Metrics")
    
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate",
            json={"folder": "test"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Overall Recall: {data['overall_recall']:.2%}")
            
            print("\n📋 Per-Field Recall:")
            for field in data['per_field_recall']:
                bar_length = int(field['recall'] * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"  {field['field']:<30} {bar} {field['recall']:.1%} ({field['true_count']}/{field['total']})")
            
            print("\n✅ Evaluation successful!")
        else:
            print(f"❌ Request failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download_csv():
    """Test 6: Download test predictions as CSV."""
    print_section("TEST 6: Download Test Predictions CSV")
    
    try:
        response = requests.post(f"{BASE_URL}/predict-test-csv")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            output_file = "test_predictions_downloaded.csv"
            with open(output_file, "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"\n✅ CSV downloaded successfully!")
            print(f"📄 Saved to: {output_file}")
            print(f"📊 File size: {file_size} bytes")
            
            # Show first few lines
            print("\n📋 Preview:")
            lines = response.content.decode('utf-8').split('\n')[:4]
            for line in lines:
                print(f"  {line}")
        else:
            print(f"❌ Request failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all API tests."""
    print("\n" + "🚀" * 30)
    print("  MetaExtract API Test Suite")
    print("🚀" * 30)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print("Please start the server first:")
        print("  cd backend && python main.py")
        return
    
    # Run all tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Provider Info", test_provider()))
    results.append(("Single File Extraction", test_extract_single_file()))
    results.append(("Batch Extraction", test_batch_extract()))
    results.append(("Evaluation", test_evaluate()))
    results.append(("Download CSV", test_download_csv()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")

if __name__ == "__main__":
    main()
