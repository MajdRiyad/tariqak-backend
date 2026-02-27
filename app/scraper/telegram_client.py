from telethon import TelegramClient
from telethon.sessions import StringSession
from app.config import settings

_client: TelegramClient | None = None


def get_telegram_client() -> TelegramClient:
    global _client
    if _client is None:
        _client = TelegramClient(
            StringSession(settings.telegram_string_session),
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
    return _client
