from enum import Enum

class ResponseSignal(Enum):
  PROJECT_CREATED_SUCCESSFULLY = "project created successfully"
  PROJECT_CREATION_FAILED = "project creation failed"
  PROJECT_ALREADY_EXISTS = "project already exists"

  FILE_TYPE_NOT_ALLOWED = "file type not allowed"
  FILE_SIZE_EXCEEDED = "file size exceeded"
  FILE_NO_CONTENT = "file has no content"
  FILE_UPLOADED_SUCCESSFULLY = "file uploaded successfully"
  FILE_UPLOAD_FAILED = "file upload failed"
  
  CHUNKING_COMPLETED = "chunking process completed successfully"
  CHUNKING_FAILED = "chunking failed"
  
  NO_FILES_IDS = "No Files Found"
  FILE_ID_ERROR = "No File Found With This ID"
  
  PROJECT_NOT_FOUND = "Project With This ID Not Found"
  
  INSERT_INTO_VECTOR_DB_ERROR = "Insert Into Vector DB Error"
  INSERT_INTO_VECTOR_DB_SUCCESS = "Insert Into Vector DB Succeed"
  
  VECTOR_DB_COLLECTION_RETRIEVED = "VectorDB Collection Retrieved"
  
  VECTOR_DB_SEARCH_ERROR = "Vector DB Search Error"
  VECTOR_DB_SEARCH_SUCCESS = "Vector DB Search Succeed"
  
  RAG_ANSWER_ERROR = "RAG Answer Error"
  RAG_ANSWER_SUCCESS = "RAG Answer Succeed"
  
  # SAVAAL Pipeline signals
  MAIN_IDEA_EXTRACTION_STARTED = "Main idea extraction started"
  MAIN_IDEA_EXTRACTION_SUCCESS = "Main idea extraction completed successfully"
  MAIN_IDEA_EXTRACTION_FAILED = "Main idea extraction failed"
  
  MAIN_IDEA_RETRIEVAL_SUCCESS = "Main ideas retrieved successfully"
  MAIN_IDEA_RETRIEVAL_FAILED = "Main idea retrieval failed"
  
  MAIN_IDEA_RANKING_SUCCESS = "Main ideas ranked successfully"
  MAIN_IDEA_RANKING_FALIED = "Main idea ranking failed"
  
  NO_MAIN_IDEAS_FOUND = "No main ideas found"
  
  QUESTION_GENERATION_SUCCESS = "Question generation completed successfully"
  QUESTION_GENERATION_FAILED = "Question generation failed"

  INSPIRATION_EXTRACTION_SUCCESS = "Inspiration extraction completed successfully"
  INSPIRATION_NO_CONTENT = "Couldn't extract content from provided text corpus, maybe text is either empty or has no valid content."
  INSPIRATION_EXTRACTION_FAILED = "Inspiration extraction failed"
  