import shutil
import os
from src.ports.interfaces import FileStorage

class LocalFileStorage(FileStorage):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(os.path.join(self.base_path, "uploads"), exist_ok=True)

    def save(self, file_obj, filename: str) -> str:
        file_path = os.path.join(self.base_path, "uploads", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return file_path
