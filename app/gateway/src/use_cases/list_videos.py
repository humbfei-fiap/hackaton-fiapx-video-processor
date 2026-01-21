from typing import List
from src.domain.entities import Video, User
from src.ports.interfaces import VideoRepository, VideoCache

class ListVideosUseCase:
    def __init__(self, video_repo: VideoRepository, cache: VideoCache):
        self.video_repo = video_repo
        self.cache = cache

    def execute(self, user: User) -> List[Video]:
        # 1. Tentar pegar do cache
        cached_videos = self.cache.get_user_videos(user.id)
        if cached_videos is not None:
            return cached_videos
        
        # 2. Se não tiver, pegar do banco
        videos = self.video_repo.list_by_user(user.id)
        
        # 3. Salvar no cache
        self.cache.set_user_videos(user.id, videos)
        
        return videos
