Intelligent Workflow Builder - Backend
This repository contains the backend service for the Intelligent Workflow Builder application. It is a FastAPI server responsible for handling document processing, managing AI model interactions, performing web searches, and executing the logic of user-defined workflows.

Features
Document Processing: API endpoint to upload PDF documents, extract text, and store them as vector embeddings in a ChromaDB vector store.

Workflow Execution: Core logic to interpret a workflow created on the frontend, retrieve relevant context from the knowledge base, and generate intelligent responses.

AI Integration: Connects to Google's Gemini API for text embedding and generative AI capabilities.

Web Search: Optionally uses SerpAPI to fetch real-time information from the web to augment AI responses.

Tech Stack
Framework: FastAPI

Databases: PostgreSQL (for metadata), ChromaDB (for vector storage)

AI: Google Gemini API

Web Search: SerpAPI

Containerization: Docker & Docker Compose
