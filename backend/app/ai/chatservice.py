import os
from dotenv import load_dotenv
from litellm import completion

from app.core.config import Setting

load_dotenv()


def ask_llm(prompt: str) -> str:
    """
    Send the prompt to the DeepSeek model using LiteLLM and return the response.
    Falls back to Groq API using LiteLLM if DeepSeek fails or lacks balance.
    """
    messages = [
        {"role": "system", "content": "You are a helpful real estate AI assistant."},
        {"role": "user", "content": prompt}
    ]

    deepseek_key = Setting.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        try:
            response = completion(
                model="deepseek/deepseek-chat",
                messages=messages,
                api_key=deepseek_key,
                temperature=0.7,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LiteLLM DeepSeek call failed: {e}")

    # Fallback to Groq API via LiteLLM if DeepSeek API fails or lacks balance
    groq_key = Setting.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            response = completion(
                model="groq/llama-3.3-70b-versatile",
                messages=messages,
                api_key=groq_key,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM Error (Groq Fallback): {e}"

    return "LLM Error: DeepSeek API request failed (Please check DEEPSEEK_API_KEY balance)."

