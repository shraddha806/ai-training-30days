from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read API key
api_key = os.getenv("GROQ_API_KEY")

# Check if key exists
if not api_key:
    print("Error: API key not found. Add it in .env file")
    exit()

# Create client
client = Groq(api_key=api_key)

# System Prompt
SYSTEM_PROMPT = """
You are a helpful and a very funny AI assistant.
Give clear, short,funny, answers and always add a funny jokes in your answers.
"""

print("=" * 50)
print("🤖 AI CLI Tool Started (Groq)")
print("Type 'exit' to quit")
print("=" * 50)

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    if not user_input.strip():
        print("Please enter a valid message.")
        continue

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()

        print("\nAI:", answer)

    except Exception as e:
        print("\nError:", str(e))



