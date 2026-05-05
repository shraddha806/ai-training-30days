import argparse
import json
import os
from pathlib import Path

import faiss
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# Configuration
DOCS_DIR = Path("docs")
INDEX_FILE = Path("index.faiss")
METADATA_FILE = Path("metadata.json")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 450
TOP_K = 4
UNKNOWN_DISTANCE_THRESHOLD = 2.5

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def load_documents(folder_path):
    documents = []
    for file_path in sorted(folder_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()
        if text:
            documents.append({
                "name": file_path.name,
                "text": text,
            })
    return documents


def chunk_text(text, chunk_size):
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size
    return chunks


def build_index(documents):
    encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    all_chunks = []
    metadata = []

    for document in documents:
        chunks = chunk_text(document["text"], CHUNK_SIZE)
        for chunk_id, chunk_text_content in enumerate(chunks):
            all_chunks.append(chunk_text_content)
            metadata.append(
                {
                    "doc_name": document["name"],
                    "chunk_id": chunk_id,
                    "text": chunk_text_content,
                }
            )

    embeddings = encoder.encode(all_chunks, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype("float32"))

    return index, metadata


def save_index(index, metadata):
    faiss.write_index(index, str(INDEX_FILE))
    with METADATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def load_index():
    index = faiss.read_index(str(INDEX_FILE))
    metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    return index, metadata


def retrieve(query, index, metadata, top_k=TOP_K):
    encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = encoder.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    retrieved = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0:
            continue
        item = metadata[idx].copy()
        item["distance"] = float(dist)
        retrieved.append(item)
    return retrieved


def format_citations(retrieved_chunks):
    citations = []
    for chunk in retrieved_chunks:
        citations.append(f"{chunk['doc_name']} (chunk {chunk['chunk_id']})")
    return citations


def build_fallback_answer(retrieved_chunks):
    if not retrieved_chunks:
        return "I don't know based on the provided documents."

    top_chunks = retrieved_chunks[:2]
    answer_text = "\n\n".join(chunk["text"] for chunk in top_chunks)
    return (
        "Based on the most relevant document content, here is the answer:\n\n"
        f"{answer_text}\n\n"
        "[Note: Set GROQ_API_KEY in .env to enable AI-generated summarization.]"
    )


def should_use_unknown(retrieved_chunks):
    if not retrieved_chunks:
        return True
    average_distance = sum(chunk["distance"] for chunk in retrieved_chunks) / len(retrieved_chunks)
    return average_distance > UNKNOWN_DISTANCE_THRESHOLD


def generate_answer(query, retrieved_chunks):
    citations = format_citations(retrieved_chunks)
    context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    system_message = (
        "You are a document assistant. Answer only from the provided context. "
        "If the question cannot be answered from the context, reply: 'I don't know based on the provided documents.'"
    )
    user_message = (
        f"Context:\n{context}\n\nQuestion: {query}\n\n"
        "Provide a concise answer and include a 'Sources:' section with citations."
    )

    if client:
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )
            answer = response.choices[0].message.content.strip()
        except (AttributeError, TypeError) as e:
            answer = f"Error generating answer (Groq API issue): {e}"
        except Exception as e:
            answer = f"Error generating answer: {e}"
    else:
        answer = build_fallback_answer(retrieved_chunks)

    if "Sources:" not in answer:
        answer += "\n\nSources: " + ", ".join(citations)
    return answer


def answer_query(query, index, metadata):
    retrieved = retrieve(query, index, metadata)
    if should_use_unknown(retrieved):
        return "I don't know based on the provided documents."

    answer = generate_answer(query, retrieved)
    return answer


TEST_QUESTIONS = [
    "What are the steps to install the product?",
    "How does the product handle data privacy?",
    "What is the refund policy?",
    "What should I do if the app crashes on startup?",
    "Which features are new in version 2.0?",
    "Can I use the product offline?",
    "How do I reset my password?",
    "What are the security requirements for users?",
    "Does the product support team collaboration?",
    "What is the warranty period for hardware?",
]


def run_tests(index, metadata):
    results = []
    for question in TEST_QUESTIONS:
        retrieved = retrieve(question, index, metadata)
        answer = answer_query(question, index, metadata)
        citations = format_citations(retrieved)
        results.append(
            {
                "question": question,
                "answer": answer,
                "sources": citations,
                "top_distances": [chunk["distance"] for chunk in retrieved],
            }
        )

    output_path = Path("test_results.json")
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved test results to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Day15 Document Assistant")
    parser.add_argument("--index", action="store_true", help="Build or rebuild the document index")
    parser.add_argument("--test", action="store_true", help="Run sample test questions")
    parser.add_argument("--query", type=str, help="Ask a single question")
    args = parser.parse_args()

    if args.index or not INDEX_FILE.exists() or not METADATA_FILE.exists():
        print("Building document index...")
        docs = load_documents(DOCS_DIR)
        if not docs:
            raise FileNotFoundError(f"No .txt documents found in {DOCS_DIR}")
        index, metadata = build_index(docs)
        save_index(index, metadata)
        print(f"Indexed {len(metadata)} chunks from {len(docs)} documents.")
    else:
        print("Loading existing index...")
        index, metadata = load_index()

    if args.test:
        run_tests(index, metadata)
    elif args.query:
        print(answer_query(args.query, index, metadata))
    else:
        print("Enter a question, or type 'quit' to exit.")
        while True:
            query = input("Question: ").strip()
            if query.lower() in {"quit", "exit"}:
                break
            if not query:
                continue
            print(answer_query(query, index, metadata))
            print()
