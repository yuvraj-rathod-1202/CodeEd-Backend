from app.models.BaseModel.personalized.firebase import User
from app.models.BaseModel.personalized.personal import Personalized_User_Content

def extract_personalized_user(user_data) -> Personalized_User_Content:
    return Personalized_User_Content(
        country=getattr(user_data, "country", "Unknown"),
        primaryGoal=getattr(user_data, "primaryGoal", "General Learning"),
        studyTime=getattr(user_data, "studyTime", "1-2 hours per week"),
        subjectsOfInterest=getattr(user_data, "subjectsOfInterest", ["General"]),
        educationLevel=getattr(user_data, "educationLevel", "Not Specified"),
    )

class UserService:
    def __init__(self, db):
        self.db = db

    def get_user_by_id(self, userId: str):
        user_doc = self.db.collection('users').document(userId).get()
        if user_doc.exists:
            return User(**user_doc.to_dict())
        
    def get_personalized_user_content(self, userId: str) -> Personalized_User_Content:
        user = self.get_user_by_id(userId)
        if user:
            return extract_personalized_user(user)
        return Personalized_User_Content(
            country="Unknown",
            primaryGoal="General Learning",
            studyTime="1-2 hours per week",
            subjectsOfInterest=["General"],
            educationLevel="Not Specified"
        )