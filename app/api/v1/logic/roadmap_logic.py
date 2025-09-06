import json
import os
import datetime
from google import genai
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from app.models.BaseModel.roadmap import RoadmapRequest, RoadmapResponse, RoadmapStep
from app.services.personalization.prompt_enhancer import enhance_prompt_with_personalization
from app.services.firebase.config import get_firebase_db
from app.services.firebase.roadmap import RoadmapService

load_dotenv()

# Configure Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class RoadmapGenerator:
    def __init__(self):
        self.max_steps = 12
        self.min_steps = 4

    def _create_roadmap_prompt(self, topic: str, skill_level: str, time_commitment: str, 
                              learning_style: str, specific_goals: Optional[str] = None, 
                              userId: Optional[str] = None) -> str:
        """
        Create a personalized prompt for learning roadmap generation.
        
        Args:
            topic (str): The topic to create a learning roadmap for
            skill_level (str): Beginner, Intermediate, Advanced
            time_commitment (str): light, moderate, intensive
            learning_style (str): visual, practical, theoretical, balanced
            specific_goals (Optional[str]): Specific learning goals
            userId (Optional[str]): Optional user ID for personalization
            
        Returns:
            str: The enhanced prompt for roadmap generation
        """
        
        # Time commitment mapping
        time_commitment_details = {
            "light": "1-2 hours per week, casual learning pace",
            "moderate": "3-5 hours per week, steady progress",
            "intensive": "8+ hours per week, accelerated learning"
        }
        
        # Learning style instructions
        style_instructions = {
            "visual": "Emphasize visual learning resources, diagrams, videos, and interactive content",
            "practical": "Focus on hands-on projects, coding exercises, and real-world applications",
            "theoretical": "Include comprehensive reading materials, academic resources, and conceptual understanding",
            "balanced": "Mix of visual, practical, and theoretical approaches for well-rounded learning"
        }
        
        time_detail = time_commitment_details.get(time_commitment, "moderate pace")
        style_instruction = style_instructions.get(learning_style, "balanced approach")
        goals_text = f"\nSpecific Goals: {specific_goals}" if specific_goals else ""
        
        base_prompt = f"""
Create a comprehensive learning roadmap for mastering "{topic}".

LEARNER PROFILE:
- Current Level: {skill_level}
- Time Commitment: {time_detail}
- Learning Style: {style_instruction}{goals_text}

ROADMAP REQUIREMENTS:
1. Create {self.min_steps}-{self.max_steps} progressive learning steps
2. Each step should build upon previous knowledge
3. Include realistic time estimates for each step
4. Provide specific milestones to track progress
5. Suggest relevant resources and learning materials
6. Include practical exercises or projects where applicable
7. Specify prerequisites for advanced steps

STEP STRUCTURE GUIDELINES:
- Title: Clear, actionable step name
- Description: Detailed explanation of what to learn and why
- Duration: Realistic time estimate based on commitment level
- Difficulty: Appropriate for the progression level
- Milestones: 2-4 specific, measurable achievements
- Resources: 2-5 recommended learning materials (books, courses, tutorials, tools)
- Prerequisites: What must be completed before this step

PERSONALIZATION NOTES:
- Adapt difficulty progression based on skill level
- Adjust time estimates for the specified commitment level
- Emphasize resources that match the preferred learning style
- Include industry-relevant skills and current best practices

Please respond in JSON format with:
{{
    "topic": "{topic}",
    "total_duration": "Estimated total time to complete the roadmap",
    "difficulty_level": "{skill_level}",
    "description": "Brief overview of what this roadmap will achieve",
    "steps": [
        {{
            "step_number": 1,
            "title": "Step title",
            "description": "Detailed description of what to learn",
            "duration": "Time estimate (e.g., '2 weeks', '1 month')",
            "difficulty_level": "Beginner/Intermediate/Advanced",
            "milestones": ["Milestone 1", "Milestone 2", "Milestone 3"],
            "resources": ["Resource 1", "Resource 2", "Resource 3"],
            "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
        }}
    ]
}}
"""

        # Enhance the prompt with personalization if userId is provided
        if userId:
            return enhance_prompt_with_personalization(base_prompt, userId)
        
        return base_prompt

    async def generate_roadmap(self, topic: str, skill_level: str = "Beginner", 
                              time_commitment: str = "moderate", learning_style: str = "balanced",
                              specific_goals: Optional[str] = None, userId: Optional[str] = None) -> RoadmapResponse:
        """
        Generate a comprehensive learning roadmap using Gemini AI.
        
        Args:
            topic (str): The topic to create a learning roadmap for
            skill_level (str): Beginner, Intermediate, Advanced
            time_commitment (str): light, moderate, intensive
            learning_style (str): visual, practical, theoretical, balanced
            specific_goals (Optional[str]): Specific learning goals
            userId (Optional[str]): Optional user ID for personalization
            
        Returns:
            RoadmapResponse: The generated learning roadmap
        """
        try:
            # Create the personalized prompt
            prompt = self._create_roadmap_prompt(topic, skill_level, time_commitment, 
                                               learning_style, specific_goals, userId)

            # Generate content using Gemini
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt, 
                config={"response_mime_type": "application/json"}
            )

            if response.text is None:
                raise ValueError("No text received from Gemini AI")

            # Parse the response
            data = json.loads(response.text)
            
            # Extract and validate roadmap data
            topic_title = data.get("topic", topic)
            total_duration = data.get("total_duration", "Variable")
            difficulty_level = data.get("difficulty_level", skill_level)
            description = data.get("description", f"A comprehensive learning roadmap for {topic}")
            steps_data = data.get("steps", [])
            
            # Validate and create step objects
            steps_list = []
            for step_data in steps_data:
                if isinstance(step_data, dict) and all(key in step_data for key in ["step_number", "title", "description"]):
                    step_obj = RoadmapStep(
                        step_number=step_data.get("step_number", len(steps_list) + 1),
                        title=step_data.get("title", "Learning Step"),
                        description=step_data.get("description", "Step description"),
                        duration=step_data.get("duration", "2 weeks"),
                        difficulty_level=step_data.get("difficulty_level", "Beginner"),
                        milestones=step_data.get("milestones", ["Complete step objectives"]),
                        resources=step_data.get("resources", ["Online tutorials", "Practice exercises"]),
                        prerequisites=step_data.get("prerequisites", [])
                    )
                    steps_list.append(step_obj)
            
            # Ensure we have at least minimum steps
            if not steps_list:
                steps_list = [
                    RoadmapStep(
                        step_number=1,
                        title="Getting Started with " + topic,
                        description=f"Introduction to {topic} fundamentals and basic concepts",
                        duration="2 weeks",
                        difficulty_level="Beginner",
                        milestones=["Understand basic concepts", "Complete introductory exercises"],
                        resources=["Online documentation", "Tutorial videos", "Practice platform"],
                        prerequisites=[]
                    )
                ]
            
            # Limit to maximum number of steps
            if len(steps_list) > self.max_steps:
                steps_list = steps_list[:self.max_steps]
            
            result = RoadmapResponse(
                topic=topic_title,
                total_duration=total_duration,
                difficulty_level=difficulty_level,
                description=description,
                steps=steps_list
            )
            
            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return RoadmapResponse(
                topic=topic,
                total_duration="Variable",
                difficulty_level=skill_level,
                description=f"A learning roadmap for {topic} (generated with fallback due to parsing error)",
                steps=[
                    RoadmapStep(
                        step_number=1,
                        title="Start Learning " + topic,
                        description="Begin your learning journey with basic concepts and fundamentals",
                        duration="2-4 weeks",
                        difficulty_level="Beginner",
                        milestones=["Understand core concepts", "Complete basic exercises"],
                        resources=["Online tutorials", "Documentation", "Practice exercises"],
                        prerequisites=[]
                    )
                ]
            )
        except Exception as e:
            print(f"❌ Roadmap generation error: {e}")
            return RoadmapResponse(
                topic=topic,
                total_duration="Variable",
                difficulty_level=skill_level,
                description=f"A learning roadmap for {topic} (generated with fallback due to error)",
                steps=[
                    RoadmapStep(
                        step_number=1,
                        title="Error Recovery - " + topic,
                        description=f"An error occurred during roadmap generation: {str(e)}. This is a basic starting point.",
                        duration="Variable",
                        difficulty_level=skill_level,
                        milestones=["Review topic requirements", "Seek additional resources"],
                        resources=["Search for tutorials", "Consult documentation", "Join communities"],
                        prerequisites=[]
                    )
                ]
            )

# Global instance
roadmap_generator = RoadmapGenerator()

async def create_roadmap_logic(topic: str, skill_level: str = "Beginner", 
                              time_commitment: str = "moderate", learning_style: str = "balanced",
                              specific_goals: Optional[str] = None, userId: Optional[str] = None) -> RoadmapResponse:
    """
    Main function to create a learning roadmap for any topic.
    
    Args:
        topic (str): The topic to create a learning roadmap for
        skill_level (str): Beginner, Intermediate, Advanced
        time_commitment (str): light, moderate, intensive
        learning_style (str): visual, practical, theoretical, balanced
        specific_goals (Optional[str]): Specific learning goals
        userId (Optional[str]): Optional user ID for personalization
        
    Returns:
        RoadmapResponse: Generated learning roadmap
    """
    return await roadmap_generator.generate_roadmap(topic, skill_level, time_commitment, 
                                                   learning_style, specific_goals, userId)