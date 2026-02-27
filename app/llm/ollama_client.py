import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


async def generate(system_prompt: str, user_prompt: str) -> str:
    """Call Ollama's /api/generate endpoint and return the response text."""
    url = f"{settings.ollama_base_url}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 1024,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama. Is it running? (ollama serve)")
        return '{"checkpoints": []}'
    except httpx.TimeoutException:
        logger.error("Ollama request timed out after 120 seconds.")
        return '{"checkpoints": []}'
    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        return '{"checkpoints": []}'
