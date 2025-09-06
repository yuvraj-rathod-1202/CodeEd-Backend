from pydantic import BaseModel
from typing import List, Optional

class flashcard(BaseModel):
    quetion: str
    answer: str

class flashcard_response(BaseModel):
    flashcards: List[flashcard]
    title: str
    
class flashcard_request(BaseModel):
    text: str
    instruction: Optional[str] = None  # Optional instruction for flashcard generation
    language: Optional[str] = "English"
    userId: Optional[str] = None  # Optional user ID for personalization