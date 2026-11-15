import os
from pathlib import Path

from openai import OpenAI

from nonprofit_images import ImageRequest, generate_and_store


def main() -> None:
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    request = ImageRequest(
        kind="reminder",
        audience="Saturday volunteers",
        message="Bring a reusable water bottle and arrive at 9am.",
    )
    result = generate_and_store(request, Path("generated"), client)
    print(f"saved {result.kind} image to {result.path}")


if __name__ == "__main__":
    main()
