import datetime
from app.models.BaseModel.personalized.personal import Personalized_Roadmap, Personalized_Roadmap_Content
from typing import List

def extract_personalized_roadmap(roadmap_data) -> Personalized_Roadmap:
    """Extract personalized roadmap data from Firebase document"""
    return Personalized_Roadmap(
        topic=roadmap_data.get('topic', ''),
        skill_level=roadmap_data.get('skill_level', 'Beginner'),
        total_steps=len(roadmap_data.get('steps', [])),
        completion_rate=roadmap_data.get('completion_rate', 0.0),
        time_spent=roadmap_data.get('time_spent', '0 hours'),
        feedback=roadmap_data.get('feedback', '')
    )

class RoadmapService:
    def __init__(self, db):
        self.db = db

    def get_last5_roadmaps(self, userId: str) -> Personalized_Roadmap_Content:
        """Get the last 5 roadmaps for a user for personalization"""
        try:
            roadmap_docs = self.db.collection('users').document(userId).collection('roadmaps').get()
            if not roadmap_docs:
                return Personalized_Roadmap_Content(roadmaps=[])

            roadmaps_data = [roadmap_doc.to_dict() for roadmap_doc in roadmap_docs]
            # Sort roadmaps by createdAt in descending order and get the last 5
            sorted_roadmaps = sorted(roadmaps_data, key=lambda x: x.get('createdAt', 0), reverse=True)[:5]
            
            roadmaps = []
            for roadmap_data in sorted_roadmaps:
                roadmaps.append(extract_personalized_roadmap(roadmap_data))
            
            return Personalized_Roadmap_Content(roadmaps=roadmaps)
            
        except Exception as e:
            print(f"Error fetching roadmaps for user {userId}: {e}")
            return Personalized_Roadmap_Content(roadmaps=[])

    def save_roadmap(self, userId: str, roadmap_data: dict) -> bool:
        """Save a roadmap to Firebase"""
        try:
            self.db.collection('users').document(userId).collection('roadmaps').add(roadmap_data)
            return True
        except Exception as e:
            print(f"Error saving roadmap for user {userId}: {e}")
            return False

    def update_roadmap_progress(self, userId: str, roadmap_id: str, completion_rate: float, time_spent: str) -> bool:
        """Update roadmap progress"""
        try:
            self.db.collection('users').document(userId).collection('roadmaps').document(roadmap_id).update({
                'completion_rate': completion_rate,
                'time_spent': time_spent,
                'updatedAt': datetime.datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error updating roadmap progress for user {userId}: {e}")
            return False
