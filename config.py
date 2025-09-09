# backend/config.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("AIzaSyBx9LotrEcg__1Sb9NSSqkPPdIjmYmRfMw")