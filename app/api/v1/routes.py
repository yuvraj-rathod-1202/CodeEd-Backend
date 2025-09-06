from fastapi import APIRouter, UploadFile, File
from app.models.BaseModel.generateQuestionsBaseModel import generateQuestionRequest, generateQuestionResponse
from app.models.BaseModel.summrize import summarize_textRequest, summarize_textResponse
from app.models.BaseModel.flowchart import flowchart_request, flowchart_response
from app.models.BaseModel.flashcard import flashcard_request, flashcard_response
from app.api.v1.logic.summarize_logic import summarize_text_logic
from app.api.v1.logic.flowchart_logic import create_flowchart_logic
from app.api.v1.logic.flashcard_logic import create_flashcard_logic
from app.models.BaseModel.mongo.Schema import UserResponse, User
from app.api.v1.logic.generate_questions import generate_question_logic
from app.api.v1.logic.extract_text_from_pdf import extract_text_from_pdf_logic
from app.api.v1.logic.scrape_web_page import scrape_web_page_logic
from app.models.BaseModel.common import scrapedWebPageResponse, scrapedWebPageRequest, YouTubeTranscriptRequest, YouTubeTranscriptResponse, TranslationRequest, TranslationResponse
from app.api.v1.logic.extract_text_from_youtube import extract_text_from_youtube_logic
from app.services.text.change_language import change_language
from app.api.v1.logic.flashcard_logic import create_flashcard_logic

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

@router.post('/get-youtube-transcript', response_model=YouTubeTranscriptResponse)
async def get_youtube_transcript(request: YouTubeTranscriptRequest):
    text = await extract_text_from_youtube_logic(request.video_url)
    return YouTubeTranscriptResponse(text=text["text"])

@router.post('/get-webpage-text', response_model=scrapedWebPageResponse)
async def get_webpage_text(request: scrapedWebPageRequest):
    url = request.url
    text = await scrape_web_page_logic(url)
    return scrapedWebPageResponse(text=text)

@router.post('/summarize', response_model=summarize_textResponse)
async def summarize_text(request: summarize_textRequest):
    result = await summarize_text_logic(request)
    
    # Return the result directly since it already matches SummarizeResponse structure
    return result

@router.post('/translate', response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    text = request.text
    target_language = request.target_language
    translated_text = await change_language(text, target_language)

    return TranslationResponse(translated_text=translated_text)

@router.post('/flowchart', response_model=flowchart_response)
async def create_flowchart(request: flowchart_request):
    return await create_flowchart_logic(request.text, request.instruction, request.userId, request.language)

@router.post('/flashcard', response_model=flashcard_response)
async def create_flashcard(request: flashcard_request):
    return await create_flashcard_logic(request.text, request.instruction, request.userId, request.language)

# @router.post('/saveUserData', response_model=UserResponse)
# async def saveUserData(request: User):
#     return await save_user_data_logic(request)