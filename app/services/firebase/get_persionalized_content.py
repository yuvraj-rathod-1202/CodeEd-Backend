from app.services.firebase.quiz import QuizService
from app.services.firebase.user import UserService
from app.services.firebase.flowchart import FlowchartService
from app.services.firebase.flashcard import FlashcardService
from app.services.firebase.config import get_firebase_db
from app.models.BaseModel.personalized.personal import (
    Personalized_Quiz_Content, 
    Personalized_User_Content, 
    Personalized_Flowchart_Content, 
    Personalized_Flashcard_Content,
    Personalized_Content
)


class PersonalizedContentService:
    def __init__(self, db):
        self.db = db
        self.quiz_service = QuizService(db)
        self.user_service = UserService(db)
        self.flowchart_service = FlowchartService(db)
        self.flashcard_service = FlashcardService(db)

    def get_personalized_quizzes(self, userId: str) -> Personalized_Quiz_Content:
        return self.quiz_service.get_last5_personalized_quizzes(userId)
    
    def get_personalized_user_info(self, userId: str) -> Personalized_User_Content:
        return self.user_service.get_personalized_user_content(userId)
    
    def get_personalized_flowcharts(self, userId: str) -> Personalized_Flowchart_Content:
        return self.flowchart_service.get_last5_flowcharts(userId)
    
    def get_personalized_flashcards(self, userId: str) -> Personalized_Flashcard_Content:
        return self.flashcard_service.get_last5_flashcards(userId)
    
    def get_personalized_content(self, userId: str) -> Personalized_Content:
        return Personalized_Content(
            personalized_info=self.get_personalized_user_info(userId),
            personalized_quiz=self.get_personalized_quizzes(userId),
            personalized_flowchart=self.get_personalized_flowcharts(userId),
            personalized_flashcard=self.get_personalized_flashcards(userId),
        )
    
    
def get_personalized_content(userId: str) -> Personalized_Content:
    try:
        db = get_firebase_db()
        service = PersonalizedContentService(db)
        return service.get_personalized_content(userId)
        
    except Exception as e:
        print(f"Error getting personalized content: {e}")
        return Personalized_Content(
            personalized_info=Personalized_User_Content(
                country="Unknown",
                goal="General Learning",
                experience="Beginner",
                interests=["General"],
                education="Not Specified"
            ),
            personalized_quiz=Personalized_Quiz_Content(quizzes=[]),
            personalized_flowchart=Personalized_Flowchart_Content(flowcharts=[]),
            personalized_flashcard=Personalized_Flashcard_Content(flashcards=[]),
        )
