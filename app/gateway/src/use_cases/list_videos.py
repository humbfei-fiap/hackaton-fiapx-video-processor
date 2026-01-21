from typing import List
from src.domain.entities import Video, User
from src.ports.interfaces import VideoRepository

class ListVideosUseCase:
    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    def execute(self, user: User) -> List[Video]:
        return self.video_repo.list_by_user(user.id)
