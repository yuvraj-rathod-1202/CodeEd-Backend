import json
import os
import datetime
from google import genai
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from app.models.BaseModel.flashcard import flashcard_request, flashcard_response, flashcard
from app.services.personalization.prompt_enhancer import enhance_prompt_with_personalization
from app.services.firebase.config import get_firebase_db
from app.services.firebase.flashcard import FlashcardService

load_dotenv()

# Configure Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class FlashcardGenerator:
    def __init__(self):
        self.max_flashcards = 20
        self.min_flashcards = 5

    def _create_flashcard_prompt(self, text: str, instruction: Optional[str] = None, userId: Optional[str] = None, language: Optional[str] = "English") -> str:
        """
        Create a personalized prompt for flashcard generation.
        
        Args:
            text (str): The input text to create flashcards from
            instruction (Optional[str]): Optional instruction for flashcard generation
            userId (Optional[str]): Optional user ID for personalization
            
        Returns:
            str: The enhanced prompt for flashcard generation
        """
        # Build the base prompt
        base_instruction = instruction if instruction else "Create flashcards that help with memorization and understanding of key concepts."
        
        base_prompt = f"""
Generate educational flashcards from the following text. Create between {self.min_flashcards} and {self.max_flashcards} flashcards that cover the most important concepts, facts, and key points.

INSTRUCTION: {base_instruction}

Each flashcard should follow these guidelines:
- Question (front): Should be clear, concise, and test understanding
- Answer (back): Should be comprehensive but not too lengthy
- Focus on key concepts, definitions, important facts, and relationships
- Vary question types: definitions, explanations, examples, comparisons, applications
- Make questions engaging and thought-provoking
- Ensure answers are accurate and complete

IMPORTANT RULES:
- Create flashcards that promote active recall and spaced repetition
- Questions should be specific enough to have clear answers
- Avoid overly simple yes/no questions unless they test important concepts
- Include context when necessary for clarity
- Make sure each flashcard is self-contained and understandable

Flashcard Language: {language} (the main language should be {language}, but some English words are also acceptable)

Text to create flashcards from:
{text}

Please respond in JSON format with:
{{
    "title": "A descriptive title for this set of flashcards",
    "flashcards": [
        {{
            "quetion": "The question for the flashcard front",
            "answer": "The comprehensive answer for the flashcard back"
        }}
    ]
}}
"""

        # Enhance the prompt with personalization if userId is provided
        if userId:
            return enhance_prompt_with_personalization(base_prompt, userId)
        
        return base_prompt

    async def generate_flashcards(self, text: str, instruction: Optional[str] = None, userId: Optional[str] = None, language: Optional[str] = "English") -> flashcard_response:
        """
        Generate flashcards based on the provided text using Gemini AI.
        
        Args:
            text (str): The input text to create flashcards from
            instruction (Optional[str]): Optional instruction for flashcard generation
            userId (Optional[str]): Optional user ID for personalization
            
        Returns:
            flashcard_response: The generated flashcards with title
        """
        try:
            # Create the personalized prompt
            prompt = self._create_flashcard_prompt(text, instruction, userId, language)

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
            
            # Extract title and flashcards
            title = data.get("title", "Study Flashcards")
            flashcards_data = data.get("flashcards", [])
            
            # Validate and create flashcard objects
            flashcards_list = []
            for card_data in flashcards_data:
                if isinstance(card_data, dict) and "quetion" in card_data and "answer" in card_data:
                    flashcard_obj = flashcard(
                        quetion=card_data["quetion"],
                        answer=card_data["answer"]
                    )
                    flashcards_list.append(flashcard_obj)
            
            # Ensure we have at least one flashcard
            if not flashcards_list:
                flashcards_list = [
                    flashcard(
                        quetion="What are the main topics covered in the provided text?",
                        answer="The text contains information that can be studied through these flashcards for better understanding and retention."
                    )
                ]
            
            # Limit to maximum number of flashcards
            if len(flashcards_list) > self.max_flashcards:
                flashcards_list = flashcards_list[:self.max_flashcards]
            
            result = flashcard_response(
                flashcards=flashcards_list,
                title=title
            )
            
            
            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return flashcard_response(
                flashcards=[
                    flashcard(
                        quetion="What is the main content of the study material?",
                        answer="This flashcard was created as a fallback. Please review the original text for detailed information."
                    )
                ],
                title="Study Flashcards"
            )
        except Exception as e:
            print(f"❌ Flashcard generation error: {e}")
            return flashcard_response(
                flashcards=[
                    flashcard(
                        quetion="Study Question",
                        answer=f"An error occurred during flashcard generation: {str(e)}. Please try again with different content."
                    )
                ],
                title="Error - Study Flashcards"
            )

# Global instance
flashcard_generator = FlashcardGenerator()

async def create_flashcard_logic(text: str, instruction: Optional[str] = None, userId: Optional[str] = None, language: Optional[str] = "English") -> flashcard_response:
    """
    Main function to create flashcard logic based on input text.
    
    Args:
        text (str): The input text to analyze and create flashcards from
        instruction (Optional[str]): Optional instruction for flashcard generation
        userId (Optional[str]): Optional user ID for personalization
        
    Returns:
        flashcard_response: Generated flashcards with title
    """
    return await flashcard_generator.generate_flashcards(text, instruction, userId, language)