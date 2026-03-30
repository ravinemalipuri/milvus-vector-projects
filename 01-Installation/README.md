# 01-Installation — Local Milvus Setup on Windows

Step-by-step local setup of Milvus vector database on Windows using Docker, and hands-on demos of inserting vectors and searching.

---

## What This Folder Does

| File | Purpose |
|---|---|
| `docker-compose.yml` | Starts Milvus standalone (+ etcd + MinIO) in Docker |
| `requirements.txt` | All Python packages needed |
| `test_connection.py` | Verify Python can connect to Milvus |
| `milvus_demo_local.py` | Create a collection and insert sample vectors |
| `prepare_data.py` | Generate embeddings from text and insert into Milvus |
| `semantic_search.py` | Search by meaning using natural language queries |
| `vector_search_metadata_filter.py` | Search with metadata filters (category, year) |
| `concepts.md` | Key concepts to understand before implementing |
| `Learnings.md` | All errors encountered and how they were fixed |

---

## Quick Start

```powershell
# 1. Start Milvus
docker compose up -d

# 2. Install packages
py -3.12 -m pip install -r requirements.txt

# 3. Test connection
py -3.12 test_connection.py

# 4. Insert data
py -3.12 prepare_data.py

# 5. Search
py -3.12 semantic_search.py

# 6. Search with filters
py -3.12 vector_search_metadata_filter.py
```

---

## Notes

- Requires **Python 3.12** from `python.org` (not Windows Store Python)
- Milvus must be running in Docker before executing any script
- See `Learnings.md` for Windows-specific issues and fixes
