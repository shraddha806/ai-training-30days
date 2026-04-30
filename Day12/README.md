# Day 12 — Mini Project: AI Chatbot with Prompt Toolkit

## Project Overview

This is Day 12 of the training journey, focusing on building a complete AI chatbot that leverages a prompt toolkit for various natural language processing tasks. The project demonstrates practical AI integration using the Groq API, with a focus on prompt engineering and conversational AI.

## Assignment Details

**MINI PROJECT: Build a complete chatbot OR prompt toolkit**

**Deliverables:**
- Python code for the working chatbot
- 5 tested prompts with examples
- 2-minute verbal demo to partner

## Features

- Interactive CLI chatbot powered by Groq's Llama model
- Modular prompt system for different AI tasks
- Environment-based configuration for API keys
- Error handling for robust operation
- Support for multiple prompt types: summarization, sentiment analysis, entity extraction, Q&A, and rewriting

## Files

- `chatbot.py` — Main chatbot application script
- `prompts.md` — Documentation of 5 tested prompts with examples
- `requirements.txt` — Python dependencies
- `.env` — API key configuration (not tracked in git)
- `README.md` — This documentation file

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key:**
   Create a `.env` file in the `Day12` folder:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

## Usage

1. **Run the chatbot:**
   ```bash
   python chatbot.py
   ```

2. **Interact with the AI:**
   - Type your questions or prompts
   - The AI will respond based on the system prompt
   - Type 'exit' to quit

## Prompt Toolkit

The project includes 5 tested prompts for different AI tasks:

1. **Summarization** — Condenses text into 5 bullet points
2. **Sentiment Classification** — Analyzes text sentiment (Positive/Neutral/Negative)
3. **Entity Extraction** — Extracts names, companies, dates in JSON format
4. **Q&A** — Provides beginner-friendly explanations
5. **Rewriting** — Converts text to professional tone

See `prompts.md` for detailed prompt templates and examples.

## Demo Preparation

For the 2-minute verbal demo:
- Show the chatbot running
- Demonstrate each of the 5 prompt types
- Explain the code structure briefly
- Highlight prompt engineering techniques used

## Technical Details

- **Model:** llama-3.1-8b-instant
- **Temperature:** 0.7 (balanced creativity and coherence)
- **API:** Groq for fast inference
- **Language:** Python 3.x
- **Dependencies:** groq, python-dotenv

## Learning Outcomes

- Prompt engineering for specific tasks
- API integration with AI services
- CLI application development
- Error handling in AI applications
- Documentation of AI prompts

## Next Steps

- Consider adding more prompt types
- Implement conversation memory
- Add web interface (Flask/Streamlit)
- Explore other AI models for comparison