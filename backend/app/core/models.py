from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class QuestionRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str, Any]]] = []

