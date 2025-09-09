import io
import pymupdf
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from database import SessionLocal
import models

router = APIRouter()
# Load a standard model for creating embeddings. This runs locally.
embedding_model = SentenceTransformer('all-mpnet-base-v2') # This model outputs 768 dimensions

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_content = await file.read()
    text = ""
    with pymupdf.open(stream=io.BytesIO(file_content), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    # First, create the main document record to get an ID
    db_document = models.Document(filename=file.filename)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Now, create the embedding for the text content
    embedding = embedding_model.encode(text).tolist()
    
    # Create and store the chunk with its embedding
    db_chunk = models.DocumentChunk(
        document_id=db_document.id, 
        content=text, 
        embedding=embedding
    )
    db.add(db_chunk)
    db.commit()

    return {"filename": file.filename, "message": "Document processed and stored."}

