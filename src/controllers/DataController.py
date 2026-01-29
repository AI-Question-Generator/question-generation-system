from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os
import re
from .ProjectController import ProjectController


class DataController(BaseController):
  def __init__(self):
    super().__init__()
    self.size_scale=1024*1024

  def validate_uploaded_file(self, file: UploadFile):
    
    if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
      return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value
    
    if file.size > self.settings.FILE_ALLOWED_SIZE*self.size_scale:
      return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
    
    return True, ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value
  
  
  def generate_unique_filepath(self, orig_file_name: str, project_id: str):
    
    random_filename = self.generate_random_string()
    project_path = ProjectController().get_project_path(project_id=project_id)
    
    cleaned_filename=self.get_cleaned_filename(orig_file_name=orig_file_name)
    
    new_file_path=os.path.join(project_path,
                              random_filename+"_"+cleaned_filename
                              )
    
    if os.path.exists(new_file_path):
      return self.generate_unique_filepath(orig_file_name=orig_file_name,
                                          project_id=project_id)  
    
    return new_file_path, random_filename+"_"+cleaned_filename
    
    
  def get_cleaned_filename(self, orig_file_name: str):
    # remove special characters
    cleaned_filename = re.sub(r"[^\w.]", "", orig_file_name.strip())
    # replace spaces with underscores
    cleaned_filename = re.sub(" ", "_", cleaned_filename)
    return cleaned_filename