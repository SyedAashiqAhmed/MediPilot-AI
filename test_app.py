#!/usr/bin/env python3
"""
Simple test script to verify the Flask app works correctly
"""
import os
import sys
import requests
import time

def test_flask_app():
    """Test the Flask application endpoints"""
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Flask App Endpoints...")
    
    # Test routes
    routes_to_test = [
        ("/", "Intro page"),
        ("/patient", "Patient portal"),
        ("/doctor", "Doctor portal"),
        ("/chat", "Chat portal"),
        ("/test_gemini", "Gemini API test"),
        ("/get_all_patients", "Get all patients")
    ]
    
    for route, description in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"{status} - {description}: {route}")
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR - {description}: {route} - {str(e)}")
    
    print("\n📝 Test Summary:")
    print("- If all routes show ✅ PASS, your Flask app is working correctly")
    print("- If /test_gemini shows an error, set your GEMINI_API_KEY environment variable")
    print("- Run the app with: python dpp.py")

if __name__ == "__main__":
    print("Make sure your Flask app is running on http://127.0.0.1:5001")
    print("Start it with: python dpp.py")
    input("Press Enter when the app is running...")
    test_flask_app()
