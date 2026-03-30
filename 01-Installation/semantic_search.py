from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

# Connect to Milvus running in Docker
client = MilvusClient("http://localhost:19530")

# Load same embedding model used during prepare_data.py (must match!)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Query — what you want to search for
queries = [
    "Who is Alan Turing?",
    "Tell me about Ravi",
    "What is a vector database?",
]

# Encode queries into vectors
query_vectors = embedding_model.encode(queries).tolist()

# Search — find top 2 nearest matches for each query
results = client.search(
    collection_name="demo_collection",
    data=query_vectors,
    limit=2,
    output_fields=["text"]
)

# Print results
for i, query in enumerate(queries):
    print(f"\nQuery: '{query}'")
    print("Top matches:")
    for hit in results[i]:
        print(f"  [{hit['distance']:.4f}] {hit['entity']['text']}")
