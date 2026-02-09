from enum import Enum

class ResponseSignal(Enum):
  FILE_TYPE_NOT_ALLOWED = "file type not allowed"
  FILE_SIZE_EXCEEDED = "file size exceeded"
  FILE_UPLOADED_SUCCESSFULLY = "file uploaded successfully"
  FILE_UPLOAD_FAILED = "file upload failed"
  
  CHUNKING_COMPLETED = "chunking process completed successfully"
  CHUNKING_FAILED = "chunking failed"
  
  NO_FILES_IDS = "No Files Founded"
  FILE_ID_ERROR = "No File Founded With This ID"
  
  PROJECT_NOT_FOUND = "Project With This ID Not Found"
  
  INSERT_INTO_VECTOR_DB_ERROR = "Insert Into Vector DB Error"
  INSERT_INTO_VECTOR_DB_SUCCESS = "Insert Into Vector DB Succeed"
  
  VECTOR_DB_COLLECTION_RETRIEVED = "VectorDB Collection Retrieved"
  
  VECTOR_DB_SEARCH_ERROR = "Vector DB Search Error"
  VECTOR_DB_SEARCH_SUCCESS = "Vector DB Search Succeed"