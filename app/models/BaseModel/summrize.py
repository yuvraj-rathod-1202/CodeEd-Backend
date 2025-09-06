from pydantic import BaseModel
from typing import Optional, Union, List

class summarize_textResponse(BaseModel):
    success: bool
    summary: Optional[Union[str, List[str]]] = None  # String for paragraph, List for bullet points
    title: Optional[str] = None
    error: Optional[str] = None
    format: str
    chunks_processed: int
    original_length: int
    summary_length: int
    estimated_tokens: Optional[int] = None
    compression_ratio: Optional[float] = None
    

class summarize_textRequest(BaseModel):
    text: str
    format: str = "paragraph"  # "paragraph" or "bullet_points"
    length: str = "medium"  # "small", "medium", or "large"
    userId: Optional[str] = None  # For personalization
    userId: Optional[str] = None  # For personalization