# Soual - AI Question Generation Platform (سؤال)

Soual is an AI-powered model-agnostic question generation platform focused on the Egyptian high-school
curriculum. It supports bilingual (Arabic/English) inputs, curriculum-based and
custom-document workflows, and produces pedagogically-aligned questions (MCQ, short
answer, essay, True/False).

Highlights
- Retrieval-augmented generation (RAG) pipeline with vector search (Qdrant)
- Pluggable LLM providers (OpenAI, Gemini, Cohere, Ollama, local models)
- Structured JSON outputs and prompt templates for reproducible generation

Quickstart (local Python)

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install project dependencies

```bash
pip install -r src/requirements.txt
```

3. Copy the example environment file and fill values

```bash
cp src/.env.example src/.env
# edit src/.env and set: MONGODB_URL, MONGODB_DATABASE, GENERATION_BACKEND, GENERATION_MODEL_ID,
# EMBEDDING_BACKEND, EMBEDDING_MODEL_ID, EMBEDDING_MODEL_SIZE, VECTOR_DB_BACKEND, etc.
```

4. Run the app

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Docker (optional)

1. Populate docker environment files

```bash
cd docker/env
cp .env.example.app .env.app
cp .env.example.mongodb .env.mongodb
cp .env.example.grafana .env.grafana
cp .env.example.mongodb-exporter .env.mongodb-exporter
# edit files in docker/env to set credentials
```

2. Start services

```bash
cd docker
docker compose up -d
```

Core concepts & architecture
- Ingestion & chunking: `controllers.ProcessController` — text loaders and chunking
- Storage: MongoDB stores Projects, Assets, Chunks, Main Ideas
- Vector index: Qdrant via `stores.vectordb` providers
- Generation: pluggable LLM providers in `stores.llm.providers`
- Main Idea pipeline: `controllers.MainIdeaController` handles extract/combine/reduce/rank
- Question generation: `controllers.QuestionController` composes context, inspirations, and prompts

Important files
- `src/main.py`: application entrypoint and lifecycle (connections to MongoDB, LLMs, vector DB)
- `src/controllers/`: business logic for ingestion, NLP, main-idea extraction and question generation
- `src/routes/`: API endpoints (data, nlp, savaal, inspiration)
- `src/stores/llm/` and `src/stores/vectordb/`: provider factories and adapters

API highlights
- Create project: `POST /data/create/{project_id}` — initializes project metadata
- Upload file: `POST /data/upload/{project_id}` — multipart file upload
- Process/chunk file: `POST /data/process/{project_id}` — chunking pipeline
- Index into vector DB: `POST /api/v1/nlp/index/push/{project_id}`
- Extract main ideas: `POST /api/v1/savaal/extract/{project_id}`
- Associate chunks: `POST /api/v1/savaal/associate/{project_id}`
- Batch generate questions: `POST /api/v1/savaal/generate`

Further notes
- Postman and Apidog collections are provided under `src/assets/apidoc` for API exploration
- The project contains observability tooling (Prometheus + Grafana) in `docker/grafana`

Paper reference
- Retrieval and generation techniques used here are inspired by:  
[Savaal: Scalable Concept-Driven Question Generation to Enhance Human Learning](https://arxiv.org/abs/2502.12477)
