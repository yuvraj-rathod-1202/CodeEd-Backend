from app.models.BaseModel.personalized.personal import Personalized_Flashcard, Personalized_Flashcard_Content
from typing import List

def extract_personalized_flashcard(flashcard_data) -> Personalized_Flashcard:
    """Extract personalized flashcard data from Firebase document"""
    return Personalized_Flashcard(
        title=flashcard_data.get('title', ''),
        feedback=flashcard_data.get('feedback', ''),
        flashcard_count=len(flashcard_data.get('flashcards', []))
    )

class FlashcardService:
    def __init__(self, db):
        self.db = db

    def get_last5_flashcards(self, userId: str) -> Personalized_Flashcard_Content:
        """Get the last 5 flashcard sets for a user for personalization"""
        try:
            flashcard_docs = self.db.collection('users').document(userId).collection('flashcards').get()
            if not flashcard_docs:
                return Personalized_Flashcard_Content(flashcards=[])

            flashcards_data = [flashcard_doc.to_dict() for flashcard_doc in flashcard_docs]
            # Sort flashcards by generatedAt in descending order and get the last 5
            sorted_flashcards = sorted(flashcards_data, key=lambda x: x.get('generatedAt', 0), reverse=True)[:5]
            
            flashcards = []
            for flashcard_data in sorted_flashcards:
                flashcards.append(extract_personalized_flashcard(flashcard_data))
            
            return Personalized_Flashcard_Content(flashcards=flashcards)
            
        except Exception as e:
            print(f"Error fetching flashcards for user {userId}: {e}")
            return Personalized_Flashcard_Content(flashcards=[])

    def save_flashcard_set(self, userId: str, flashcard_data: dict) -> bool:
        """Save a flashcard set to Firebase"""
        try:
            self.db.collection('users').document(userId).collection('flashcards').add(flashcard_data)
            return True
        except Exception as e:
            print(f"Error saving flashcard set for user {userId}: {e}")
            return False
