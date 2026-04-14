from langchain_ollama import ChatOllama
from app.config import settings


def get_coordinator_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.coordinator_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
    )


def get_worker_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.worker_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
    )