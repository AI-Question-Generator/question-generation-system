APP_NAME=""


FILE_ALLOWED_TYPES=["text/plain", "application/pdf"]
FILE_ALLOWED_SIZE=10
FILE_DEFAULT_CHUNK_SIZE=512000

MONGODB_URL=""
MONGODB_DATABASE=""

# =============================== LLM Config ===============================

GENERATION_BACKEND=""
EMBEDDING_BACKEND=""

OPENAI_API_KEY=""
OPENAI_API_URL=""
GEMINI_API_KEY=""
COHERE_API_KEY=""

GENERATION_MODEL_ID=""
EMBEDDING_MODEL_ID=""
EMBEDDING_MODEL_SIZE=1024

DEFAULT_INPUT_MAX_CHARACHTERS=2048
GENERATION_DEFAULT_MAX_TOKENS=4096
GENERATION_DEFAULT_TEMPERATURE=0.1

# =============================== Vector DB Config ===============================

VECTOR_DB_BACKEND = "QDRANT" 
VECTOR_DB_PATH = "qdrant_db"
VECTOR_DB_DISTANCE_METHOD = "cosine"

# =============================== Template Configs ===============================

PRIMARY_LANG = "en"
DEFAULT_LANG = "en"
