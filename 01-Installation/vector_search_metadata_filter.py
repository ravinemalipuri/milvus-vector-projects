from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer

# Connect to Milvus running in Docker
client = MilvusClient("http://localhost:19530")

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ─────────────────────────────────────────────
# Step 1: Create collection with metadata fields
# ─────────────────────────────────────────────
COLLECTION = "demo_metadata"

if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)

schema = client.create_schema(auto_id=False, enable_dynamic_field=False)
schema.add_field("id",       DataType.INT64,        is_primary=True)
schema.add_field("vector",   DataType.FLOAT_VECTOR, dim=384)
schema.add_field("text",     DataType.VARCHAR,      max_length=512)
schema.add_field("category", DataType.VARCHAR,      max_length=64)
schema.add_field("year",     DataType.INT32)

index_params = client.prepare_index_params()
index_params.add_index("vector", metric_type="COSINE", index_type="FLAT")

client.create_collection(COLLECTION, schema=schema, index_params=index_params)
print("Collection with metadata created.")

# ─────────────────────────────────────────────
# Step 2: Insert documents with metadata
# ─────────────────────────────────────────────
docs = [
    {"id": 1, "text": "Artificial intelligence was founded as an academic discipline in 1956.", "category": "AI History",   "year": 1956},
    {"id": 2, "text": "Alan Turing was the first person to conduct substantial research in AI.", "category": "AI History",   "year": 1950},
    {"id": 3, "text": "Born in Maida Vale, London, Turing was raised in southern England.",     "category": "Biography",    "year": 1912},
    {"id": 4, "text": "Ravi Nemalipuri Born in India, Came to US Sunnyvale in 2007, went back on 2014 and came back to St Louis.", "category": "Biography", "year": 2007},
    {"id": 5, "text": "Milvus is a vector database built for AI applications.",                 "category": "Technology",   "year": 2019},
    {"id": 6, "text": "Vector databases store and search high-dimensional embeddings.",          "category": "Technology",   "year": 2020},
    {"id": 7, "text": "Cosine similarity measures the angle between two vectors.",               "category": "Mathematics",  "year": 2000},
]

texts = [d["text"] for d in docs]
vectors = embedding_model.encode(texts).tolist()

data = [
    {
        "id":       docs[i]["id"],
        "vector":   vectors[i],
        "text":     docs[i]["text"],
        "category": docs[i]["category"],
        "year":     docs[i]["year"],
    }
    for i in range(len(docs))
]

client.insert(collection_name=COLLECTION, data=data)
client.flush(collection_name=COLLECTION)
print(f"Inserted {len(data)} documents with metadata.")

# ─────────────────────────────────────────────
# Insert more docs — new subject: Drug Discovery
# ─────────────────────────────────────────────
more_docs = [
    {"id": 8,  "text": "Machine learning has been used for drug design.",                                      "category": "Drug Discovery", "year": 2021},
    {"id": 9,  "text": "Computational synthesis with AI algorithms predicts molecular properties.",             "category": "Drug Discovery", "year": 2022},
    {"id": 10, "text": "DDR1 is involved in cancers and fibrosis.",                                            "category": "Drug Discovery", "year": 2020},
]

more_texts = [d["text"] for d in more_docs]
more_vectors = embedding_model.encode(more_texts).tolist()

more_data = [
    {
        "id":       more_docs[i]["id"],
        "vector":   more_vectors[i],
        "text":     more_docs[i]["text"],
        "category": more_docs[i]["category"],
        "year":     more_docs[i]["year"],
    }
    for i in range(len(more_docs))
]

client.insert(collection_name=COLLECTION, data=more_data)
client.flush(collection_name=COLLECTION)
print(f"Inserted {len(more_data)} drug discovery documents.")

# ─────────────────────────────────────────────
# Step 3: Insert biology docs (quickstart pattern)
# Subject filter demo — from Milvus quickstart guide
# Note: using embedding_model.encode() instead of embedding_fn (not supported on Windows)
# ─────────────────────────────────────────────
biology_docs = [
    "Machine learning has been used for drug design.",
    "Computational synthesis with AI algorithms predicts molecular properties.",
    "DDR1 is involved in cancers and fibrosis.",
]

biology_vectors = embedding_model.encode(biology_docs).tolist()
biology_data = [
    {"id": 11 + i, "vector": biology_vectors[i], "text": biology_docs[i], "category": "biology", "year": 2021}
    for i in range(len(biology_vectors))
]

client.insert(collection_name=COLLECTION, data=biology_data)
client.flush(collection_name=COLLECTION)
print(f"Inserted {len(biology_data)} biology documents.")

# Search filtered to biology only — excludes AI History docs even if vectors are close
print("\n── Search: 'tell me AI related information' (filter: category == 'biology') ──")
res = client.search(
    collection_name=COLLECTION,
    data=embedding_model.encode(["tell me AI related information"]).tolist(),
    filter='category == "biology"',
    limit=2,
    output_fields=["text", "category"],
)
for hit in res[0]:
    print(f"  [{hit['distance']:.4f}] [{hit['entity']['category']}] {hit['entity']['text']}")

# ─────────────────────────────────────────────
# Step 4: Search WITHOUT filter (baseline)
# ─────────────────────────────────────────────
query = "Tell me about AI research"
query_vector = embedding_model.encode([query]).tolist()

print(f"\n── Search: '{query}' (no filter) ──")
results = client.search(
    collection_name=COLLECTION,
    data=query_vector,
    limit=3,
    output_fields=["text", "category", "year"]
)
for hit in results[0]:
    print(f"  [{hit['distance']:.4f}] [{hit['entity']['category']}] {hit['entity']['text']}")

# ─────────────────────────────────────────────
# Step 4: Search WITH metadata filter
# ─────────────────────────────────────────────
print(f"\n── Search: '{query}' (filter: category == 'AI History') ──")
results = client.search(
    collection_name=COLLECTION,
    data=query_vector,
    limit=3,
    filter='category == "AI History"',
    output_fields=["text", "category", "year"]
)
for hit in results[0]:
    print(f"  [{hit['distance']:.4f}] [{hit['entity']['category']}] {hit['entity']['text']}")

# ─────────────────────────────────────────────
# Step 5: Search with range filter on year
# ─────────────────────────────────────────────
print(f"\n── Search: '{query}' (filter: year >= 2000) ──")
results = client.search(
    collection_name=COLLECTION,
    data=query_vector,
    limit=3,
    filter="year >= 2000",
    output_fields=["text", "category", "year"]
)
for hit in results[0]:
    print(f"  [{hit['distance']:.4f}] [{hit['entity']['year']}] {hit['entity']['text']}")
