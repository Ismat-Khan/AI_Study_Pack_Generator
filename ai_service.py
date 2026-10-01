import json
import re
from openai import OpenAI

MODEL = "openai/gpt-oss-120b"
BASE_URL = "https://api.groq.com/openai/v1"

def create_client(api_key: str) -> OpenAI:
    if not api_key:
        raise ValueError("Groq API key is missing.")
    return OpenAI(api_key=api_key, base_url=BASE_URL)

def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            result = json.loads(text[start:end + 1])
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
    raise ValueError("AI returned invalid JSON. The response may have been truncated. Try again with less source material.")

def ask_ai(api_key: str, system_prompt: str, user_prompt: str) -> dict:
    client = create_client(api_key)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            temperature=0.15,
            max_tokens=12000,
            response_format={"type":"json_object"},
        )
        content = (response.choices[0].message.content or "").strip()
        return _extract_json(content)
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise RuntimeError(f"AI service error: {exc}") from exc
