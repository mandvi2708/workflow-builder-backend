import io
import os
import pymupdf
import google.generativeai as genai
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, collection
import models

# This configures the Google AI client with your API key from the .env file
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter()

def get_db():
    """Dependency to get a new database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    This endpoint handles PDF document uploads. It performs the following steps:
    1. Validates that the uploaded file is a PDF.
    2. Extracts text content from the PDF using PyMuPDF.
    3. Generates vector embeddings for the text using Google's Gemini API.
    4. Stores the embeddings and text in the ChromaDB vector store.
    5. Stores the document's metadata (filename) in the PostgreSQL database.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_content = await file.read()
    text = ""
    with pymupdf.open(stream=io.BytesIO(file_content), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    # Generate embeddings using Google's model
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT" # Specify the task for better embeddings
        )
        embedding = result['embedding']
    except Exception as e:
        # Catch potential errors from the Google API (e.g., invalid key)
        raise HTTPException(status_code=500, detail=f"Error with Google AI: {e}")

    # Store embeddings in ChromaDB, using the filename as a unique ID
    collection.add(
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"filename": file.filename}],
        ids=[file.filename]
    )

    # Store metadata in PostgreSQL
    db_document = models.Document(filename=file.filename)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return {"filename": file.filename, "message": "Document processed successfully with Gemini."}

