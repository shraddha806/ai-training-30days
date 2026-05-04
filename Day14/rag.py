import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import pickle

# Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize embedding model
#this is the pretrained model from the huggingface sentence-transformers library, which provides a good balance of performance and speed for RAG tasks. You can experiment with other models as needed.
model = SentenceTransformer('all-MiniLM-L6-v2')

# Chunk size
CHUNK_SIZE = 500

def load_documents(folder_path):
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                documents.append(f.read())
    return documents

def chunk_text(text, chunk_size):
    chunks = []   
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

def index_documents(documents):
    all_chunks = []
    chunk_metadata = []
    for doc_idx, doc in enumerate(documents):
        chunks = chunk_text(doc, CHUNK_SIZE)
        all_chunks.extend(chunks)
        for chunk_idx, chunk in enumerate(chunks):
            chunk_metadata.append({'doc_idx': doc_idx, 'chunk_idx': chunk_idx, 'text': chunk})
    
    # Embed chunks
    embeddings = model.encode(all_chunks)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    return index, chunk_metadata

def retrieve(query, index, chunk_metadata, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding.astype('float32'), top_k)
    retrieved_chunks = [chunk_metadata[i] for i in indices[0]]
    return retrieved_chunks

def generate_answer(query, retrieved_chunks):
    context = "\n".join([chunk['text'] for chunk in retrieved_chunks])
    prompt = f"Based on the following context, answer the question: {query}\n\nContext:\n{context}\n\nAnswer:"
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def save_index(index, metadata, folder_path):
    faiss.write_index(index, os.path.join(folder_path, 'index.faiss'))
    with open(os.path.join(folder_path, 'metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)

def load_index(folder_path):
    index = faiss.read_index(os.path.join(folder_path, 'index.faiss'))
    with open(os.path.join(folder_path, 'metadata.pkl'), 'rb') as f:
        metadata = pickle.load(f)
    return index, metadata

if __name__ == "__main__":
    folder_path = "."
    
    # Check if index exists
    if not os.path.exists('index.faiss'):
        print("Indexing documents...")
        documents = load_documents(folder_path)
        index, metadata = index_documents(documents)
        save_index(index, metadata, folder_path)
        print("Indexing complete.")
    else:
        print("Loading existing index...")
        index, metadata = load_index(folder_path)
    
    # Interactive query
    while True:
        query = input("Enter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        retrieved = retrieve(query, index, metadata)
        answer = generate_answer(query, retrieved)
        print(f"Answer: {answer}")
        print("Retrieved chunks:")
        for chunk in retrieved:
            print(f"Doc {chunk['doc_idx']}, Chunk {chunk['chunk_idx']}: {chunk['text'][:100]}...")

