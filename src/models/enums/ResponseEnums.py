from enum import Enum

class ResponseSignal(Enum):
  FILE_TYPE_NOT_ALLOWED = "file type not allowed"
  FILE_SIZE_EXCEEDED = "file size exceeded"
  FILE_UPLOADED_SUCCESSFULLY = "file uploaded successfully"
  FILE_UPLOAD_FAILED = "file upload failed"