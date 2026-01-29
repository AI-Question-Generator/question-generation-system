from helpers import get_setting, Settings
import os
import random
import string


class BaseController:
    def __init__(self, settings: Settings = get_setting()):
        self.settings = settings
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, 'assets', 'files')
        
    def generate_random_string(self, length: int=12):
      return ''.join(random.choices(string.ascii_letters + string.digits, k=length))