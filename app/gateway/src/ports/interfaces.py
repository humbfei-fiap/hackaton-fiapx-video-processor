from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import User, Video

class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

class VideoRepository(ABC):
    @abstractmethod
    def create(self, video: Video) -> Video:
        pass

    @abstractmethod
    def list_by_user(self, user_id: int) -> List[Video]:
        pass
    
    @abstractmethod
    def get_by_id(self, video_id: int) -> Optional[Video]:
        pass

class MessageBroker(ABC):
    @abstractmethod
    def publish_video_processing(self, video_id: int, filename: str):
        pass

class VideoCache(ABC):
    @abstractmethod
    def get_user_videos(self, user_id: int) -> Optional[List[Video]]:
        pass
    
    @abstractmethod
    def set_user_videos(self, user_id: int, videos: List[Video]):
        pass

class FileStorage(ABC):
    @abstractmethod
    def save(self, file_content, filename: str) -> str:
        pass
