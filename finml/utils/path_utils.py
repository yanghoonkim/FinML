import os

def set_path(dir_path=None):
    if not os.path.exists(dir_path):
      os.makedirs(dir_path)

    return dir_path


