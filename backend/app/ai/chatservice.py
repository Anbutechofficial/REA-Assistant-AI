import os
import asyncio
from dotenv import load_dotenv
from litellm import completion

from app.core.config import Setting

load_dotenv()

SYSTEM_PROMPT = (
    "You are a helpful and expert Real Estate AI Assistant. "
    "When listing properties, format each property strictly as:\n\n"
    "Property 1\n"
    "Property Name: <Name>\n"
    "Price: <Price>\n"
    "Sqft: <Sqft>\n"
    "BHK: <BHK>\n\n"
    "Do NOT include conversational introductory phrases, markdown bullet points, or concluding questions. Output only clean, direct property blocks."
)


async def ask_llm(prompt: str) -> str:
    """
    Asynchronously call fast LLM providers (Groq 8B instant first for sub-200ms latency, followed by 70B/Gemini/DeepSeek).
    Runs completion in asyncio thread execution to keep FastAPI non-blocking.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    # 1. Primary: Groq LPU API (Ultra-fast 8B model: ~150-250ms response time at 800+ tokens/sec)
    groq_key = Setting.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            response = await asyncio.to_thread(
                completion,
                model="groq/llama-3.1-8b-instant",
                messages=messages,
                api_key=groq_key,
                temperature=0.3,
                timeout=5
            )
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
                if content:
                    return content
        except Exception as e:
            print(f"Groq 8B instant LLM call note ({e}), trying Groq 70B fallback...")

        # 1b. Secondary Groq model fallback: 70B Versatile
        try:
            response = await asyncio.to_thread(
                completion,
                model="groq/llama-3.3-70b-versatile",
                messages=messages,
                api_key=groq_key,
                temperature=0.3,
                timeout=6
            )
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
                if content:
                    return content
        except Exception as e:
            print(f"Groq 70B LLM call note ({e}), trying Gemini fallback...")

    # 2. Tertiary: Gemini 2.0 Flash API (~300ms latency)
    gemini_key = Setting.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            response = await asyncio.to_thread(
                completion,
                model="gemini/gemini-2.0-flash",
                messages=messages,
                api_key=gemini_key,
                timeout=6
            )
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
                if content:
                    return content
        except Exception as e:
            print(f"Gemini LLM call note ({e}).")

    # 3. Quaternary: DeepSeek API
    deepseek_key = Setting.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        try:
            response = await asyncio.to_thread(
                completion,
                model="deepseek/deepseek-chat",
                messages=messages,
                api_key=deepseek_key,
                temperature=0.7,
                timeout=6
            )
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                content = response.choices[0].message.content or ""
                if content:
                    return content
        except Exception as e:
            print(f"DeepSeek LLM call note ({e}).")

    return "LLM Error: Could not reach LLM provider. Please check API keys."


