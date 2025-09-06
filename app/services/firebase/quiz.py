from app.models.BaseModel.personalized.personal import Feedback, Personalized_Quiz, Personalized_Quiz_Content
from app.models.BaseModel.personalized.firebase import Submission
from typing import List

def extract_personalized_quiz(quiz_data) -> Personalized_Quiz:
    correct_answer = 0
    incorrect_answer = 0
    for submission in quiz_data.get('submissions', []):
        for answer in getattr(submission, 'answers', {}).values():
            if answer == quiz_data.get('questions', [])[0].get('correct'):
                correct_answer += 1
            else:
                incorrect_answer += 1

    return Personalized_Quiz(
        scores=quiz_data.get('list_score', []),
        total_questions=quiz_data.get('number', 0),
        correct_answers=correct_answer,
        incorrect_answers=incorrect_answer,
        time_taken=[getattr(sub, 'time_taken', 0) for sub in quiz_data.get('submissions', [])] if quiz_data.get('submissions') else [],
        feedback=Feedback(
            experience=quiz_data.get('feedback', {}).get('experience', ''),
            improvements=quiz_data.get('feedback', {}).get('improvements', []),
            rating=quiz_data.get('feedback', {}).get('rating', 0)
        ),
        difficulty=quiz_data.get('difficulty', ''),
        title=quiz_data.get('title', ''),
        quiz_type=quiz_data.get('quiz_type', ''),
        total_submissions=quiz_data.get('total_submissions', 0),
        average_score=(sum(quiz_data.get('list_score', [])) / len(quiz_data.get('list_score', []))) if quiz_data.get('list_score') else 0.0
    )

class QuizService:
    def __init__(self, db):
        self.db = db

    def get_submissions_by_Id(self, userId: str, quizId: str, submissionId: str) -> Submission | None:
        submission_doc = self.db.collection('users').document(userId).collection('quizes').document(quizId).collection('submissions').document(submissionId).get()
        if submission_doc.exists:
            data = submission_doc.to_dict()
            return Submission(**data)

    def get_last5_personalized_quizzes(self, userId: str) -> Personalized_Quiz_Content:
        quiz_docs = self.db.collection('users').document(userId).collection('quizes').get()
        if not quiz_docs:
            return Personalized_Quiz_Content(quizzes=[])

        quizes = [{**quiz_doc.to_dict(), "id": quiz_doc.id} for quiz_doc in quiz_docs]
        # Sort quizzes by generatedAt in descending order and get the last 5
        sorted_quizzes = sorted(quizes, key=lambda x: x['generatedAt'], reverse=True)[:5]
        quizzes = []
        for quiz in sorted_quizzes:
            quiz['submissions'] = [sub_data for sub in quiz.get('submissions', []) if (sub_data := self.get_submissions_by_Id(userId, quiz['id'], sub)) is not None]
            quizzes.append(extract_personalized_quiz(quiz))
        return Personalized_Quiz_Content(quizzes=quizzes)