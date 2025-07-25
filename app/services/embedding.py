from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

# Ensure your API key is set in env
embedder = GoogleGenerativeAIEmbeddings(model=os.getenv("EMBEDDING_MODEL_NAME"), google_api_key=os.getenv("GOOGLE_API_KEY"))

async def get_embedding(text: str) -> list[float]:
    return await embedder.aembed_query(text)
