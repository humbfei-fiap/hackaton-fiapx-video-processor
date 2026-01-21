from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI(title="FIAP X Video Processor Gateway")

@app.get("/")
async def root():
    return {"message": "FIAP X Video Processor API Gateway is running"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Placeholder para lógica de upload
    return {"filename": file.filename, "status": "received"}
