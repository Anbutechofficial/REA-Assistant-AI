import os
import requests
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.core.models import QuestionRequest
from app.core.config import Setting
from app.rag.retrieval import retrieve
from app.ai.prompt import build_prompt, check_query_safety
from app.ai.chatservice import ask_llm

router = APIRouter()


@router.post("/ask")
async def ask(request: QuestionRequest):

    # Step 0: Security & Intent Check (Block prompt injections & off-topic queries)
    is_safe, default_reply = check_query_safety(request.question)
    if is_safe == False:
        return {
            "question": request.question,
            "answer": default_reply
        }

    # Step 1: Retrieve Top 5 Properties via MongoDB Atlas Hybrid Search
    retrieved_docs = await retrieve(request.question)

    # Step 2: Build Prompt
    prompt = build_prompt(
        request.question,
        retrieved_docs
    )

    # Step 3: Get LLM Response
    try:
        answer = ask_llm(prompt)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


    # Step 4: Return Response
    return {
        "question": request.question,
        "answer": answer
    }



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
        "model": "whisper-large-v3",
        "response_format": "json",
        "language": "en",
        "prompt": "Transcribe spoken speech strictly in English or Tanglish (Tamil words written using English/Latin alphabet, e.g. '3 BHK flat in Egmore, budget 50 lakhs irukka'). Output ONLY in English or Tanglish using standard English letters."
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        return {"text": result.get("text", "")}
    except Exception as e:
        error_msg = str(e)
        if 'response' in locals() and hasattr(response, 'text'):
            error_msg += f" | {response.text}"
        raise HTTPException(status_code=500, detail=f"Transcription failed: {error_msg}")
