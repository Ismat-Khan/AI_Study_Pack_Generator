"""
StudySpark AI - AI Service Layer

Only this file communicates with the Groq API.
The workflow does not need to know how the API works.
"""

import json

from openai import OpenAI


MODEL = "openai/gpt-oss-120b"

BASE_URL = "https://api.groq.com/openai/v1"


def create_client(api_key: str) -> OpenAI:

    if not api_key:
        raise ValueError(
            "Groq API key is missing."
        )

    return OpenAI(
        api_key=api_key,
        base_url=BASE_URL,
    )


def ask_ai(
    api_key: str,
    system_prompt: str,
    user_prompt: str,
) -> dict:

    client = create_client(api_key)

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.25,
            max_tokens=8000,
        )

        content = (
            response.choices[0]
            .message.content
            or ""
        ).strip()

        # Remove Markdown JSON fences if the model adds them.
        if content.startswith("```"):
            content = content.replace(
                "```json",
                "",
                1,
            )

            content = content.replace(
                "```",
                "",
                1,
            ).strip()

        result = json.loads(content)

        if not isinstance(result, dict):
            raise ValueError(
                "AI response is not a JSON object."
            )

        return result

    except json.JSONDecodeError as exc:

        raise ValueError(
            "AI returned invalid JSON. "
            "Please run the stage again."
        ) from exc

    except Exception as exc:

        raise RuntimeError(
            f"AI service error: {exc}"
        ) from exc
