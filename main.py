from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import documents, workflow # Import both routers

# This line creates the 'documents' table in your database if it doesn't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS Configuration ---
# Allows your frontend (running on a different port) to communicate with this backend
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Include Routers ---
# This makes the endpoints from your other files available to the application
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(workflow.router, prefix="/workflow", tags=["workflow"])

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

