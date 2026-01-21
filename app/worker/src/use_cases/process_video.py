from src.domain.entities import Video, VideoStatus
from src.ports.interfaces import VideoRepository, VideoProcessor, NotificationService
import os

class ProcessVideoUseCase:
    def __init__(self, video_repo: VideoRepository, processor: VideoProcessor, notifier: NotificationService, uploads_dir: str, outputs_dir: str):
        self.video_repo = video_repo
        self.processor = processor
        self.notifier = notifier
        self.uploads_dir = uploads_dir
        self.outputs_dir = outputs_dir

    def execute(self, video_id: int, filename: str):
        print(f"Executing use case for video {video_id}")
        
        # 1. Update status to PROCESSING
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        video.status = VideoStatus.PROCESSING
        self.video_repo.update_status(video)

        try:
            # 2. Process Video
            video_path = os.path.join(self.uploads_dir, filename)
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"File {video_path} does not exist")

            zip_filename = self.processor.extract_frames_to_zip(video_path, self.outputs_dir)

            # 3. Update status to COMPLETED
            video.status = VideoStatus.COMPLETED
            video.zip_path = zip_filename
            self.video_repo.update_status(video)
            
        except Exception as e:
            print(f"Error processing video: {e}")
            video.status = VideoStatus.ERROR
            self.video_repo.update_status(video)
            
            # 4. Notify User
            user_email = self.video_repo.get_user_email_by_video(video_id)
            if user_email:
                self.notifier.notify_error(user_email, filename, str(e))
            
            raise e
