from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class User:
    username: str
    password: str # Hashed
    id: Optional[int] = None

@dataclass
class Video:
    filename: str
    original_name: str
    user_id: int
    status: VideoStatus = VideoStatus.PENDING
    id: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    zip_path: Optional[str] = None
