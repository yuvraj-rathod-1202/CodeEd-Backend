from pydantic import BaseModel
from typing import List

class Personalized_Quiz(BaseModel):
    scores: List[int]
    total_questions: List[int]
    correct_answers: int
    incorrect_answers: int
    time_taken: int  # in seconds
    feedback: str
    difficulty: str
    title: str
    quiz_type: str
    total_submissions: int
    average_score: float
    
class Personalized_Quiz_Content(BaseModel):
    quizes: List[Personalized_Quiz]
    summary_titles: List[str]
    flowchart_titles: List[str]

class Personalized_Flowchart(BaseModel):
    title: str
    feedback: str
    node_count: int

class Personalized_Flowchart_Content(BaseModel):
    flowcharts: List[Personalized_Flowchart]
    quiz_titles: List[str]
    summary_titles: List[str]

class Personalized_Summary(BaseModel):
    original_length: int
    summary_length: int
    feedback: str
    format: str

class Personalized_Summary_Content(BaseModel):
    summaries: List[Personalized_Summary]
    quiz_titles: List[str]
    flowchart_titles: List[str]

class Personalized_User_Content(BaseModel):
    country: str
    goal: str
    experience: str
    interests: List[str]
    education: str
    personalized_quiz: Personalized_Quiz_Content
    personalized_flowchart: Personalized_Flowchart_Content
    personalized_summary: Personalized_Summary_Content