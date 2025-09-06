from googletrans import Translator
from fastapi import HTTPException
import asyncio
from typing import Dict

# Initialize the translator
translator = Translator()

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

async def change_language(text: str, target_language: str) -> str:
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        if not target_language.strip():
            raise HTTPException(status_code=400, detail="Target language cannot be empty")

        target_lang_code = get_language_code(target_language)

        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None,
            lambda: translator.translate(text, dest=target_lang_code)
        )

        return translated.text

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        if "language" in error_msg and ("not supported" in error_msg or "invalid" in error_msg):
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

async def detect_language(text: str) -> Dict[str, str]:
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        loop = asyncio.get_running_loop()
        detected = await loop.run_in_executor(
            None,
            lambda: translator.detect(text)
        )

        return {"language": detected.lang, "confidence": str(detected.confidence)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")
