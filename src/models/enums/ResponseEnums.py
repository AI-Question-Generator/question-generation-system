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