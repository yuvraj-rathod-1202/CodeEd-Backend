from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union, Dict

class Question(BaseModel):
    id: int
    question: str
    type: str
    difficulty: str
    explanation: str
    options: Optional[List[str]] = None
    correct: Union[int, bool, str, None]
    
class Submission(BaseModel):
    attempt_number: int
    time_taken: int
    submittedAt: datetime
    answers: Dict[int, Union[str, int, bool]]
    score: int

class Quiz(BaseModel):
    id: Optional[str] = None
    title: str
    difficulty: str
    generatedAt: datetime
    number: int
    quiz_type: str
    time_limit: int
    total_submissions: int
    updatedAt: datetime
    list_score: List[int]
    questions: List[Question]
    submissions: List[Submission] = []

class Node(BaseModel):
    label: str
    children: Optional[List[int]] = None

class FlowChart(BaseModel):
    id: Optional[str]
    title: str
    generatedAt: datetime
    nodes: List[Node]
    
class User(BaseModel):
    id: str
    email: str
    username: str
    joined: datetime
    quizes: Optional[List[Quiz]] = None
    flowcharts: Optional[List[FlowChart]] = None