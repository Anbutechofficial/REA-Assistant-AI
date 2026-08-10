import os
import requests
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.core.models import QuestionRequest
from app.core.config import Setting
from app.rag.retrieval import retrieve
from app.ai.prompt import build_prompt, check_query_safety
from app.ai.chatservice import ask_llm

router = APIRouter()

_ask_response_cache: dict[str, dict] = {}
MAX_RESPONSE_CACHE_SIZE = 300


import re

def sanitize_answer(answer: str) -> str:
    if not answer:
        return answer
    
    # Remove any stray [METADATA] header lines if leaked
    cleaned = re.sub(r'\[METADATA\][^\n]*\n?', '', answer, flags=re.IGNORECASE)
    
    # Strip introductory matching count lines and top matching properties header lines
    cleaned = re.sub(r'(?:We found|There are)\s+\d+\s+matching properties[^\n]*\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'Here are the top \d+ matching properties:?\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'(?:Total matching properties|Matching properties count)(?: found)?:?\s*\d*\.?\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'(?:Matching_Count|matching_count):\s*\d+\.?\n?', '', cleaned, flags=re.IGNORECASE)
    
    # Transform raw snake_case technical values into elegant human phrasing if any remain
    cleaned = re.sub(r'(?:Average_Property_Price|average_price):\s*(?:Rs\s*)?([\d\.]+)\s*(?:Lakhs)?', r'The average property price is Rs \1 Lakhs.', cleaned, flags=re.IGNORECASE)
    
    # Clean up residual snake_case keys if any remain
    cleaned = cleaned.replace("Average_Property_Price:", "Average Property Price:")
    cleaned = cleaned.replace("Matching_Count:", "")
    cleaned = cleaned.replace("Exact_Match_Found:", "")
    cleaned = cleaned.replace("exact_match_found:", "")
    cleaned = cleaned.replace("total_database_listings:", "")

    return cleaned.strip()


@router.post("/ask")
async def ask(request: QuestionRequest):
    cache_key = request.question.strip().lower()
    if cache_key in _ask_response_cache:
        return _ask_response_cache[cache_key]

    # Step 0: Security & Intent Check (Block prompt injections & off-topic queries)
    is_safe, default_reply = check_query_safety(request.question)
    if is_safe == False:
        res = {
            "question": request.question,
            "answer": default_reply
        }
        return res

    # Step 1: Retrieve Top 5 Properties via MongoDB Atlas Hybrid Search / Smart RAM Filter
    retrieved_docs = await retrieve(request.question, history=request.history)

    # Step 2: Build Prompt
    prompt = build_prompt(
        request.question,
        retrieved_docs
    )

    # Step 3: Get LLM Response asynchronously
    try:
        raw_answer = await ask_llm(prompt)
        answer = sanitize_answer(raw_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = {
        "question": request.question,
        "answer": answer
    }

    if len(_ask_response_cache) > MAX_RESPONSE_CACHE_SIZE:
        _ask_response_cache.clear()
    _ask_response_cache[cache_key] = result

    # Step 4: Return Response
    return result



# -------------------------
# Transcribe Route
# -------------------------
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_data = await file.read()

    groq_api_key = Setting.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}"
    }

    files = {
        "file": (file.filename or "audio.webm", audio_data, file.content_type or "audio/webm")
    }
    data = {
        "model": "whisper-large-v3-turbo",
        "response_format": "json",
        "language": "en",
        "prompt": "Transcribe spoken speech strictly in English or Tanglish (Tamil words written using English/Latin alphabet, e.g. '3 BHK flat in Egmore, budget 50 lakhs irukka'). Output ONLY in English or Tanglish using standard English letters."
    }

    try:
        def _call_transcribe():
            return requests.post(url, headers=headers, files=files, data=data, timeout=20)

        response = await asyncio.to_thread(_call_transcribe)
        response.raise_for_status()
        result = response.json()
        return {"text": result.get("text", "")}
    except Exception as e:
        error_msg = str(e)
        if 'response' in locals() and hasattr(response, 'text'):
            error_msg += f" | {response.text}"
        raise HTTPException(status_code=500, detail=f"Transcription failed: {error_msg}")
