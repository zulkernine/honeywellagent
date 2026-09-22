from langchain_openai import ChatOpenAI
from config import settings

llm = ChatOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
    model=settings.openrouter_model,
    temperature=0,
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Certificate Operations Agent",
    },
)
