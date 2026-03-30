# Learnings — Issues & Fixes (Windows + Milvus Setup)

Real errors encountered while setting up Milvus on Windows, and how they were fixed.

---

## Issue 1: `milvus-lite` not supported on Windows

**Error:**
```
ConnectionConfigException: milvus-lite is required for local database connections.
Please install it with: pip install pymilvus[milvus_lite]
```

**Cause:** `milvus-lite` (file-based `.db` mode) only works on Linux/Mac. Not supported on Windows.

**Fix:** Connect to Milvus running in Docker instead of a `.db` file:

```python
# Do NOT use on Windows:
client = MilvusClient("milvus_demo.db")

# Use this instead:
client = MilvusClient("http://localhost:19530")
```

---

## Issue 2: `AlbertTokenizer has no attribute encode_plus`

**Error:**
```
AttributeError: AlbertTokenizer has no attribute encode_plus. Did you mean: '_encode_plus'?
```

**Cause:** `pymilvus[model]` `DefaultEmbeddingFunction` uses an ONNX-based model (`paraphrase-albert`) that has a tokenizer compatibility bug on Windows with newer versions of `transformers`.

**Fix:** Replace `DefaultEmbeddingFunction` with `sentence-transformers` directly:

```python
# Do NOT use (buggy on Windows):
from pymilvus import model
embedding_fn = model.DefaultEmbeddingFunction()
vectors = embedding_fn.encode_documents(docs)

# Use this instead:
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
vectors = embedding_model.encode(docs).tolist()
```

> Note: `all-MiniLM-L6-v2` outputs **384-dim** vectors. Set `dimension=384` when creating your collection.

---

## Issue 3: PyTorch not found warning

**Warning:**
```
PyTorch was not found. Models won't be available and only tokenizers,
configuration and file/data utilities can be used.
```

**Cause:** `sentence-transformers` requires PyTorch but it wasn't installed.

**Fix:**
```powershell
pip install torch
```

---

## Issue 4: `pip install` fails — OSError broken package metadata

**Error:**
```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory:
'...site-packages\pkg_resources\tests\data\my-test-package_unpacked-egg\...\dependency_links.txt'
```

**Cause:** Corrupted/broken package metadata in Windows Store Python installation.

**Fix:** Upgrade pip and setuptools first:
```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install sentence-transformers
```

---

## Issue 5: `pip install` fails — Windows Long Path limit

**Error:**
```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory:
'...torch\include\ATen\native\transformers\cuda\...\predicated_tile_access_iterator_residual_last.h'
HINT: This error might have occurred since this system does not have Windows Long Path support enabled.
```

**Cause:** Windows default max path length is 260 characters. PyTorch has deeply nested file paths that exceed this.

**Fix — Run PowerShell as Administrator:**
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Restart VS Code, then retry:
```powershell
python -m pip install sentence-transformers torch
```

> To open PowerShell as Administrator: `Win` key → type `PowerShell` → Right-click → **Run as administrator**

---

## Issue 6: PyTorch DLL load failure

**Error:**
```
Error loading "...\torch\lib\c10.dll" or one of its dependencies.
```

**Cause:** PyTorch requires Microsoft Visual C++ Redistributable which is not installed by default.

**Fix:**
1. Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Restart VS Code
3. Retry `python prepare_data.py`

---

## Issue 7: `&&` not valid in PowerShell

**Error:**
```
The token '&&' is not a valid statement separator in this version of the language.
```

**Cause:** `&&` is a bash/cmd operator. PowerShell uses `;` or separate lines.

**Fix:** Run commands separately or use `;`:
```powershell
# Instead of:
docker --version && docker ps

# Use:
docker --version; docker ps
```

---

## Issue 8: `backend="onnx"` requires `optimum` package

**Error:**
```
ModuleNotFoundError: No module named 'optimum'
Exception: Using the ONNX backend requires installing Optimum and ONNX Runtime.
pip install sentence-transformers[onnx]
```

**Cause:** `backend="onnx"` was added as a workaround for PyTorch DLL issues on Windows Store Python 3.11. Not needed on Python 3.12.

**Fix:** Remove `backend="onnx"` — PyTorch works fine on Python 3.12:

```python
# Remove this:
embedding_model = SentenceTransformer("all-MiniLM-L6-v2", backend="onnx")

# Use this:
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
```

---

## Issue 9: HuggingFace unauthenticated warning

**Warning:**
```
Warning: You are sending unauthenticated requests to the HF Hub.
Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

**Cause:** No HuggingFace token set. Models are downloaded anonymously with lower rate limits.

**Fix (optional):** Set a free HuggingFace token:
1. Sign up at `huggingface.co`
2. Go to Settings → Access Tokens → New token
3. Set in PowerShell:
```powershell
$env:HF_TOKEN = "your_token_here"
```
Or add permanently to your user environment variables.

---

## Issue 10: Windows Store Python — PyTorch DLL load failure

**Error:**
```
OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed.
Error loading "...torch\lib\c10.dll" or one of its dependencies.
```

**Cause:** Windows Store Python (installed via Microsoft Store) has sandbox/isolation restrictions that block PyTorch DLL loading.

**Fix:** Uninstall Windows Store Python, install Python 3.12 from `python.org`:
```powershell
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe" -OutFile "$env:TEMP\python-3.12.9.exe"
Start-Process "$env:TEMP\python-3.12.9.exe" -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1" -Wait
```

Then reinstall packages with `py -3.12 -m pip install pymilvus[model] sentence-transformers torch`.

---

## Issue 11: Python code typed directly into PowerShell

**Error:**
```
The 'from' keyword is not supported in this version of the language.
At line:1 char:1 + from pymilvus import MilvusClient
```

**Cause:** Python code was typed/pasted directly into a PowerShell terminal instead of a `.py` file.

**Fix:** Always save code to a `.py` file and run it with:
```powershell
py -3.12 your_script.py
```

---

## Issue 12: Script not found — wrong working directory

**Error:**
```
can't open file 'prepare_data.py': [Errno 2] No such file or directory
```

**Cause:** Running `python prepare_data.py` from the wrong folder.

**Fix:** Always `cd` to the script folder first:
```powershell
cd "C:\Users\ravin_ofqtfxd\OneDrive\Documents\git-ravin-local\milvus-vector-projects\01-Installation"
py -3.12 prepare_data.py
```

---

## Issue 13: Python 3.12 installed but `python` still points to 3.11

**Symptom:**
```
python --version → Python 3.11.9   (expected 3.12)
```

**Cause:** Windows Store Python 3.11 takes PATH priority over newly installed Python 3.12.

**Fix:** Use `py -3.12` launcher explicitly to target the right version:
```powershell
py -3.12 prepare_data.py
py -3.12 -m pip install <package>
```

Or add Python 3.12 Scripts to PATH permanently:
```powershell
$newPath = "C:\Users\ravin_ofqtfxd\AppData\Roaming\Python\Python312\Scripts"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";" + $newPath, "User")
```

---

## Issue 14: BertModel UNEXPECTED key warning

**Warning:**
```
BertModel LOAD REPORT — embeddings.position_ids | UNEXPECTED
```

**Cause:** The `all-MiniLM-L6-v2` model checkpoint has a key (`position_ids`) that the current architecture doesn't expect. Common with models trained on slightly different versions.

**Fix:** Safe to ignore — model loads and works correctly. Not an error.

---

## Key Learnings Summary

| # | Issue | Root Cause | Fix |
|---|---|---|---|
| 1 | `milvus-lite` error | Not supported on Windows | Use Docker `http://localhost:19530` |
| 2 | `AlbertTokenizer` error | ONNX bug in pymilvus on Windows | Use `sentence-transformers` directly |
| 3 | PyTorch not found | Not installed | `pip install torch` |
| 4 | pip OSError metadata | Broken Windows Store Python env | Upgrade pip + setuptools |
| 5 | pip Long Path error | Windows 260-char path limit | Enable Long Paths via Registry (Admin) |
| 6 | PyTorch DLL load failure | Missing Visual C++ Redistributable | Install vc_redist.x64.exe from Microsoft |
| 7 | `&&` not valid | PowerShell syntax | Use `;` or separate commands |
| 8 | `backend="onnx"` error | `optimum` not installed, not needed on 3.12 | Remove `backend="onnx"` |
| 9 | HuggingFace unauthenticated warning | No HF_TOKEN set | Set `$env:HF_TOKEN` (optional) |
| 10 | PyTorch DLL failure | Windows Store Python sandbox restrictions | Install Python 3.12 from python.org |
| 11 | Python code in PowerShell | Wrong terminal usage | Save to `.py` file, run with `py -3.12` |
| 12 | Script not found | Wrong working directory | `cd` to script folder first |
| 13 | `python` points to 3.11 not 3.12 | PATH priority | Use `py -3.12` explicitly |
| 14 | BertModel UNEXPECTED key warning | Model checkpoint mismatch | Safe to ignore |
