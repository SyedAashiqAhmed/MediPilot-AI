import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:20]}..." if api_key else "No API key found!")

if api_key:
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        
        # Create model with correct name
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        print("✅ Model created successfully (models/gemini-2.0-flash)")
        
        # Test message
        test_message = "Tell me a short joke"
        print(f"\n📤 Sending: {test_message}")
        
        # Generate response
        response = model.generate_content(test_message)
        print(f"\n✅ Response received!")
        print(f"\n📥 Response text:\n{response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"❌ Message: {str(e)}")
        import traceback
        print(f"\n❌ Full traceback:")
        traceback.print_exc()
else:
    print("❌ No GEMINI_API_KEY found in .env file")
