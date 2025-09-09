import os
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from serpapi import GoogleSearch

import models
from database import SessionLocal

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
router = APIRouter()
# Ensure we use the exact same model for querying as we did for storing
embedding_model = SentenceTransformer('all-mpnet-base-v2')

class Node(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]

class Edge(BaseModel):
    source: str
    target: str

class WorkflowPayload(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    query: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/run")
async def run_workflow(payload: WorkflowPayload, db: Session = Depends(get_db)):
    context = ""
    # Create an embedding for the user's query
    query_embedding = embedding_model.encode(payload.query).tolist()
    
    # Find the 2 most similar document chunks from PostgreSQL using L2 distance
    results = db.query(models.DocumentChunk).order_by(models.DocumentChunk.embedding.l2_distance(query_embedding)).limit(2).all()
    if results:
        context = "\n".join([res.content for res in results])

    # The rest of the workflow logic remains the same
    llm_node = next((n for n in payload.nodes if n.data.get('label') == 'LLM Engine'), None)
    if not llm_node:
        raise HTTPException(status_code=400, detail="LLM Engine node is required.")
    
    if llm_node.data.get('webSearch'):
        try:
            search = GoogleSearch({"q": payload.query, "api_key": os.getenv("SERPAPI_API_KEY")})
            search_results = search.get_dict().get("organic_results", [])
            context += "\n\nWeb Search Results:\n" + "\n".join([r.get("snippet", "") for r in search_results[:3]])
        except Exception as e:
            context += f"\n\nWeb Search failed: {e}"

    custom_prompt = llm_node.data.get('prompt', 'Based on the context, answer the user question.')
    prompt_for_llm = f"Context:\n{context or 'No context provided.'}\n\n---\n{custom_prompt}\nUser Question: {payload.query}"
    
    try:
        model_gen = genai.GenerativeModel('gemini-1.5-flash')
        response = model_gen.generate_content(prompt_for_llm)
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Google AI: {e}")

