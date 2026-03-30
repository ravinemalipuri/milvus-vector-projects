from pymilvus import MilvusClient

# Connect to a local Milvus Lite file-based database
client = MilvusClient("http://localhost:19530")

# 1. Create a collection (like a table) for 768-dimensional vectors
if client.has_collection(collection_name="demo_collection"):
    client.drop_collection(collection_name="demo_collection")
client.create_collection(
    collection_name="demo_collection",
    dimension=768,  # The vectors we will use in this demo has 768 dimensions
)
print("Collection created.")

# 2. Insert some vectors with labels
data = [
    {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4], "label": "cat"},
    {"id": 2, "vector": [0.9, 0.8, 0.7, 0.6], "label": "dog"},
    {"id": 3, "vector": [0.1, 0.3, 0.2, 0.5], "label": "kitten"},
    {"id": 4, "vector": [0.8, 0.9, 0.6, 0.7], "label": "puppy"},
]
client.insert(collection_name="demo_collection", data=data)
print(f"Inserted {len(data)} vectors.")

# 3. Search — find the 2 most similar vectors to a query
query_vector = [0.1, 0.25, 0.25, 0.45]
results = client.search(
    collection_name="demo_collection",
    data=[query_vector],
    limit=2,
    output_fields=["label"]
)

print("\nSearch results (nearest matches):")
for hit in results[0]:
    print(f"  id={hit['id']}  label={hit['entity']['label']}  distance={hit['distance']:.4f}")
