from app.models.BaseModel.personalized.firebase import User
from app.models.BaseModel.personalized.personal import Personalized_User_Content

def extract_personalized_user(user_data) -> Personalized_User_Content:
    return Personalized_User_Content(
        country=user_data.get('country', ''),
        goal=user_data.get('goal', ''),
        experience=user_data.get('experience', ''),
        interests=user_data.get('interests', []),
        education=user_data.get('education', ''),
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
            country='',
            goal='',
            experience='',
            interests=[],
            education=''
        )