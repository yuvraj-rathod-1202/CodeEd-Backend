from fastapi import HTTPException
from fastapi.responses import JSONResponse
import fitz
from typing import Dict
from docx import Document
from pptx import Presentation
from PIL import Image
import pytesseract
from io import BytesIO
import speech_recognition as sr
from pydub import AudioSegment
import ffmpeg

def text_cleaning(extracted_text: str) -> Dict[str, str]:
    cleaned_text = extracted_text.replace("\n", " ").replace("\r", " ").strip()
    print("length of text", len(cleaned_text))
    if(len(cleaned_text) == 0):
        raise HTTPException(status_code=500, detail=f"no text found in file")
    if(len(cleaned_text) > 100000):
        raise HTTPException(status_code=500, detail=f"Please upload small file")
    return {"text": cleaned_text}

async def extract_text_from_pdf_logic(pdf_file) -> Dict[str, str]:
    if not pdf_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    file_content = await pdf_file.read()

    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    return text_cleaning(extracted_text)


async def extract_text_from_docx_logic(docx_file) -> Dict[str, str]:
    if not docx_file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files are allowed.")
    
    file_content = await docx_file.read()

    try:

        document = Document(BytesIO(file_content))
        extracted_text = ""
        for para in document.paragraphs:
            extracted_text += para.text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing DOCX: {str(e)}")
    
    return text_cleaning(extracted_text)

async def extract_text_from_html_logic(html_file) -> Dict[str, str]:
    if not html_file.filename.endswith(".html") and not html_file.filename.endswith(".htm"):
        raise HTTPException(status_code=400, detail="Only HTML files are allowed.")
    
    file_content = await html_file.read()
    try:
        extracted_text = file_content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing HTML: {str(e)}")

    return text_cleaning(extracted_text)

async def extract_text_from_text_logic(txt_file) -> Dict[str, str]:
    if not txt_file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only TXT files are allowed.")
    
    file_content = await txt_file.read()
    try:
        extracted_text = file_content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing TXT: {str(e)}")

    return text_cleaning(extracted_text)

async def extract_text_from_pptx_logic(pptx_file) -> Dict[str, str]:
    if not pptx_file.filename.endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only PPTX files are allowed.")
    
    file_content = await pptx_file.read()
    try:
        presentation = Presentation(BytesIO(file_content))
        extracted_text = ""
        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    extracted_text += getattr(shape, "text") + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PPTX: {str(e)}")
    
    return text_cleaning(extracted_text)

async def extract_text_from_md_logic(md_file) -> Dict[str, str]:
    if not md_file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only MD files are allowed.")
    
    file_content = await md_file.read()
    try:
        extracted_text = file_content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing MD: {str(e)}")
    
    return text_cleaning(extracted_text)

async def extract_text_from_image_logic(image_file) -> Dict[str, str]:
    if not (image_file.filename.endswith(".png") or image_file.filename.endswith(".jpg") or image_file.filename.endswith(".jpeg")):
        raise HTTPException(status_code=400, detail="Only PNG, JPG, and JPEG files are allowed.")
    
    file_content = await image_file.read()
    try:
        image = Image.open(BytesIO(file_content))
        extracted_text = pytesseract.image_to_string(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    return text_cleaning(extracted_text)

async def extract_text_from_audio_logic(audio_file) -> Dict[str, str]:
    if not (audio_file.filename.endswith(".wav") or audio_file.filename.endswith(".mp3") or audio_file.filename.endswith(".m4a")):
        raise HTTPException(status_code=400, detail="Only WAV, MP3, and M4A files are allowed.")
    
    file_content = await audio_file.read()
    try:
        audio = AudioSegment.from_file(BytesIO(file_content))
        audio = audio.set_frame_rate(16000).set_channels(1)
        temp_wav = BytesIO()
        audio.export(temp_wav, format="wav")
        temp_wav.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            extracted_text = recognizer.recognize_google(audio_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
    
    return text_cleaning(extracted_text)

async def extract_text_from_video_logic(video_file) -> Dict[str, str]:
    if not (video_file.filename.endswith(".mp4") or video_file.filename.endswith(".mov") or video_file.filename.endswith(".avi")):
        raise HTTPException(status_code=400, detail="Only MP4, MOV, and AVI files are allowed.")
    
    file_content = await video_file.read()
    try:
        out, err = (
            ffmpeg
            .input('pipe:0')
            .output('pipe:1', format='wav', acodec='pcm_s16le', ac=1, ar='16000')
            .run(input=file_content, capture_stdout=True, capture_stderr=True)
        )

        temp_audio = BytesIO(out)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio) as source:
            audio_data = recognizer.record(source)
            extracted_text = recognizer.recognize_google(audio_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
    
    return text_cleaning(extracted_text)

async def extract_text_logic(file) -> Dict[str, str]:
    if file.size > 10 * 1024 * 1024:  # 10 MB
        return {"text": "File size exceeds the 10MB limit. Please upload a smaller file."}
    
    if file.filename.endswith(".pdf"):
        textObj = await extract_text_from_pdf_logic(file)
        return textObj

    if file.filename.endswith(".txt"):
        textObj = await extract_text_from_text_logic(file)
        return textObj

    if file.filename.endswith(".docx"):
        textObj = await extract_text_from_docx_logic(file)
        return textObj

    if file.filename.endswith(".html"):
        textObj = await extract_text_from_html_logic(file)
        return textObj
    
    if file.filename.endswith(".pptx"):
        textObj = await extract_text_from_pptx_logic(file)
        return textObj
    
    if file.filename.endswith(".md"):
        textObj = await extract_text_from_md_logic(file)
        return textObj
    
    if file.filename.endswith(".png") or file.filename.endswith(".jpg") or file.filename.endswith(".jpeg"):
        textObj = await extract_text_from_image_logic(file)
        return textObj
    
    if file.filename.endswith(".wav") or file.filename.endswith(".mp3") or file.filename.endswith(".m4a"):
        textObj = await extract_text_from_audio_logic(file)
        return textObj
    
    if file.filename.endswith(".mp4") or file.filename.endswith(".mov") or file.filename.endswith(".avi"):
        textObj = await extract_text_from_video_logic(file)
        return textObj

    return {"text": "No valid file format found. Please upload a PDF, DOCX, HTML, TXT, PPTX, IMAGE, Audio, Video or MD file."}