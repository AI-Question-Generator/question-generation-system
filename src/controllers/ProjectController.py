from .BaseController import BaseController
from fastapi import  UploadFile
import os
class ProjectController(BaseController):
  '''Controller for managing projects, including project paths and related operations.'''
  
  def __init__(self):
    super().__init__()

  def get_project_path(self, project_id):
    
    project_path = os.path.join(self.files_dir, project_id)
    
    if not os.path.exists(project_path):
      os.makedirs(project_path)
    
    return project_path
    
    
