# Day 11 — AI CLI Project

## Project Overview

This project is a simple AI-powered command-line interface that connects to the Groq API. It lets the user ask questions and receive short, funny responses from an AI assistant.

## Features

- CLI-based chat loop
- Uses `groq` client library for AI completions
- Loads API credentials from a `.env` file
- Includes a fun system prompt to keep replies humorous and concise

## Files

- `app.py` — main application script
- `requirements.txt` — Python dependencies
- `.env` (not tracked) — API key configuration file

## Setup

1. Create a Python virtual environment (recommended):

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `Day11` folder with the following content:

```text
GROQ_API_KEY=your_api_key_here
```

## Usage

Run the application from the `Day11` directory:

```bash
python app.py
```

Then type your prompts and press Enter. Type `exit` to quit.

## Notes

- Ensure your `GROQ_API_KEY` is valid and available in the `.env` file.
- The app uses `llama-3.1-8b-instant` as the model with a temperature of `0.7`.
- If the API key is missing, the program exits with an error message.
