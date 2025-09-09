import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# --- PostgreSQL Connection ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ChromaDB Connection ---
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")
chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

# Explicitly create an embedding function using the Google Generative AI API
google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv("GOOGLE_API_KEY"))

# Get or create the collection, specifying the embedding function to ensure consistency
collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=google_ef
)

