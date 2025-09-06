from pydantic import BaseModel
from typing import List

class Personalized_Quiz(BaseModel):
    scores: List[int]
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    time_taken: List[int]  # in seconds
    feedback: str
    difficulty: str
    title: str
    quiz_type: str
    total_submissions: int
    average_score: float
    
class Personalized_Quiz_Content(BaseModel):
    quizzes: List[Personalized_Quiz]

class Personalized_Flowchart(BaseModel):
    title: str
    feedback: str
    node_count: int

class Personalized_Flowchart_Content(BaseModel):
    flowcharts: List[Personalized_Flowchart]

class Personalized_Summary(BaseModel):
    original_length: int
    summary_length: int
    feedback: str
    format: str

class Personalized_Summary_Content(BaseModel):
    summaries: List[Personalized_Summary]

class Personalized_Flashcard(BaseModel):
    title: str
    feedback: str
    flashcard_count: int

class Personalized_Flashcard_Content(BaseModel):
    flashcards: List[Personalized_Flashcard]

class Personalized_Roadmap(BaseModel):
    topic: str
    skill_level: str
    total_steps: int
    completion_rate: float  # 0.0 to 1.0
    time_spent: str
    feedback: str

class Personalized_Roadmap_Content(BaseModel):
    roadmaps: List[Personalized_Roadmap]

class Personalized_User_Content(BaseModel):
    country: str
    goal: str
    experience: str
    interests: List[str]
    education: str
    
    
class Personalized_Content(BaseModel):
    personalized_info: Personalized_User_Content
    personalized_quiz: Personalized_Quiz_Content
    personalized_flowchart: Personalized_Flowchart_Content
    personalized_flashcard: Personalized_Flashcard_Content
    # personalized_summary: Personalized_Summary_Content