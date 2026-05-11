from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Key
api_key = os.getenv("GROQ_API_KEY")

# Create Groq client
client = Groq(api_key=api_key)

# FastAPI app
app = FastAPI()

# Request model
class ChatRequest(BaseModel):
    message: str

# System Prompt
SYSTEM_PROMPT = """
You are a helpful AI assistant.
Answer clearly and professionally.
"""

# API Endpoint
@app.post("/chat")
def chat(request: ChatRequest):

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]
        )

        answer = response.choices[0].message.content

        return {
            "user_message": request.message,
            "ai_response": answer
        }

    except Exception as e:
        return {
            "error": str(e)
        }