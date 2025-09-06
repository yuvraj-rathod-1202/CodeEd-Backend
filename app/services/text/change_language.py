import json
import os
from google import genai
from deep_translator import GoogleTranslator
from fastapi import HTTPException
import asyncio
from typing import Dict, Optional
from dotenv import load_dotenv
from app.services.personalization.prompt_enhancer import enhance_prompt_with_personalization

load_dotenv()

# Configure Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Language code mapping
LANGUAGE_CODES = {
    'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
    'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'japanese': 'ja',
    'korean': 'ko', 'chinese': 'zh', 'arabic': 'ar', 'hindi': 'hi',
    'dutch': 'nl', 'swedish': 'sv', 'norwegian': 'no', 'danish': 'da',
    'finnish': 'fi', 'polish': 'pl', 'turkish': 'tr', 'greek': 'el',
    'hebrew': 'he', 'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id',
    'malay': 'ms', 'bengali': 'bn', 'tamil': 'ta', 'telugu': 'te',
    'gujarati': 'gu', 'marathi': 'mr', 'punjabi': 'pa', 'urdu': 'ur'
}

def get_language_code(language: str) -> str:
    language_lower = language.lower().strip()
    if len(language_lower) == 2:
        return language_lower
    return LANGUAGE_CODES.get(language_lower, language_lower)

async def personalized_translate_with_ai(text: str, target_language: str, userId: Optional[str] = None) -> Dict[str, str]:
    """
    Use Gemini AI to provide personalized, context-aware translation that considers user background.
    This provides more nuanced translations than basic machine translation.
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        if not target_language.strip():
            raise HTTPException(status_code=400, detail="Target language cannot be empty")

        # Create base translation prompt
        base_prompt = f"""
Please provide a high-quality, contextually appropriate translation of the following text to {target_language}.

TRANSLATION REQUIREMENTS:
1. Maintain the original meaning and tone
2. Use natural, fluent language in the target language
3. Consider cultural context and idioms
4. Preserve any technical terms or educational content appropriately
5. If the text contains educational content, ensure the translation is suitable for learning
6. Adapt formality level appropriately for the target language and context

Original Text:
{text}

Target Language: {target_language}

Please respond in JSON format with:
{{
    "translated_text": "The translated text in {target_language}",
}}
"""

        # Enhance prompt with personalization if userId provided
        if userId:
            prompt = enhance_prompt_with_personalization(base_prompt, userId)
        else:
            prompt = base_prompt

        # Generate translation using Gemini AI
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )

        if response.text is None:
            raise ValueError("No response received from AI translation service")

        result = json.loads(response.text)
        
        return {
            "translated_text": result.get("translated_text", ""),
        }

    except json.JSONDecodeError:
        # Fallback to basic translation if AI parsing fails
        return await change_language(text, target_language, fallback=True)
    except Exception as e:
        error_msg = str(e).lower()
        if "api" in error_msg or "quota" in error_msg:
            # Fallback to basic translation if AI service fails
            return await change_language(text, target_language, fallback=True)
        else:
            raise HTTPException(status_code=500, detail=f"Personalized translation failed: {str(e)}")

async def change_language(text: str, target_language: str, userId: Optional[str] = None, fallback: bool = False) -> Dict[str, str]:
    """
    Enhanced translation function that can use AI personalization or fallback to basic translation.
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        if not target_language.strip():
            raise HTTPException(status_code=400, detail="Target language cannot be empty")

        # Use AI personalized translation if not in fallback mode
        if not fallback and userId:
            try:
                return await personalized_translate_with_ai(text, target_language, userId)
            except Exception as e:
                print(f"AI translation failed, falling back to basic translation: {e}")

        # Basic translation using GoogleTranslator
        target_lang_code = get_language_code(target_language)

        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None,
            lambda: GoogleTranslator(source="auto", target=target_lang_code).translate(text)
        )

        return {
            "translated_text": translated,
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        if "not supported" in error_msg or "invalid" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {target_language}"
            )
        elif any(x in error_msg for x in ["network", "connection", "timeout"]):
            raise HTTPException(
                status_code=503,
                detail="Translation service temporarily unavailable. Try again later."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

async def get_translation_with_context(text: str, target_language: str, userId: Optional[str] = None, context: Optional[str] = None) -> Dict[str, str]:
    """
    Get translation with additional context information for better personalization.
    
    Args:
        text: Text to translate
        target_language: Target language for translation
        userId: Optional user ID for personalization
        context: Optional additional context (e.g., "academic", "casual", "technical")
    
    Returns:
        Dict containing translated text and metadata
    """
    try:
        if context:
            # Add context to the text for better translation
            contextual_text = f"Context: {context}\n\nText: {text}"
            result = await change_language(contextual_text, target_language, userId)
            # Remove context from translated result if it was added
            if result["translated_text"].startswith("Context:"):
                lines = result["translated_text"].split("\n")
                result["translated_text"] = "\n".join(lines[2:]) if len(lines) > 2 else result["translated_text"]
            return result
        else:
            return await change_language(text, target_language, userId)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contextual translation failed: {str(e)}")

async def detect_and_translate(text: str, target_language: str, userId: Optional[str] = None) -> Dict[str, str]:
    """
    Detect source language and translate with personalization.
    """
    try:
        # For now, we'll use auto-detection in GoogleTranslator
        # In the future, this could be enhanced with AI-based language detection
        result = await change_language(text, target_language, userId)
        result["source_language"] = "auto-detected"
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection and translation failed: {str(e)}")

# Backward compatibility function that returns just the string
async def simple_translate(text: str, target_language: str) -> str:
    """
    Simple translation function for backward compatibility.
    Returns just the translated text as a string.
    """
    result = await change_language(text, target_language)
    return result["translated_text"]

# For detection you need a different lib
# Example with langdetect:
# pip install langdetect
# from langdetect import detect, detect_langs

# async def detect_language(text: str) -> Dict[str, str]:
#     try:
#         if not text.strip():
#             raise HTTPException(status_code=400, detail="Text cannot be empty")

#         loop = asyncio.get_running_loop()
#         detected = await loop.run_in_executor(
#             None,
#             lambda: detect_langs(text)
#         )

#         # detect_langs gives list of possibilities with probabilities
#         best = detected[0]
#         return {"language": best.lang, "confidence": str(best.prob)}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")
