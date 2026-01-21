import redis
import json
import os
from typing import List, Optional
from src.ports.interfaces import VideoCache
from src.domain.entities import Video, VideoStatus

class RedisVideoCache(VideoCache):
    def __init__(self, redis_url: str, ttl_seconds: int = 10):
        self.client = redis.from_url(redis_url)
        self.ttl = ttl_seconds

    def get_user_videos(self, user_id: int) -> Optional[List[Video]]:
        key = f"user_videos:{user_id}"
        data = self.client.get(key)
        if data:
            try:
                videos_json = json.loads(data)
                return [
                    Video(
                        id=v["id"],
                        filename=v["filename"],
                        original_name=v["original_name"],
                        user_id=v["user_id"],
                        status=VideoStatus(v["status"]),
                        zip_path=v.get("zip_path")
                    ) for v in videos_json
                ]
            except Exception as e:
                print(f"Erro ao deserializar cache: {e}")
                return None
        return None

    def set_user_videos(self, user_id: int, videos: List[Video]):
        key = f"user_videos:{user_id}"
        # Converter objetos para dict/json
        videos_json = [
            {
                "id": v.id,
                "filename": v.filename,
                "original_name": v.original_name,
                "user_id": v.user_id,
                "status": v.status.value,
                "zip_path": v.zip_path
            } for v in videos
        ]
        self.client.setex(key, self.ttl, json.dumps(videos_json))
