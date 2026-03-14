from .BaseController import BaseController
from models.db_schemas import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from helpers.config import get_settings, Settings
from typing import List
import json
import time


class NLPController(BaseController):
  '''Controller for handling NLP-related operations, including vector database management and RAG question answering.'''
  
  def __init__(self, vectordb_client, generation_client, embedding_client,template_parser):
    
    super().__init__()
    
    self.vectordb_client = vectordb_client
    self.generation_client = generation_client
    self.embedding_client = embedding_client
    self.template_parser = template_parser
    
    
    
  def create_collection_name(self, project_id: str):
    return f"collection_{project_id}".strip()
  
  async def reset_vector_db_collection(self, project: Project):
    collection_name = self.create_collection_name(project_id=project.project_id)
    return self.vectordb_client.delete_collection(collection_name=collection_name)
  
  
  async def get_vector_db_collection_info(self, project: Project):
    collection_name = self.create_collection_name(project_id=project.project_id)
    collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
    
    return json.loads(
      json.dumps(collection_info, default=lambda x : x.__dict__)
    )
  
  async def index_into_vector_db(self,project: Project, chunks: List[DataChunk],
                                chunks_ids : List[int],
                                do_reset: bool = False):
    
    # get collection name
    collection_name = self.create_collection_name(project_id=project.project_id)
    
    # manage items
    texts = [ c.chunk_text for c in chunks]
    metadata = [ c.chunk_metadata | {'db_id': str(c.id)} for c in chunks]
    

    vectors = []
    for text in texts:
        vectors.append( await self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value))
    
    # create collection name if not exists
    _ = self.vectordb_client.create_collection( collection_name=collection_name,
                                                embedding_size=self.embedding_client.embedding_size,
                                                do_reset=do_reset)
    
    # push into vector db
    
    result = self.vectordb_client.insert_many(
      collection_name=collection_name,
      texts=texts,
      vectors=vectors,
      metadata=metadata,
      record_ids=chunks_ids
      )
    
    return result
  
  async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
    
    # get collection name
    collection_name = self.create_collection_name(project_id=project.project_id)
    
    # embedding user query
    vector = await self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)
    
    if not vector or len(vector) == 0:
      return False
    
    # semantic search step
    
    results = self.vectordb_client.search_by_vector(  collection_name=collection_name,
                                                      vector=vector, limit=limit)
    
    return results
  
  
  async def search_chunks_metadata(self, project: Project, text: str, limit: int = 10):
    
    # get collection name
    collection_name = self.create_collection_name(project_id=project.project_id)
    
    # embedding user query
    vector = await self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)
    if not vector or len(vector) == 0:
      return False
    
    # semantic search step for metadata
    
    results = self.vectordb_client.search_chunks_metadata_by_vector(
                                                      collection_name=collection_name,
                                                      vector=vector, 
                                                      limit=limit)
    
    return results
  
  
  async def answer_rag_question(self,  project: Project, query: str, limit: int = 10):
    
    answer, full_prompt, chat_history = None, None, None
    
    retrieved_documents = await self.search_vector_db_collection( project=project,
                                                            text=query,
                                                            limit=limit)
    

    
    if not retrieved_documents or len(retrieved_documents) == 0:
      return answer, full_prompt, chat_history
    
    system_prompt = self.template_parser.get("rag", "system_prompt")
        
    documents_prompts = "\n".join([
      self.template_parser.get( "rag",
                                "document_prompt",{
                                "doc_num":idx+1,
                                "chunk_text":doc.text
                              })
      for idx, doc in enumerate(retrieved_documents)
    ])
    
    
    footer_prompt = self.template_parser.get("rag", "footer_prompt")
    
    
    chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]
    
    full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

    
    answer = await self.generation_client.generate_text(
      prompt=full_prompt,
      chat_history=chat_history,
      # max_output_tokens=self.generation_client.default_generation_max_output_tokens,
      # temperature=self.generation_client.default_generation_temperature
    )
    
    return answer, full_prompt, chat_history