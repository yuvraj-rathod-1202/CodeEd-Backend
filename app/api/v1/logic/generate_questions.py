from app.models.BaseModel.generateQuestionsBaseModel import generateQuestionRequest, generateQuestionResponse
from app.services.YouTube.getYouTubeId import GetYoutubeURL
from app.services.YouTube.getYouTubeTranscript import GetYouTubeTranscript
from app.services.Questions.get_questions import GetQuestionsModel
from app.models.GEMINI.Questions import Question as Qu
from app.services.mongo.save.crud import save_response
from app.models.BaseModel.mongo.Schema import Response
import datetime
from bson import ObjectId
from typing import Optional

async def generate_question_logic(request: generateQuestionRequest) -> generateQuestionResponse:
    transcript = request.text
    numbers = request.numbers
    difficulty = request.difficulty
    quiz_type = request.quiz_type
    language = request.language
    userId = request.userId
    questions, title = GetQuestionsModel().execute_model(text=transcript, number=numbers, difficulty=difficulty, quiz_type=quiz_type, userId=userId, language=language)
    if not questions:
        return generateQuestionResponse(title="no Title", questions=[Qu(id=1, type="mix", difficulty="Easy", question="No questions generated", correct="The transcript may not contain enough information to generate questions.", explanation="Please provide a more detailed transcript or adjust the parameters.")])
    # Convert questions to a list of dictionaries
    # if user_id:
    #     await save_response(
    #         Response(
    #             userId=user_id,
    #             url_id=id,
    #             createdAt=datetime.datetime.now(),
    #             updatedAt=datetime.datetime.now(),
    #             questions=questions,
    #             quiz_type=quiz_type,
    #             difficulty=difficulty,
    #             numbers=numbers,
    #             score=[],
    #         )
    #     )
    
    return generateQuestionResponse(questions=questions, title=title)