import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/wordlists", tags=["Wordlists"])

WORDLISTS_DIR = "/app/wordlists"

class WordlistInfo(BaseModel):
    name: str
    size_bytes: int

@router.get("", response_model=List[WordlistInfo])
def list_wordlists():
    if not os.path.exists(WORDLISTS_DIR):
        return []
    
    files = []
    for filename in os.listdir(WORDLISTS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(WORDLISTS_DIR, filename)
            files.append(WordlistInfo(name=filename, size_bytes=os.path.getsize(filepath)))
            
    return sorted(files, key=lambda x: x.name)

@router.post("/upload")
def upload_wordlist(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")
        
    os.makedirs(WORDLISTS_DIR, exist_ok=True)
    filepath = os.path.join(WORDLISTS_DIR, file.filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"filename": file.filename, "message": "Uploaded successfully"}
