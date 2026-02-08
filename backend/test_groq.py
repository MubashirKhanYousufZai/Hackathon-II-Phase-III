import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get the API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in .env file")
else:
    print("SUCCESS: GROQ_API_KEY found in environment")
    
    # Initialize Groq client
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    
    try:
        # Test the API key by making a simple request
        print("Testing API key...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello, just testing if the API key works.",
                }
            ],
            model="llama3-8b-8192",
        )
        print("SUCCESS: API key is valid and working!")
        print("Response:", chat_completion.choices[0].message.content[:100] + "..." if len(chat_completion.choices[0].message.content) > 100 else chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"ERROR: Issue with API key: {str(e)}")