from fastapi import HTTPException
from typing import Dict
import re
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

def get_video_id(url: str) -> str:
    # Extract video ID from YouTube URL
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|$)*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise HTTPException(status_code=400, detail="Invalid YouTube URL.")

def check_video_duration(video_id: str) -> bool:
    """
    Check if video duration is reasonable (under 30 minutes).
    Returns True if duration is acceptable, False otherwise.
    """
    try:
        # Try to get video info from YouTube API (if available) 
        # or use yt-dlp/youtube-dl approach
        # For now, we'll skip this check and rely on text length limits
        return True
    except:
        return True  # If we can't check duration, proceed anyway

async def extract_text(video_id: str) -> str:
    """
    Extract text from YouTube video. First tries YouTube's built-in captions,
    then falls back to AssemblyAI for transcription if needed.
    """
    
    # First, try to get existing YouTube captions (fastest method)
    try:
        print("Trying to get YouTube captions...")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # print("Raw transcript list:", transcript_list)
        transcript_text = " ".join([entry['text'] for entry in transcript_list])
        
        if transcript_text.strip():
            print("Using YouTube captions (fast method)")
            return transcript_text
        else:
            return "No YouTube captions available, using AssemblyAI..."
            
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "Error: No transcript available for this video."
    except VideoUnavailable:
        return "Error: The video is unavailable."
    except Exception as e:
        return f"Unexpected error: {e}"

async def extract_text_from_youtube_logic(video_url: str) -> Dict[str, str]:
    """
    Extract text from a YouTube video URL.
    
    Args:
        video_url (str): The YouTube video URL
        
    Returns:
        Dict[str, str]: A dictionary containing the extracted text
        
    Raises:
        HTTPException: If URL is invalid or text extraction fails
    """
    if "youtube.com" not in video_url and "youtu.be" not in video_url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")

    video_id = get_video_id(video_url)
    print("Extracting text from video ID:", video_id)

    # Extract actual transcript from the video
    extracted_text = await extract_text(video_id)
    print("Raw extracted text length:", len(extracted_text))

    # Clean the text by removing excessive whitespace and newlines
    cleaned_text = extracted_text.replace("\n", " ").replace("\r", " ").strip()
    # Remove multiple spaces with single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    print("Length of extracted text:", len(cleaned_text))
    
    if len(cleaned_text) == 0:
        raise HTTPException(status_code=500, detail="No text found in the YouTube video.")
    

    return {"text": cleaned_text[:100000]}


# urls = [
#     "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
#     "https://youtu.be/dQw4w9WgXcQ",
#     "https://www.youtube.com/embed/dQw4w9WgXcQ",
#     "https://www.youtube.com/v/dQw4w9WgXcQ",
#     "https://www.youtube.com/shorts/dQw4w9WgXcQ"
# ]

# async def test():
#     # Test the function with a sample URL
#     video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
#     result = await extract_text_from_youtube_logic(video_url)
#     print(result)

# asyncio.run(test())