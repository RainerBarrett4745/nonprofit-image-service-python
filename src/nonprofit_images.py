from pathlib import Path
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, Field


class ImageRequest(BaseModel):
    kind: Literal["receipt", "reminder", "report"]
    audience: str = Field(min_length=1)
    message: str = Field(min_length=1)


class StoredImage(BaseModel):
    kind: str
    path: Path
    prompt: str


PROMPTS = {
    "receipt": "A warm, clear nonprofit donor receipt illustration",
    "reminder": "A friendly nonprofit volunteer reminder illustration",
    "report": "A clean nonprofit campaign reporting illustration",
}


def build_prompt(request: ImageRequest) -> str:
    return f"{PROMPTS[request.kind]}. Audience: {request.audience}. Message: {request.message}. No text in the image."


def generate_and_store(request: ImageRequest, output_dir: Path, client: OpenAI) -> StoredImage:
    output_dir.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(request)
    response = client.images.generate(model="auto", prompt=prompt)
    image_url = response.data[0].url
    if not image_url:
        raise ValueError("image response did not include a URL")

    # The example keeps persistence deliberately visible: fetch the returned image and save it.
    import urllib.request

    destination = output_dir / f"{request.kind}.png"
    urllib.request.urlretrieve(image_url, destination)
    return StoredImage(kind=request.kind, path=destination, prompt=prompt)
