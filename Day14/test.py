import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from rag import retrieve, load_index

# Load index and metadata
folder_path = "."
index, metadata = load_index(folder_path)

# Initialize model for consistency
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test questions
questions = [
    "When was the term AI coined?",
    "What defeated world champions in Go?",
    "What layer of the atmosphere is where most weather occurs?",
    "What tools do meteorologists use for wind speed?",
    "What was the name of the early chatbot from the 1960s?",
    "What are key components of chatbots?",
    "How has climate change affected weather patterns?",
    "What are some applications of AI?",
    "What challenges do chatbots face?",
    "What is the future of AI?"
]

# Expected doc indices for each question (manual)
expected_docs = [0, 0, 1, 1, 2, 2, 1, 0, 2, 0]

results = []

for i, q in enumerate(questions):
    retrieved = retrieve(q, index, metadata, top_k=3)
    retrieved_docs = [chunk['doc_idx'] for chunk in retrieved]
    right_chunk = expected_docs[i] in retrieved_docs
    
    # For correct, since no generation, we'll say based on chunks
    # But for now, log
    result = {
        'question': q,
        'retrieved_chunks': [{'doc': chunk['doc_idx'], 'chunk': chunk['chunk_idx'], 'text': chunk['text'][:100]} for chunk in retrieved],
        'right_chunk_retrieved': right_chunk,
        'correct': 'N/A (no generation)',
        'improvements': 'Add LLM generation, improve chunking, use better embeddings'
    }
    results.append(result)

# Write results to file
with open('test_results.md', 'w') as f:
    f.write("# RAG Test Results\n\n")
    for i, res in enumerate(results, 1):
        f.write(f"## Question {i}: {res['question']}\n")
        f.write(f"- **Right chunk retrieved?** {res['right_chunk_retrieved']}\n")
        f.write(f"- **Correct?** {res['correct']}\n")
        f.write(f"- **Improvements:** {res['improvements']}\n")
        f.write("- **Retrieved chunks:**\n")
        for chunk in res['retrieved_chunks']:
            f.write(f"  - Doc {chunk['doc']}, Chunk {chunk['chunk']}: {chunk['text']}...\n")
        f.write("\n")

print("Test results written to test_results.md")






