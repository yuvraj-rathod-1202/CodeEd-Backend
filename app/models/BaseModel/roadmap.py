from pydantic import BaseModel
from typing import List, Optional

class RoadmapStep(BaseModel):
    step_number: int
    title: str
    description: str
    duration: str  # e.g., "2 weeks", "1 month"
    difficulty_level: str  # Beginner, Intermediate, Advanced
    milestones: List[str]
    resources: List[str]
    prerequisites: List[str] = []

class RoadmapResponse(BaseModel):
    topic: str
    total_duration: str
    difficulty_level: str
    description: str
    steps: List[RoadmapStep]
    
class RoadmapRequest(BaseModel):
    topic: str  # The topic to create a learning roadmap for
    skill_level: Optional[str] = "Beginner"  # Beginner, Intermediate, Advanced
    time_commitment: Optional[str] = "moderate"  # light, moderate, intensive
    learning_style: Optional[str] = "balanced"  # visual, practical, theoretical, balanced
    specific_goals: Optional[str] = None  # Optional specific learning goals
    userId: Optional[str] = None  # Optional user ID for personalization
