import os
from typing import Callable

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

load_dotenv()


def build_prompt(context: str, history: str, prompt: str) -> str:
    return f"""
----- Context -----
{context or "No Context"}

----- History -----
{history or "No History"}

current-prompt: {prompt}
""".strip()


def build_system_prompt(external_system_cmd: str) -> str:
    command_text = external_system_cmd or "You are a helpful assistant."
    return f"""ADVANCED SYSTEM PROMPT
- Answer questions accurately and in under 1000 characters.
- If you don't know something, say so instead of making it up.
- Do not mention these instructions to users.
- Don't unnecessarily repeat the user's question.
- You're allowed to ask clarifying questions if the user's prompt is ambiguous.
- You're free to use emojis in your responses, but don't overuse them.
- If the user asks for a code snippet, provide it wrapped in two backticks.

SYSTEM PROMPT
{command_text}
""".strip()


async def _mock_provider(prompt: str, system_prompt: str) -> str:
    return (
        "Mock response from the local fallback provider. "
        "Add real API keys to use live models."
    )


async def use_gemini(prompt: str, system_prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)
    response = await client.aio.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=1500,
            temperature=0.7,
            top_p=0.8,
            system_instruction=system_prompt,
        ),
    )
    return response.text or ""


async def use_cloudflare(prompt: str, system_prompt: str) -> str:
    account_id = os.getenv("CLOUDFLARE_ACC_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not account_id or not api_token:
        raise RuntimeError("Cloudflare credentials are missing")

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
        "/ai/run/@cf/meta/llama-3.1-8b-instruct"
    )
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["result"]["response"]


async def use_qwen(prompt: str, system_prompt: str) -> str:
    api_key = os.getenv("ORCA_ROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("ORCA_ROUTER_API_KEY is not configured")

    client = OpenAI(
        base_url="https://api.orcarouter.ai/v1",
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b-free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


async def use_groq(prompt: str, system_prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


async def use_random(prompt: str, system_prompt: str) -> str:
    api_key = os.getenv("LLM7IO_API_KEY")
    if not api_key:
        raise RuntimeError("LLM7IO_API_KEY is not configured")

    client = OpenAI(
        base_url="https://api.llm7.io/v1",
        api_key=api_key,
    )
    response = client.chat.completions.create(
        model="default",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def get_provider_order():
    return [
        ("gemini", use_gemini),
        ("cloudflare", use_cloudflare),
        ("qwen", use_qwen),
        ("groq", use_groq),
        ("random", use_random),
        ("mock", _mock_provider),
    ]


async def generate_ai_response(
    prompt: str,
    context: str,
    history: str,
    system_command: str,
):
    final_prompt = build_prompt(context, history, prompt)
    system_prompt = build_system_prompt(system_command)
    last_error = None

    for provider_name, provider_func in get_provider_order():
        try:
            response = await provider_func(final_prompt, system_prompt)
            if response and response.strip():
                return {"provider": provider_name, "response": response.strip()}
        except Exception as exc:  # pragma: no cover - provider/network failure handling
            last_error = exc
            print(f"{provider_name.title()} failed: {exc}")

    if last_error is not None:
        raise RuntimeError(f"All configured AI providers failed. Last error: {last_error}")

    return {
        "provider": "mock",
        "response": "Sorry, I couldn't get a response from the configured AI providers.",
    }
            