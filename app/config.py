from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_string_session: str = ""
    telegram_channels: str = "ahwalaltreq,a7walstreet,Palestine_Streets_Radar"
    scrape_interval_hours: int = 3

    ollama_base_url: str = "http://localhost:11434"
    ollama_api_key: str = ""
    ollama_model: str = "llama3"

    database_path: str = "./tariqak.db"
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def channel_list(self) -> list[str]:
        return [ch.strip() for ch in self.telegram_channels.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
