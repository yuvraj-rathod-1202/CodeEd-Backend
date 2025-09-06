from pydantic import BaseModel
from app.models.BaseModel.mongo.Schema import PyObjectId
from app.models.BaseModel.common import Question
from typing import Optional

class generateQuestionRequest(BaseModel):
    text: str
    numbers: int
    difficulty: str
    quiz_type: str
    userId: Optional[str]


class generateQuestionResponse(BaseModel):
    questions: list[Question]
    title: str | None = None
