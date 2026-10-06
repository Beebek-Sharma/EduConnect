"""
Test script for the Groq client.
Run this script to test the Groq API connection.

IMPORTANT: You need to update the .env file with a valid Groq API key:
1. Go to https://console.groq.com/ to sign up and get your API key
2. Open the .env file in the backend directory
3. Replace 'your_groq_api_key_here' with your actual Groq API key
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def run_test():
    # Try importing the Groq client
    try:
        from groq import Groq
        print("Successfully imported groq package")
    except ImportError as e:
        print(f"Failed to import groq package: {e}")
        print("Please install with: pip install groq")
        sys.exit(1)

    # Get API key and model from environment
    api_key = os.environ.get('GROK_API_KEY')
    model = 'llama-3.1-8b-instant'  # Explicitly use this model

    print(f"Using model: {model}")
    print(f"API key available: {'Yes' if api_key else 'No'}")

    if not api_key:
        print("No GROK_API_KEY set. Skipping live Groq test.")
        return

    # Test the connection
    try:
        # Initialize Groq client with API key
        client = Groq(api_key=api_key)
        
        # Create a simple completion
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, can you give me a brief introduction to your capabilities?"}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        # Print the response
        print("\nGroq API test successful! Response:")
        print("-" * 50)
        print(completion.choices[0].message.content)
        print("-" * 50)
        print(f"Model used: {model}")
        print(f"Total tokens: {completion.usage.total_tokens}")
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError testing Groq API: {str(e)}")
        print("Please check your API key and model name.")
        sys.exit(1)

if __name__ == '__main__':
    run_test()