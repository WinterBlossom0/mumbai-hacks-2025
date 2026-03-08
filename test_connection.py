#!/usr/bin/env python3
"""
Test script to verify backend-frontend connection.
"""

import requests
import sys

def test_backend():
    """Test if backend is running."""
    print("Testing backend connection...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_health():
    """Test health endpoint."""
    print("\nTesting health endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint is working")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Health endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_cors():
    """Test CORS configuration."""
    print("\nTesting CORS configuration...")
    try:
        response = requests.options(
            "http://localhost:8000/api/verify",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        if "access-control-allow-origin" in response.headers:
            print("✓ CORS is configured")
            return True
        else:
            print("⚠ CORS might not be configured properly")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_frontend():
    """Test if frontend is accessible."""
    print("\nTesting frontend connection...")
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"✗ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to frontend. Is it running?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("="*70)
    print("Truth Lens - Connection Test")
    print("="*70)
    print()
    
    results = []
    results.append(test_backend())
    results.append(test_health())
    results.append(test_cors())
    results.append(test_frontend())
    
    print()
    print("="*70)
    if all(results):
        print("✓ All tests passed! System is ready.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nMake sure to run 'python run.py' first!")
    print("="*70)
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
