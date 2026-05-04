import os

# Read the document
with open(r"c:\Users\shrad\OneDrive - bsc-us co in\Desktop\Training\Day12\README.md", 'r', encoding='utf-8') as f:
    text = f.read()

print(f"Total characters: {len(text)}")

# Chunk sizes
sizes = [200, 500, 1000]

for size in sizes:
    chunks = []
    for i in range(0, len(text), size):
        chunk = text[i:i+size]
        chunks.append(chunk)
    print(f"\nChunk size {size}: {len(chunks)} chunks")
    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx+1}: {chunk[:50]}...")  # First 50 chars