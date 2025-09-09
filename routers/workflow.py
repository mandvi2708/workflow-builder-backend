import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from serpapi import GoogleSearch

from database import collection

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter()

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

@router.post("/run")
async def run_workflow(payload: WorkflowPayload):
    context = ""
    kb_node = next((node for node in payload.nodes if node.data.get('label') == 'KnowledgeBase'), None)

    if kb_node:
        try:
            results = collection.query(query_texts=[payload.query], n_results=2)
            documents = results.get('documents')
            if documents and documents[0]:
                context = "\n".join(documents[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {e}")

    llm_node = next((node for node in payload.nodes if node.data.get('label') == 'LLM Engine'), None)
    if not llm_node:
        raise HTTPException(status_code=400, detail="Workflow must contain an LLM Engine node.")

    web_search_enabled = llm_node.data.get('webSearch', False)
    if web_search_enabled:
        try:
            search = GoogleSearch({
                "q": payload.query,
                "api_key": os.getenv("SERPAPI_API_KEY")
            })
            search_results = search.get_dict()
            organic_results = search_results.get("organic_results", [])
            search_context = "\n".join([res.get("snippet", "") for res in organic_results[:3]])
            context += f"\n\nWeb Search Results:\n{search_context}"
        except Exception as e:
            context += f"\n\nWeb Search failed: {e}"

    custom_prompt = llm_node.data.get('prompt', 'Based on the context below, answer the user question.')
    prompt_for_llm = f"Context:\n{context if context else 'No context provided.'}\n\n---\n{custom_prompt}\nUser Question: {payload.query}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_for_llm)
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Google AI: {e}")

