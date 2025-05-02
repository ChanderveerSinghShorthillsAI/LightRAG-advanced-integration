# LightRAG Custom Integration Demo: Ollama, Weaviate, Neo4j

This project demonstrates a **custom, production-grade Retrieval-Augmented Generation (RAG) pipeline** using [LightRAG](https://github.com/kaistAI/lightRAG), with advanced integration of **Ollama** (LLM), **E5** (embeddings), **Weaviate** (vector database), and **Neo4j** (graph database).  
It includes custom backend code to enable Weaviate support and a flexible, interactive chatbot interface for querying your own documents.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Custom Integrations](#custom-integrations)
- [File Structure](#file-structure)
- [Extending the Project](#extending-the-project)
- [Troubleshooting](#troubleshooting)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Project Overview

This repository is a hands-on exploration and extension of LightRAG, starting from basic OpenAI-based RAG, then advancing to a highly optimized, production-ready pipeline:

- **Started** with a simple OpenAI-based chatbot (`app/lightrag_openai.py`).
- **Advanced** to a custom pipeline using:
  - **Ollama** as the LLM (with Qwen2.0 model).
  - **E5** as the embedding model.
  - **Weaviate** as the vector database (custom integration).
  - **Neo4j** as the knowledge graph backend.
- **Custom backend**: Implemented `lrag/lightrag/kg/weaviate_vector_db_impl.py` to enable Weaviate support in LightRAG.
- **Main entrypoint**: `app/lightrag_ollama_weaviate_neo4j.py` — a fully interactive chatbot that ingests PDF/TXT, chunks, embeds, and enables advanced querying.

---

## Key Features

- **Plug-and-play RAG**: Swap LLMs, embedding models, and vector/graph backends.
- **Custom Weaviate integration**: Full support for Weaviate as a vector DB, including centroid management and S3 backup.
- **Ollama LLM**: Use local or remote LLMs (Qwen2.0) for fast, private inference.
- **E5 Embeddings**: Efficient, high-quality embeddings for retrieval.
- **Neo4j GraphRAG**: Enhanced entity/relation reasoning and graph-based retrieval.
- **Interactive CLI chatbot**: Ingest your own documents and ask questions in real time.
- **Production logging**: Rotating logs, debug options, and robust error handling.
- **Extensible**: Easily add new backends, models, or chunking strategies.

---

## Architecture

```
User Query
   │
   ▼
[LightRAG Pipeline]
   │
   ├─► [Chunking & Embedding (E5)]
   │
   ├─► [Vector Search (Weaviate)]
   │
   ├─► [Graph Reasoning (Neo4j)]
   │
   └─► [LLM Generation (Ollama/Qwen2.0)]
   │
   ▼
Response
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd lightRAG\ demo
```

### 2. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- **Dependencies**: `sentence-transformers`, `fitz` (PyMuPDF), `weaviate-client`, `neo4j`, `ollama`, `openai`, etc.

### 3. Set Environment Variables

Instead of using a `.env` file, **export all required variables in your shell** before running the project. Example:

```bash
export WEAVIATE_URL="https://your-weaviate-instance"
export WEAVIATE_API_KEY="your-weaviate-api-key"
export EMBEDDING_DIMENSIONS=768
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-neo4j-password"
export LOG_DIR="/path/to/logs"
export LOG_MAX_BYTES=10485760
export LOG_BACKUP_COUNT=5
# Add any other variables required by your settings.py or code
```

> **Tip:** You can add these to your `.bashrc` or `.zshrc` for convenience.

### 4. Start Required Services

#### a. **Start Ollama Server**

```bash
ollama serve
ollama pull qwen2:0.5b
```

#### b. **Start Neo4j Database**

If you have Neo4j installed locally:

```bash
neo4j start
```

Or use Docker:

```bash
docker run -d --name neo4j -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/your-neo4j-password neo4j:latest
```

#### c. **Start Weaviate (if running locally)**

If you use a local Weaviate instance, follow [Weaviate's documentation](https://weaviate.io/developers/weaviate/installation/docker-compose) or use your cloud endpoint.

### 5. Prepare Data

- Place your document (TXT or PDF) in the project directory (e.g., `book3.txt`).

---

## Usage

### Run the Main Demo

```bash
python app/lightrag_ollama_weaviate_neo4j.py
```

- The script will:
  - Extract text from your document.
  - Chunk and embed using E5.
  - Store embeddings in Weaviate.
  - Store entities/relations in Neo4j.
  - Enter an interactive CLI for querying.

#### Example Interaction

```
Your question: Who is Silas?
Answer: Silas is a character in the story...
```

- Type `exit`, `quit`, or `q` to leave.

---

## Custom Integrations

### 1. **Weaviate Vector DB Integration**

- Implemented in [`lrag/lightrag/kg/weaviate_vector_db_impl.py`](lrag/lightrag/kg/weaviate_vector_db_impl.py).
- Handles:
  - Upserting embeddings and metadata.
  - Centroid calculation and S3 backup.
  - Batch operations and error handling.
- Registered in `lrag/lightrag/kg/__init__.py` for LightRAG compatibility.

### 2. **Ollama LLM + E5 Embeddings**

- LLM: Qwen2.0 via Ollama (`ollama_model_complete`).
- Embeddings: E5 (`intfloat/e5-base-v2`), with custom formatting for queries/passages.

### 3. **Neo4j Graph Storage**

- Used for entity/relation storage and graph-based retrieval.
- Enables advanced GraphRAG capabilities.

---

## File Structure

```
app/
├── lightrag_openai.py                # Simple OpenAI-based RAG demo
├── lightrag_ollama_weaviate_neo4j.py # Main custom demo (Ollama + Weaviate + Neo4j)
├── core/
│   └── settings.py                   # Project settings and credentials
├── book3.txt                         # Example document
lrag/
└── lightrag/
    ├── kg/
    │   ├── weaviate_vector_db_impl.py # Custom Weaviate integration
    │   └── __init__.py                # Backend registration
    └── ...                            # LightRAG core modules
```

---

## Extending the Project

- **Add new LLMs**: Swap `llm_model_func` in your main script.
- **Change embedding model**: Update `EmbeddingFunc` in your config.
- **Switch vector/graph DB**: Change `vector_storage`/`graph_storage` in LightRAG instantiation.
- **Tune chunking**: Adjust chunk size and overlap in your ingestion logic.
- **Web UI**: Integrate with the LightRAG React web UI for a graphical interface.

---

## Troubleshooting

- **.gitignore not working?**  
  Run `git init` to start tracking files, then check your `.gitignore`.
- **Weaviate/Neo4j connection errors?**  
  Ensure endpoints, API keys, and network access are correct.
- **Ollama not responding?**  
  Make sure Ollama is running and the model is pulled.
- **Module not found?**  
  Check your `PYTHONPATH` and ensure all dependencies are installed.

---

## Acknowledgements

- [LightRAG](https://github.com/kaistAI/lightRAG) by KAIST AI
- [Weaviate](https://weaviate.io/)
- [Neo4j](https://neo4j.com/)
- [Ollama](https://ollama.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Project Gutenberg](https://www.gutenberg.org/) for sample texts

---

## License

This project is for educational and research purposes.  
See [LICENSE](LICENSE) and respect third-party licenses (e.g., Project Gutenberg texts).

---