from google.genai.types import GenerateContentConfig
from google.genai.client import Client
from typing import Any

DEFAULT_TIMEOUT = 180

def safe_generate_content(
    client: Client,
    model_name: str,
    config: GenerateContentConfig,
    contents: Any
):
    # Convert the incoming config to a dict so we can inspect/modify it
    merged = config.to_dict()

    # Only add timeout if the caller did NOT specify one
    if "timeout" not in merged or merged["timeout"] is None:
        merged["timeout"] = DEFAULT_TIMEOUT

    # Rebuild a proper GenerateContentConfig object
    merged_config = GenerateContentConfig(**merged)

    try:
        return client.models.generate_content(
            model=model_name,
            config=merged_config,
            contents=contents
        )

    except errors.ServerError as e:
        # your existing error handling
        raise