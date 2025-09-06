from pydantic import BaseModel
from typing import List, Optional, Union

class Question(BaseModel):
    id: int
    question: str
    type: str
    difficulty: str
    explanation: str
    options: Optional[List[str]] = None
    correct: Union[int, bool, str, None]

class scrapedWebPageResponse(BaseModel):
    text: str

class scrapedWebPageRequest(BaseModel):
    url: str
    
class YouTubeTranscriptResponse(BaseModel):
    text: str
    
class YouTubeTranscriptRequest(BaseModel):
    video_url: str
    
class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TranslationResponse(BaseModel):
    translated_text: str