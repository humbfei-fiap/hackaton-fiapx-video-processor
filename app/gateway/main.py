from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from datetime import timedelta
from typing import List

import models, database, auth, messaging
from database import engine, get_db
from jose import JWTError, jwt

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FIAP X Video Processor Gateway")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Diretório para salvar os vídeos
UPLOAD_DIR = os.getenv("SHARED_DIR", "/data")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "uploads"), exist_ok=True)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(form_data.password)
    new_user = models.User(username=form_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
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
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Gera um nome único para o arquivo
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, "uploads", unique_filename)
    
    # Salva o arquivo no volume compartilhado
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Registra no banco de dados
    db_video = models.Video(
        filename=unique_filename,
        original_name=file.filename,
        user_id=current_user.id,
        status=models.VideoStatus.PENDING
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    
    # Envia para a fila do RabbitMQ
    try:
        messaging.send_to_queue(db_video.id, unique_filename)
    except Exception as e:
        # Se falhar a fila, poderíamos marcar como erro, mas vamos simplificar por agora
        print(f"Erro ao enviar para fila: {e}")
    
    return {
        "id": db_video.id,
        "filename": file.filename,
        "status": db_video.status.value
    }

@app.get("/status")
def get_status(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    videos = db.query(models.Video).filter(models.Video.user_id == current_user.id).all()
    return [
        {
            "id": v.id,
            "original_name": v.original_name,
            "status": v.status.value,
            "created_at": v.created_at,
            "zip_url": f"/download/{v.zip_path}" if v.zip_path else None
        } for v in videos
    ]

@app.get("/")
async def root():
    return {"message": "FIAP X Video Processor API Gateway is running"}