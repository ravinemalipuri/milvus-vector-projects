from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

# Connect to Milvus running in Docker
client = MilvusClient("http://localhost:19530")

# Use sentence-transformers model (384 dims) - works on Windows
# Replaces DefaultEmbeddingFunction which has ONNX tokenizer bug on Windows
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample documents to embed and store
docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",
    "Alan Turing was the first person to conduct substantial research in AI.",
    "Born in Maida Vale, London, Turing was raised in southern England.",
    "Ravi Nemalipuri Born in India, Came to US Sunnyvale in 2007, Wroked with Cognizant , Meta, Netall, Autodesk, Pepsi, Bayer, Hyster-Yale etc",
    "Milvus is a vector database built for AI applications.",
    "Vector databases store and search high-dimensional embeddings.",
    "Cosine similarity measures the angle between two vectors.",
]

# Generate embeddings (384-dim float vectors)
vectors = embedding_model.encode(docs).tolist()
print(f"Embedding dim: {len(vectors[0])}, Total vectors: {len(vectors)}")

# Recreate collection with correct dimension (384)
if client.has_collection(collection_name="demo_collection"):
    client.drop_collection(collection_name="demo_collection")
client.create_collection(collection_name="demo_collection", dimension=384)
print("Collection ready.")

# Prepare data for insertion
data = [
    {"id": i, "vector": vectors[i], "text": docs[i]}
    for i in range(len(docs))
]

# Insert into collection
res = client.insert(collection_name="demo_collection", data=data)
print(f"Inserted: {res}")
