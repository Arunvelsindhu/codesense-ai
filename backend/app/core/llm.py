import time
from google import genai
from app.core.config import settings

# Create Gemini client
client = genai.Client(api_key=settings.gemini_api_key)

DEFAULT_MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]


def get_llm_response(prompt: str, model_name: str = DEFAULT_MODEL, retries: int = 2) -> str:
    """
    Generate text using Gemini. Retries the primary model briefly, then
    falls back to alternate models if the primary is overloaded/unavailable.
    """
    models_to_try = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]

    last_error = None

    for current_model in models_to_try:
        for attempt in range(retries):
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                )
                return response.text

            except Exception as e:
                last_error = e
                print("=" * 60)
                print(f"LLM ERROR (model={current_model}, attempt {attempt + 1}/{retries})")
                print(e)
                print("=" * 60)
                time.sleep(3 * (attempt + 1))

        print(f"Giving up on {current_model}, trying next fallback model if available...")

    raise last_error


def get_embedding(text: str, retries: int = 3) -> list:
    """
    Generate embeddings using Gemini, with retry on transient errors (e.g. 503).
    """
    for attempt in range(retries):
        try:
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            return response.embeddings[0].values

        except Exception as e:
            is_last = attempt == retries - 1
            print("=" * 60)
            print(f"EMBEDDING ERROR (attempt {attempt + 1}/{retries})")
            print(e)
            print("=" * 60)
            if is_last:
                raise
            time.sleep(3 * (attempt + 1))