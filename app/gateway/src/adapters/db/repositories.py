from sqlalchemy.orm import Session
from src.domain.entities import User as UserEntity, Video as VideoEntity, VideoStatus
from src.ports.interfaces import UserRepository, VideoRepository
import models  # Importa os modelos ORM existentes (models.py na raiz de app/gateway)

class PostgresUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserEntity) -> UserEntity:
        db_user = models.User(username=user.username, email=user.email, hashed_password=user.password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity(id=db_user.id, username=db_user.username, email=db_user.email, password=db_user.hashed_password)

    def get_by_username(self, username: str) -> UserEntity:
        db_user = self.db.query(models.User).filter(models.User.username == username).first()
        if db_user:
            return UserEntity(id=db_user.id, username=db_user.username, email=db_user.email, password=db_user.hashed_password)
        return None

class PostgresVideoRepository(VideoRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, video: VideoEntity) -> VideoEntity:
        db_video = models.Video(
            filename=video.filename,
            original_name=video.original_name,
            user_id=video.user_id,
            status=models.VideoStatus.PENDING
        )
        self.db.add(db_video)
        self.db.commit()
        self.db.refresh(db_video)
        
        video.id = db_video.id
        video.created_at = db_video.created_at
        return video

    def list_by_user(self, user_id: int) -> list[VideoEntity]:
        videos = self.db.query(models.Video).filter(models.Video.user_id == user_id).all()
        return [
            VideoEntity(
                id=v.id,
                filename=v.filename,
                original_name=v.original_name,
                user_id=v.user_id,
                status=VideoStatus(v.status.value),
                created_at=v.created_at,
                zip_path=v.zip_path
            ) for v in videos
        ]
        
    def get_by_id(self, video_id: int) -> VideoEntity:
        v = self.db.query(models.Video).filter(models.Video.id == video_id).first()
        if v:
             return VideoEntity(
                id=v.id,
                filename=v.filename,
                original_name=v.original_name,
                user_id=v.user_id,
                status=VideoStatus(v.status.value),
                created_at=v.created_at,
                zip_path=v.zip_path
            )
        return None
