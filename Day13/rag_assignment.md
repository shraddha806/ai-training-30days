# RAG Assignment

## RAG Stages Explanation

### 1. Indexing Stage
The indexing stage is the foundational step in Retrieval-Augmented Generation where the system prepares the knowledge base for efficient querying. It involves collecting relevant documents from various sources, breaking them down into manageable chunks of text to fit within the model's context window, and converting each chunk into vector embeddings using an embedding model like those from OpenAI or Sentence Transformers. These embeddings capture the semantic meaning of the text and are stored in a vector database such as Pinecone or FAISS, along with metadata for quick retrieval. This process ensures that the knowledge base is searchable and scalable, allowing the system to handle large volumes of information without loading everything into memory at once.

### 2. Retrieval Stage
In the retrieval stage, when a user submits a query, the system transforms the query into a vector embedding using the same embedding model used during indexing. It then performs a similarity search in the vector database to find the most relevant chunks based on cosine similarity or other distance metrics. The top-k most similar chunks are retrieved and ranked by relevance. This stage acts as a filter to pull only the pertinent information from the vast knowledge base, ensuring that the subsequent generation is grounded in accurate and contextually appropriate data, rather than relying solely on the model's pre-trained knowledge which might be outdated or incomplete.

### 3. Generation Stage
The generation stage combines the retrieved chunks with the original user query to produce a coherent and informed response. The retrieved context is fed into a large language model, such as GPT-4 or Llama, along with a prompt that instructs the model to use the provided information to answer the query. The model generates text that synthesizes the retrieved facts, maintaining factual accuracy and relevance while avoiding hallucinations. This stage leverages the strengths of both retrieval for up-to-date knowledge and generation for natural language production, resulting in responses that are more reliable, customizable, and capable of handling domain-specific or current events that weren't in the model's training data.

## Chunking Experiment

### Document Used
The document used for chunking is the README.md file from Day12, which describes a mini project on building an AI chatbot. It has 2981 characters.

### Chunk Sizes
- 200 characters: 15 chunks
- 500 characters: 6 chunks
- 1000 characters: 3 chunks

### Test Questions
1. What is the objective of the Day 12 mini project?
2. How do you configure the API key for the chatbot?
3. What are the 5 tested prompts in the project?

### Results
For all three test questions, the chunk size of 200 characters works best. This is because smaller chunks provide more precise and relevant information without including extraneous details that could dilute the context or introduce noise. For question 1, the objective is contained in the first chunk across all sizes, but smaller chunks ensure minimal irrelevant content. For questions 2 and 3, the relevant information is isolated in specific chunks (chunk 8 for API key, chunk 10 for prompts), allowing for exact retrieval without pulling in surrounding sections that might not be directly related. Larger chunks, while covering more ground, risk including too much context that could confuse the generation process or make the response less focused.