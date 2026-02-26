from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base_router, data_router, nlp_router, savaal_router
from helpers import get_setting, Settings
from pymongo import AsyncMongoClient
from stores.llm import LLMProviderFactory
from stores.llm.LLMEnums import LLMEnums
from stores.vectordb import VectorDBProviderFactory
from stores.vectordb.VectorDBEnums import VectorDBEnums
from stores.llm.templates.template_parser import TemplateParser


@asynccontextmanager
async def lifespan(app: FastAPI):
  
  settings = get_setting()

  app.state.mongodb_conn = AsyncMongoClient(settings.MONGODB_URL)
  app.state.db_client = app.state.mongodb_conn[settings.MONGODB_DATABASE]
  
  llm_provider_factory = LLMProviderFactory(settings)
  vector_db_factory = VectorDBProviderFactory(settings)

  # generation client
  app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
  app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
  
  # embedding client
  app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
  app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)
  
  
  # vector db client
  app.state.vectordb_client = vector_db_factory.create(provider=settings.VECTOR_DB_BACKEND)
  app.state.vectordb_client.connect()
  
  
  app.state.template_parser = TemplateParser( language=settings.PRIMARY_LANG,
                                        default_language=settings.DEFAULT_LANG)
  
  yield
  
  app.state.mongodb_conn.close()
  app.state.vectordb_client.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(base_router)
app.include_router(data_router)
app.include_router(nlp_router)
app.include_router(savaal_router)