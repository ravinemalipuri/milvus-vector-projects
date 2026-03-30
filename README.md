# Milvus Vector Database — learn while doing

A practical guide to deploying and connecting to [Milvus](https://milvus.io/), an open-source vector database, from a Windows development machine.

---

## Prerequisites

I already have ( specify what you have):
- Windows laptop with VS Code
- Python (3.8+)
- Docker Desktop for Windows
-  Planning to get Azure for future( you can user your own cloud)
---

## Deployment Options

| | Option 1: Local (Docker Desktop) | Option 2: Cloud (Azure VM / AKS) |
|---|---|---|
| **Best for** | Development, testing | Production, shared environments |
| **Cost** | Free | Azure compute costs |
| **Setup time** | ~10 minutes | ~30–60 minutes |
| **Persistence** | Local volumes | Managed disks / PVC |

---

## Option 1 — Local Setup (Docker Desktop on Windows)

### Step 1: Pull and Run Milvus (Standalone)

Milvus standalone bundles etcd and MinIO into a single compose stack.

Download the official compose file:

```bash
curl -O https://raw.githubusercontent.com/milvus-io/milvus/master/deployments/docker/standalone/docker-compose.yml
```

Start all services:

```bash
docker compose up -d
```

Verify containers are running:

```bash
docker compose ps
```

Expected output — three containers running:
- `milvus-standalone`
- `milvus-etcd`
- `milvus-minio`

Milvus listens on:
- **gRPC**: `localhost:19530`
- **REST API**: `localhost:9091`

### Step 2: Install Milvus Python SDK (on your laptop)

```bash
pip install pymilvus
```

### Step 3: Connect from Windows (Local)

```python
from pymilvus import connections

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

print("Connected to Milvus (local)")
```

---

## Option 2 — Cloud Setup (Azure)

### Step 2a: Option A — Azure VM with Docker

#### Provision the VM

```bash
# Create resource group
az group create --name rg-milvus --location australiaeast

# Create Ubuntu VM (Standard_D4s_v3: 4 vCPU, 16 GB RAM recommended)
az vm create \
  --resource-group rg-milvus \
  --name vm-milvus \
  --image Ubuntu2204 \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard

# Open Milvus gRPC port
az vm open-port \
  --resource-group rg-milvus \
  --name vm-milvus \
  --port 19530 \
  --priority 1001
```

#### Step 3: Install Docker on the Cloud VM

SSH into the VM:

```bash
ssh azureuser@<YOUR_VM_PUBLIC_IP>
```

Install Docker:

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 4: Pull Milvus Docker Image and Run

```bash
# Download the compose file
curl -O https://raw.githubusercontent.com/milvus-io/milvus/master/deployments/docker/standalone/docker-compose.yml

# Start Milvus
docker compose up -d

# Verify
docker compose ps
```

---

### Step 2b: Option B — Azure Kubernetes Service (AKS)

Use this for production-grade, highly available deployments.

#### Provision AKS Cluster

```bash
az group create --name rg-milvus-aks --location australiaeast

az aks create \
  --resource-group rg-milvus-aks \
  --name aks-milvus \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --generate-ssh-keys

az aks get-credentials \
  --resource-group rg-milvus-aks \
  --name aks-milvus
```

#### Install Milvus via Helm

```bash
helm repo add milvus https://zilliztech.github.io/milvus-helm/
helm repo update

helm install milvus milvus/milvus \
  --namespace milvus \
  --create-namespace \
  --set cluster.enabled=false \
  --set standalone.persistence.persistentVolumeClaim.storageClass=managed-csi
```

Expose the service:

```bash
kubectl patch svc milvus \
  -n milvus \
  -p '{"spec": {"type": "LoadBalancer"}}'

# Get the external IP (wait ~2 minutes)
kubectl get svc milvus -n milvus
```

---

## Step 5: Install Milvus SDK on Your Laptop

Install all required packages at once:

```powershell
pip install -r 01-Installation/requirements.txt
```

Or individually:

```powershell
pip install pymilvus[model]
pip install sentence-transformers
pip install torch
```

---

## Known Issues

See [01-Installation/Learnings.md](01-Installation/Learnings.md) for all issues encountered and fixes, including Windows-specific problems with `milvus-lite`, `pip`, PyTorch long paths, and embedding model bugs.

---

## Step 6: Connect from Windows to Milvus

### Local Connection

```python
from pymilvus import connections, utility

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

print("Server version:", utility.get_server_version())
```

### Cloud Connection (VM or AKS External IP)

```python
from pymilvus import connections, utility

MILVUS_HOST = "<YOUR_VM_OR_LB_PUBLIC_IP>"  # e.g. "20.50.100.200"
MILVUS_PORT = "19530"

connections.connect(
    alias="default",
    host=MILVUS_HOST,
    port=MILVUS_PORT
)

print("Server version:", utility.get_server_version())
```

> **Tip:** For production, add authentication:
> ```python
> connections.connect(
>     alias="default",
>     host=MILVUS_HOST,
>     port=MILVUS_PORT,
>     user="root",
>     password="Milvus"
> )
> ```

---

## Quick Smoke Test

Run this after connecting to verify everything works end-to-end:

```python
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
import random

connections.connect(host="localhost", port="19530")

# Define schema
fields = [
    FieldSchema(name="id",        dtype=DataType.INT64,        is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128),
]
schema = CollectionSchema(fields, description="smoke test")

# Create collection
col = Collection("smoke_test", schema)

# Insert random vectors
data = [[random.random() for _ in range(128)] for _ in range(100)]
col.insert([data])
col.flush()

# Build index
col.create_index("embedding", {"index_type": "FLAT", "metric_type": "L2", "params": {}})
col.load()

# Search
results = col.search([data[0]], "embedding", {"metric_type": "L2"}, limit=3)
print("Top 3 nearest IDs:", [r.id for r in results[0]])

# Cleanup
col.drop()
print("Smoke test passed.")
```

---

## Project Structure

```
milvus-vector-projects/
├── README.md
└── 01-Installation/        # Setup scripts and compose files
```

---

## Useful Commands

| Task | Command |
|---|---|
| Start Milvus (local) | `docker compose up -d` |
| Stop Milvus | `docker compose down` |
| View logs | `docker compose logs -f milvus-standalone` |
| Check port open | `Test-NetConnection -ComputerName <IP> -Port 19530` (PowerShell) |
| SSH to Azure VM | `ssh azureuser@<PUBLIC_IP>` |

---

## AI Assistance

This project was co-authored with the assistance of AI-powered LLMs (Large Language Models) & https://milvus.io/docs.  

---

## References

- [Milvus Docs](https://milvus.io/docs)
- [PyMilvus API Reference](https://milvus.io/api-reference/pymilvus/v2.4.x/About.md)
- [Milvus Helm Chart](https://github.com/zilliztech/milvus-helm)
- [Azure AKS Quickstart](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
