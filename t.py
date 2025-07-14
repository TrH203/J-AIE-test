import os
from dotenv import load_dotenv

load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
e = embeddings.embed_query("What's our Q1 revenue?")

print(e)
print(len(e))