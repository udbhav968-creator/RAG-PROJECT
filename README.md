# ⚡ Industrial RAG Engine v4.0 Ultimate Suite

[![Build Status](https://img.shields.io/badge/CI%2FCD-Passing-brightgreen?style=for-the-badge&logo=githubactions)](https://github.com/udbhav968-creator/RAG-PROJECT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.1.12-1C3C3C?style=for-the-badge)](https://langchain.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-v3.0+-000000?style=for-the-badge&logo=pinecone)](https://pinecone.io)
[![Redis](https://img.shields.io/badge/Redis-v7.0-DC382D?style=for-the-badge&logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Deployed-326CE5?style=for-the-badge&logo=kubernetes)](https://kubernetes.io)
[![Helm](https://img.shields.io/badge/Helm-Chart%20v4.0-0F1689?style=for-the-badge&logo=helm)](https://helm.sh)

The Ultimate **Retrieval-Augmented Generation (RAG)** platform featuring **HyDE (Hypothetical Document Embeddings)**, **Sub-Millisecond Semantic Vector Caching**, **Voice Query Speech Recognition**, **Synthetic Evaluation Benchmark Generators**, **Enterprise Kubernetes Helm Charts (`deploy/helm/`)**, **Multi-Tenant RBAC Security**, **Guardrails AI PII Shield**, **RAPTOR Tree Indexing**, **Parent-Child Auto-Merging**, and **Interactive Knowledge Graph Canvas**.

---

## 📋 Table of Contents

- [🎯 System Architecture](#-system-architecture)
- [✨ v4.0 Ultimate Innovations](#-v40-ultimate-innovations)
- [📁 Complete Directory Structure](#-complete-directory-structure)
- [🚀 Quick Start & Helm Kubernetes Setup](#-quick-start--helm-kubernetes-setup)
- [🎙️ Voice Query & Interactive Canvas](#️-voice-query--interactive-canvas)
- [🧪 Automated Testing & Verification](#-automated-testing--verification)
- [📄 License & Author](#-license--author)

---

## 🎯 System Architecture

```mermaid
flowchart TD
    User([User / Web Dashboard / Voice Input / API]) -->|Query| Voice[Web Speech Recognition / API]
    Voice --> Guardrails[Guardrails AI & Injection Shield]
    
    Guardrails --> HyDE[HyDE Hypothetical Document Generator]
    HyDE --> SemanticCache{Sub-ms Semantic Vector Cache}
    
    SemanticCache -- Cache Hit > 0.92 -- > SubMsResp[Return Sub-Millisecond Result]
    SemanticCache -- Cache Miss -- > Router[Agentic Query Router]
    
    Router -->|Vector Search| ParentChild[Parent-Child Auto-Merging Retriever]
    Router -->|RAPTOR Summaries| RAPTOR[RAPTOR Recursive Tree Indexer]
    Router -->|Relational Graph| GraphRAG[GraphRAG Knowledge Graph Search]
    
    ParentChild --> Generator[LLM Generator / Model Selector]
    RAPTOR --> Generator
    GraphRAG --> Generator
    
    Generator --> TriadEval[RAG Triad Evaluator & Self-Correction]
    TriadEval --> SSEStream[Real-Time SSE Stream Gateway]
    SSEStream --> User
```

---

## ✨ v4.0 Ultimate Innovations

1. 🔮 **HyDE (Hypothetical Document Embeddings)** (`app/core/hyde.py`):
   - Generates candidate hypothetical answers to bridge query-chunk semantic embedding alignment.

2. ⚡ **Sub-Millisecond Semantic Vector Cache** (`app/cache/semantic_cache.py`):
   - Cosine similarity matching ($>0.92$ threshold) to serve cached answers instantly without LLM latency.

3. 🎙️ **Voice Query & Speech Synth Web UI**:
   - Web Speech API microphone speech recognition directly on the Web Console.

4. 🧪 **Synthetic Evaluation Test Case Generator** (`scripts/generate_synthetic_evals.py`):
   - Automatically generates Question-Context-Answer test triples from ingested documents.

5. 📦 **Enterprise Kubernetes Helm Chart** (`deploy/helm/rag-chart/`):
   - Production Helm Chart with deployment, service, and HPA auto-scaler definitions.

---

## 📁 Complete Directory Structure

```text
RAG-PROJECT/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI/CD workflow
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── audit.py        # CSV audit export endpoint
│   │           ├── graph.py        # Knowledge Graph Data API
│   │           ├── ingest.py       # File (.pdf, .docx, .txt) ingestion API
│   │           └── query.py        # Standard & SSE streaming query API
│   ├── cache/
│   │   ├── redis_client.py         # Redis cache manager
│   │   └── semantic_cache.py       # Sub-ms Semantic Vector Cache
│   ├── core/
│   │   ├── correction.py           # Self-Correction loop
│   │   ├── evaluator.py            # RAG Triad Evaluator
│   │   ├── generation.py           # LLM answer generator
│   │   ├── graph_rag.py            # Knowledge Graph engine
│   │   ├── guardrails.py           # Guardrails AI PII & Injection shield
│   │   ├── hyde.py                 # HyDE retriever engine
│   │   ├── parent_child.py         # Parent-Child auto-merging engine
│   │   ├── raptor.py               # RAPTOR tree summarizer
│   │   ├── rag_pipeline.py         # RAG Pipeline orchestrator
│   │   ├── retrieval.py            # Pinecone & BM25 hybrid search
│   │   ├── router.py               # Agentic router
│   │   ├── security.py             # Multi-tenant RBAC security
│   │   └── self_query.py           # Self-querying filter engine
│   ├── static/
│   │   └── index.html              # Web Dashboard with Voice & Graph Canvas
│   └── main.py                     # FastAPI application entrypoint
├── deploy/
│   └── helm/
│       └── rag-chart/              # Kubernetes Helm Chart
├── scripts/
│   ├── benchmark_triad.py          # RAG Triad benchmark
│   ├── benchmark_worldclass.py     # Architectural profiler
│   └── generate_synthetic_evals.py # Synthetic evals generator
├── tests/
│   └── test_rag.py                 # Automated test suite (100% Pass)
└── requirements.txt                # Dependencies
```

---

## 🚀 Quick Start & Helm Setup

```bash
# Helm Kubernetes Deployment
helm install rag-release ./deploy/helm/rag-chart

# Local Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Automated Testing & Verification

```bash
python -m unittest tests/test_rag.py -v
```

All unit tests pass 100%.

---

## 📄 License & Author

Developed and maintained by **[udbhav968-creator](https://github.com/udbhav968-creator)**. Distributed under the MIT License.