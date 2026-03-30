# Concepts to Learn Before Implementing

---

## 1. What is a Vector?

A vector is a list of numbers (floats) that represents the meaning or features of something.

Example — a 4-dim vector for the word "cat":
```
[0.1, 0.2, 0.3, 0.4]
```

In real use cases (e.g. sentence embeddings), vectors are 768 or 1536 dimensions.

---

## 2. What is an Embedding?

The process of converting data (text, images, audio) into a vector using a model.

```
"I love cats"  →  embedding model  →  [0.12, 0.87, 0.34, ...]  (768 floats)
```

Common embedding models:
- `sentence-transformers/all-MiniLM-L6-v2` → 384 dims
- `text-embedding-3-small` (OpenAI) → 1536 dims
- `nomic-embed-text` → 768 dims

---

## 3. What is Similarity Search?

Instead of exact lookup (like SQL WHERE), vector search finds the **nearest neighbours** — items whose vectors are closest to the query vector.

```
Query: "fluffy animals"  →  nearest matches: "cat", "kitten", "rabbit"
```

---

## 4. Distance / Similarity Metrics

How Milvus measures "closeness" between vectors.

| Metric | Description | Best for |
|---|---|---|
| **L2** (Euclidean) | Straight-line distance. Lower = more similar. | General use |
| **IP** (Inner Product) | Dot product. Higher = more similar. | Normalised vectors |
| **COSINE** | Angle between vectors. 1 = identical, 0 = unrelated. | Text embeddings |

**Cosine Similarity** is the most common for text/NLP use cases.

Reference: [Milvus Metric Types — Cosine Similarity](https://milvus.io/docs/metric.md#Cosine-Similarity)

---

## 5. Collection

Equivalent to a table in a relational database, but stores vectors.

Key parameters:
- `dimension` — must match the output size of your embedding model
- `metric_type` — how similarity is measured (L2, IP, COSINE)

---

## 6. Index

A data structure that speeds up search. Without an index, Milvus does a brute-force scan.

Common index types:
- `FLAT` — exact search, slow on large data, good for testing
- `IVF_FLAT` — approximate, faster on large datasets
- `HNSW` — graph-based, best speed/accuracy tradeoff for production

---

## 7. Milvus Lite vs Milvus Standalone

| | Milvus Lite | Milvus Standalone |
|---|---|---|
| Storage | Local `.db` file | Docker containers |
| Use case | Local dev / learning | Shared / production |
| Setup | `pip install pymilvus` only | Docker compose |
| Connection | `MilvusClient("file.db")` | `MilvusClient("http://localhost:19530")` |

---

## Next: Implement

Once you understand the above, move to `milvus_demo_local.py` to:
1. Create a collection with `dimension=768, metric_type="COSINE"`
2. Generate real embeddings from text
3. Insert and search
