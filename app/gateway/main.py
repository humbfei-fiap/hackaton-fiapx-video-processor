from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from datetime import timedelta

# Import layers
import models, database, auth
from database import engine, get_db
from src.domain.entities import User as UserEntity
from src.adapters.db.repositories import PostgresUserRepository, PostgresVideoRepository
from src.adapters.messaging.producer import RabbitMQProducer
from src.adapters.storage import LocalFileStorage
from src.use_cases.register_user import RegisterUserUseCase
from src.use_cases.upload_video import UploadVideoUseCase
from src.use_cases.list_videos import ListVideosUseCase
from jose import JWTError, jwt

# Init DB Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FIAP X Video Processor Gateway (Clean Arch)")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency Injection Setup
SHARED_DIR = os.getenv("SHARED_DIR", "/data")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://user:password@rabbitmq:5672/")

def get_current_user_entity(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserEntity:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    repo = PostgresUserRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repo = PostgresUserRepository(db)
    use_case = RegisterUserUseCase(repo, auth.get_password_hash)
    try:
        use_case.execute(form_data.username, form_data.password)
        return {"message": "User created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repo = PostgresUserRepository(db)
    user = repo.get_by_username(form_data.username)
    
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...), 
    current_user: UserEntity = Depends(get_current_user_entity),
    db: Session = Depends(get_db)
):
    video_repo = PostgresVideoRepository(db)
    broker = RabbitMQProducer(RABBITMQ_URL, "video_processing")
    storage = LocalFileStorage(SHARED_DIR)
    
    use_case = UploadVideoUseCase(video_repo, broker, storage)
    
    video = use_case.execute(file.file, file.filename, current_user)
    
    return {
        "id": video.id,
        "filename": video.original_name,
        "status": video.status
    }

@app.get("/status")
def get_status(current_user: UserEntity = Depends(get_current_user_entity), db: Session = Depends(get_db)):
    video_repo = PostgresVideoRepository(db)
    use_case = ListVideosUseCase(video_repo)
    videos = use_case.execute(current_user)
    
    return [
        {
            "id": v.id,
            "original_name": v.original_name,
            "status": v.status,
            "created_at": v.created_at,
            "zip_url": f"/download/{v.zip_path}" if v.zip_path else None
        } for v in videos
    ]

@app.get("/")
async def root():
    return {"message": "FIAP X Video Processor API Gateway is running with Clean Architecture"}
