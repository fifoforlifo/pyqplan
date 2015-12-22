import os

def ensure_dir_for_path(filepath):
    dirname = os.path.dirname(filepath)
    if not dirname:
        return
    if os.path.exists(dirname):
        return
    os.makedirs(dirname)
