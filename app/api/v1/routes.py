from fastapi import APIRouter, UploadFile, File
from app.models.BaseModel.generateQuestionsBaseModel import generateQuestionRequest, generateQuestionResponse
from app.models.BaseModel.summrize import summarize_textRequest, summarize_textResponse
from app.models.BaseModel.flowchart import flowchart_request, flowchart_response
from app.api.v1.logic.summarize_logic import summarize_text_logic
from app.api.v1.logic.flowchart_logic import create_flowchart_logic
from app.models.BaseModel.mongo.Schema import UserResponse, User
from app.api.v1.logic.generate_questions import generate_question_logic
from app.api.v1.logic.extract_text_from_pdf import extract_text_from_pdf_logic

router = APIRouter()

@router.post('/generateQuestions', response_model=generateQuestionResponse)
async def generateQuestion(request: generateQuestionRequest):
    return await generate_question_logic(request)

# async def save_user_data_logic(request: User) -> UserResponse:
#     # Logic to save user data goes here
#     # This is a placeholder implementation
#     return UserResponse(user_id=request.user_id, message="User data saved successfully")

@router.post('/extract-text')
async def extract_text_from_pdf(pdf_file: UploadFile = File(...)):
    print(f"Received file: {pdf_file.filename}")
    return await extract_text_from_pdf_logic(pdf_file)

@router.post('/summarize', response_model=summarize_textResponse)
async def summarize_text(request: summarize_textRequest):
    result = await summarize_text_logic(request)
    
    # Return the result directly since it already matches SummarizeResponse structure
    return result

@router.post('/flowchart', response_model=flowchart_response)
async def create_flowchart(request: flowchart_request):
    return await create_flowchart_logic(request.text, request.instruction)

# @router.post('/saveUserData', response_model=UserResponse)
# async def saveUserData(request: User):
#     return await save_user_data_logic(request)