User: Role:
Senior LLM Engineer

Context:
I'm building a Question Generation System, part of the production pipeline is converting each lesson (Project in our case) into set of MainIdeas & related chunks to each Main Idea.

MainIdeas & Chunks Production Pipeline:
[1] Savaal extracts main ideas from sections of the document in parallel.
[2] combines them into a succinct list.
[3] ranks them in order of importance.
[4] Savaal fetches relevant passages from the document using a vector-based retrieval model.
Finally, [5] given a main idea and fetched passages, Savaal
generates questions.

Regarding the project structure, we are using the MVC design pattern (but without views as we build only the backend part).
I want to add the MainIdea and Chunks models to store them in the database and retrieve them later when needed.

Task:
Help me decide how to organize this process (as Outlines), what is the recommended way of building the models and controllers.
Help me also solve the confusion of making a separate collection for the chunks with embeddings (in addition to the original chunks collection) or just make one collection that has chunks with embeddings.

GitHub Copilot: 

User: Role:
Senior LLM Engineer

Context:
I'm building a Question Generation System, part of the production pipeline is converting each lesson (Project in our case) into set of MainIdeas & related chunks to each Main Idea.

MainIdeas & Chunks Production Pipeline:
[1] Savaal extracts main ideas from sections of the document in parallel.
[2] combines them into a succinct list.
[3] ranks them in order of importance.
[4] Savaal fetches relevant passages from the document using a vector-based retrieval model.
Finally, [5] given a main idea and fetched passages, Savaal
generates questions.

Regarding the project structure, we are using the MVC design pattern (but without views as we build only the backend part).
I want to add the MainIdea and Chunks models to store them in the database and retrieve them later when needed.

Task:
Help me decide how to organize this process (as Outlines), what is the recommended way of building the models and controllers.
Help me also solve the confusion of making a separate collection for the chunks with embeddings (in addition to the original chunks collection) or just make one collection that has chunks with embeddings.

Workspace: Collecting workspace information## 1) Recommended process organization (Outlines)

Treat this as a **repeatable “Project → Knowledge Graph-ish artifacts” pipeline** with clear persisted checkpoints:

1. **Ingest**
   - Upload asset(s): already in `routes.data.upload`
   - Chunk & persist canonical chunks: already in `routes.data.process_endpoint` using `controllers.ProcessController` and storing `models.db_schemas.DataChunk` via `models.ChunkModel`

2. **Main Ideas Extraction (parallel over sections)**
   - Input: chunks for a project (ideally grouped by section/page from `chunk_metadata`)
   - Output: “candidate main ideas” (many, redundant)

3. **Main Ideas Consolidation**
   - Deduplicate/merge candidates into a succinct list

4. **Main Ideas Ranking**
   - Assign `rank` (importance order) + optional scoring rationale

5. **Retrieval (per Main Idea)**
   - Fetch relevant chunks via vector search (Qdrant)
   - Persist **the association**: main_idea ⇄ chunk (+ similarity score + run metadata)

6. **Question Generation (per Main Idea)**
   - Use (main_idea + retrieved chunks) → questions
   - (Optionally) persist generation runs for reproducibility

This mirrors your startup wiring in `main.app.startup_span`: you already separate `generation_client`, `embedding_client`, and `vectordb_client`.

---

## 2) Models + Controllers: what to add and where (MVC-ish)

### Database schemas (Pydantic)
Follow your existing pattern in `models.db_schemas`.

Add:
- `MainIdea` schema (new file `src/models/db_schemas/main_idea.py`)
  - `project_id: ObjectId`
  - `text: str`
  - `rank: int`
  - `source: dict | None` (optional: which section/pages contributed)
  - `created_at`
- `MainIdeaChunk` schema (new file `src/models/db_schemas/main_idea_chunk.py`)
  - `project_id: ObjectId`
  - `main_idea_id: ObjectId`
  - `chunk_id: ObjectId`
  - `score: float`
  - `retriever: str` (e.g., `qdrant`)
  - `embedding_model_id: str` (important if you ever change embeddings)
  - `created_at`

Why a link collection? It keeps your model flexible:
- multiple retrieval runs,
- multiple embedding models,
- avoids huge arrays inside a `MainIdea` document.

### Mongo “Model” classes (data access)
Follow `models.ProjectModel`, `models.ChunkModel`, `models.AssetModel`:

- `MainIdeaModel`: CRUD main ideas, list by project, update ranks
- `MainIdeaChunkModel`: bulk insert associations, query top chunks for a main idea, etc.

Also update `models.enums.DataBaseEnum` with new collection names.

### Controllers (business logic)
Keep controllers as “services” (your current style):

- `MainIdeaController`
  - `extract_candidates(project_id)` (parallelizable)
  - `consolidate(candidates)`
  - `rank(main_ideas)`
  - Persists via `MainIdeaModel`

- `RetrievalController`
  - `embed_main_idea(text)` using `request.app.embedding_client` (wired in main.py)
  - `search_chunks(project_id, vector)` using `stores.vectordb.providers.QdrantDBProvider`
  - Persists associations via `MainIdeaChunkModel`

- (Optional) `PipelineController`
  - One orchestrator method: `build_main_ideas_and_links(project_id, do_reset=False)` that calls the above steps deterministically.

This keeps `routes/*` thin like your existing `routes.data`.

---

## 3) “Separate collection for embedded chunks?” — recommended approach

### Best practice for your current architecture (Mongo + Qdrant)
**Do not store embeddings inside Mongo `chunks` documents.**  
Instead:

- Mongo `chunks` (canonical text + metadata): `models.db_schemas.DataChunk`
- Qdrant holds vectors, with payload containing identifiers:
  - `chunk_id` (Mongo ObjectId as string)
  - `project_id`
  - any metadata you need for filtering

Reasoning:
- Embeddings are large (e.g., 1024 floats). Storing them in Mongo bloats documents and costs RAM/IO.
- You already have a dedicated vector store and a provider abstraction via `stores.vectordb.VectorDBInterface` + `stores.vectordb.VectorDBProviderFactory`.
- Qdrant is built for this exact retrieval step; Mongo is built for canonical records and relations.

### When would you add a separate Mongo collection for embeddings?
Only if you need **audit/versioning** or **multi-embedding backends** without relying on the vector DB as source of truth. If so, add a small “pointer” collection, not full vectors:

- `chunk_vectors` collection:
  - `chunk_id`, `project_id`
  - `embedding_model_id`, `dim`
  - `vector_db_backend` (`QDRANT`)
  - `qdrant_point_id` (or whatever ID you use)
  - timestamps / job_id

This gives reproducibility while keeping vectors out of Mongo.

### Avoid: “two chunk collections (one raw, one embedded)”
That typically creates sync bugs (delete/update/reset drift). Prefer **one canonical chunk collection** + **one vector index** + **one link collection** (`MainIdeaChunk`) for retrieval results.

---

If you implement only one new persistence layer first, make it: **`MainIdea` + `MainIdeaChunk`** (link table) and keep embeddings solely in Qdrant via `stores.vectordb.providers.QdrantDBProvider`.