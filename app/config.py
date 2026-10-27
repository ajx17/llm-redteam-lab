from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "ollama"  # "ollama" or "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    guardrails_enabled: bool = False
    input_guard_model: str = ""  # e.g. "llama-guard3:1b"; empty turns the input check off
    docs_dir: str = "data/docs"
    top_k: int = 3


settings = Settings()
