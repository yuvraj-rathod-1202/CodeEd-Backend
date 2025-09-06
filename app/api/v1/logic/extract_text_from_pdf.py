from fastapi import HTTPException
from fastapi.responses import JSONResponse
import fitz
from typing import Dict

async def extract_text_from_pdf_logic(pdf_file) -> Dict[str, str]:
    if not pdf_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Read file content
    file_content = await pdf_file.read()

    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    cleaned_text = extracted_text.replace("\n", " ").replace("\r", " ").strip()
    # print(cleaned_text)
    print("length of text", len(cleaned_text))
    if(len(cleaned_text) == 0):
        raise HTTPException(status_code=500, detail=f"no text found in PDF")
    if(len(cleaned_text) > 100000):
        raise HTTPException(status_code=500, detail=f"Please upload small pdf")
    return {"text": cleaned_text}