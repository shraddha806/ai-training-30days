# Day15 Mini Project: Document Assistant

## Goal
Build a working Retrieval-Augmented Generation (RAG) prototype over 5+ documents with:
- citation-aware answers
- graceful "I don't know" responses when documents do not support the query
- 10 tested questions with quality scores
- a working prototype, quality report, and demo plan for tomorrow

## Files
- `Doc_assistance.py` — main prototype
- `requirements.txt` — Python dependencies
- `docs/` — 6 source documents for retrieval
- `quality_report.md` — test results, question quality scores, and evaluation notes
- `assignment.md` — task summary and delivery checklist

## Setup
1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file with your Groq key:

```env
GROQ_API_KEY=your_api_key_here
```

## Run the prototype

```bash
python Doc_assistance.py --index
python Doc_assistance.py
```

### Optional commands

```bash
python Doc_assistance.py --test
python Doc_assistance.py --query "How does the product handle data privacy?"
```

## Demo checklist

1. Index documents and verify 6 docs are loaded.
2. Ask 3 sample questions and show citation output.
3. Ask a question outside the document scope and show the graceful "I don't know" response.
4. Review `quality_report.md` with 10 test questions and quality scores.

## Notes
- The prototype uses FAISS for similarity search and `sentence-transformers` for embeddings.
- Citations are returned as document names and chunk positions.
- The LLM answer step uses Groq if `GROQ_API_KEY` is provided.
