from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = "You are a helpful AI assistant. Give clear, short answers."

def ask_llm(user_input):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

print("🤖 Chatbot Started (type 'exit' to quit)")

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    try:
        answer = ask_llm(user_input)
        print("\nAI:", answer)
    except Exception as e:
        print("Error:", e)







        