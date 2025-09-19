from fastapi import HTTPException
from typing import Dict
import re
import requests
import time
import random
import json
import xml.etree.ElementTree as ET
from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Alternative approach using direct API calls
def get_transcript_alternative(video_id: str) -> str:
    """
    Alternative method to get transcript using direct requests to avoid browser blocking
    """
    try:
        # Method 1: Use YouTube's mobile API endpoint (less restrictive)
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        # Try YouTube's timedtext API with mobile headers
        url = f"https://www.youtube.com/api/timedtext"
        params = {
            'v': video_id,
            'lang': 'en',
            'fmt': 'json3'
        }
        
        # Add some randomization to avoid detection
        time.sleep(random.uniform(0.5, 2.0))
        
        response = requests.get(url, params=params, headers=mobile_headers, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'events' in data:
                    transcript_text = ""
                    for event in data['events']:
                        if 'segs' in event:
                            for seg in event['segs']:
                                if 'utf8' in seg:
                                    transcript_text += seg['utf8'] + " "
                    
                    if transcript_text.strip():
                        return transcript_text.strip()
            except:
                pass
        
        # Method 2: Try different parameters and endpoints
        alternative_params = [
            {'v': video_id, 'lang': 'en-US', 'fmt': 'srv3'},
            {'v': video_id, 'lang': 'en', 'fmt': 'srv1'},
            {'v': video_id, 'lang': 'en', 'fmt': 'ttml'},
            {'v': video_id, 'tlang': 'en'}
        ]
        
        for params in alternative_params:
            try:
                time.sleep(random.uniform(0.3, 1.0))
                response = requests.get(url, params=params, headers=mobile_headers, timeout=10)
                
                if response.status_code == 200 and response.text:
                    # Try to parse different formats
                    if 'fmt=srv3' in str(params) or 'fmt=srv1' in str(params):
                        # Parse XML response
                        try:
                            root = ET.fromstring(response.text)
                            text_elements = root.findall('.//text')
                            transcript_text = " ".join([elem.text for elem in text_elements if elem.text])
                            
                            if transcript_text.strip():
                                return transcript_text.strip()
                        except:
                            continue
                    
                    elif 'fmt=ttml' in str(params):
                        # Parse TTML format
                        try:
                            root = ET.fromstring(response.text)
                            # TTML has different structure
                            p_elements = root.findall('.//{http://www.w3.org/ns/ttml}p')
                            transcript_text = " ".join([elem.text for elem in p_elements if elem.text])
                            
                            if transcript_text.strip():
                                return transcript_text.strip()
                        except:
                            continue
                            
            except Exception as e:
                print(f"Alternative params failed: {e}")
                continue
        
        # Method 3: Try using YouTube watch page approach
        try:
            watch_headers = get_random_headers()
            watch_url = f"https://m.youtube.com/watch?v={video_id}"
            
            response = requests.get(watch_url, headers=watch_headers, timeout=10)
            
            if response.status_code == 200:
                # Look for caption tracks in the page source
                import re
                caption_pattern = r'"captionTracks":\[(.*?)\]'
                match = re.search(caption_pattern, response.text)
                
                if match:
                    print("Found caption tracks in page source")
                    # This would require more complex parsing
                    # For now, just indicate we found something
                    
        except Exception as e:
            print(f"Watch page method failed: {e}")
                
        return ""
        
    except Exception as e:
        print(f"Alternative method failed: {e}")
        return ""

def get_random_headers():
    """Get random headers to avoid detection with updated 2025 browser versions"""
    user_agents = [
        # Chrome 129 (Latest 2025)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        
        # Chrome 128 (Stable)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        
        # Firefox 130 (Latest 2025)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
        
        # Firefox 129 (Stable)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
        
        # Edge 129 (Latest 2025)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
        
        # Safari 17.6 (Latest 2025)
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1',
        
        # Opera 104 (Latest 2025)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/104.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 OPR/104.0.0.0'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }

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
    Extract text from YouTube video with IP masking and retry logic.
    First tries alternative methods to bypass browser detection, then falls back to youtube-transcript-api.
    """
    
    # First, try alternative method with updated headers (bypass browser check)
    print("Trying alternative method with updated 2025 browser headers...")
    try:
        alternative_text = get_transcript_alternative(video_id)
        if alternative_text:
            print("Successfully extracted transcript using alternative method with updated headers")
            return alternative_text
    except Exception as e:
        print(f"Alternative method failed: {e}")
    
    # Then try the standard youtube-transcript-api with multiple strategies
    strategies = [
        {"retry_count": 2, "delay": 1},
        {"retry_count": 2, "delay": 3},
        {"retry_count": 1, "delay": 5}
    ]
    
    for strategy_idx, strategy in enumerate(strategies):
        print(f"Trying youtube-transcript-api strategy {strategy_idx + 1}: {strategy}")
        
        for attempt in range(strategy["retry_count"]):
            try:
                print(f"Attempt {attempt + 1} of {strategy['retry_count']}")
                
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = strategy["delay"] + random.uniform(0, 2)
                    print(f"Waiting {delay:.1f} seconds before retry...")
                    time.sleep(delay)
                
                # Try different language codes
                language_codes = ['en', 'en-US', 'en-GB', 'auto']
                
                for lang_code in language_codes:
                    try:
                        print(f"Trying language code: {lang_code}")
                        
                        if lang_code == 'auto':
                            # Try to get any available transcript
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        else:
                            # Try specific language
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
                        
                        # Process transcript
                        transcript_text = " ".join([entry['text'] for entry in transcript_list])
                        
                        if transcript_text.strip():
                            print(f"Successfully extracted transcript using language: {lang_code}")
                            return transcript_text
                            
                    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
                        print(f"Language {lang_code} failed: {str(e)}")
                        continue
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "browser" in error_msg or "update" in error_msg or "supported" in error_msg:
                            print(f"Browser detection error for {lang_code}: {e}")
                            # Skip this language and try next
                            continue
                        else:
                            print(f"Language {lang_code} error: {str(e)}")
                            continue
                
                # If we get here, all language attempts failed for this strategy
                print("All language codes failed for this attempt")
                
            except TranscriptsDisabled:
                return "Error: Transcripts are disabled for this video."
            except NoTranscriptFound:
                print("No transcript found, trying next strategy...")
                break  # Try next strategy
            except VideoUnavailable:
                return "Error: The video is unavailable."
            except Exception as e:
                error_msg = str(e).lower()
                if "browser" in error_msg or "update" in error_msg or "supported" in error_msg:
                    print(f"Browser detection error: {e}")
                    # This is the browser update error - try next strategy
                    break
                elif "ip" in error_msg or "blocked" in error_msg or "rate" in error_msg:
                    print(f"IP/Rate limiting detected: {e}")
                    if attempt < strategy["retry_count"] - 1:
                        continue  # Try again with this strategy
                    else:
                        break  # Try next strategy
                else:
                    print(f"Unexpected error: {e}")
                    if attempt < strategy["retry_count"] - 1:
                        continue
    
    # Final fallback: try alternative method again with different parameters
    print("Trying alternative method again as final fallback...")
    try:
        alternative_text = get_transcript_alternative(video_id)
        if alternative_text:
            print("Successfully extracted transcript using alternative method (final attempt)")
            return alternative_text
    except Exception as e:
        print(f"Final alternative method also failed: {e}")
    
    # If all strategies failed
    return "Error: Unable to extract transcript. YouTube is blocking requests or the video may not have captions available. This appears to be due to browser detection - please try again later."

def get_proxy_list():
    """Get list of free proxy servers for testing"""
    # Note: In production, you should use paid proxy services
    # These are example proxy configurations
    proxies = [
        {"http": "http://proxy1.example.com:8080", "https": "https://proxy1.example.com:8080"},
        {"http": "http://proxy2.example.com:3128", "https": "https://proxy2.example.com:3128"},
        # Add more proxies as needed
    ]
    
    # For testing purposes, return empty list
    # In production, implement proper proxy rotation service
    return []

async def extract_text_from_youtube_logic(video_url: str) -> Dict[str, str]:
    """
    Extract text from a YouTube video URL with enhanced error handling and IP masking.
    
    Args:
        video_url (str): The YouTube video URL
        
    Returns:
        Dict[str, str]: A dictionary containing the extracted text
        
    Raises:
        HTTPException: If URL is invalid or text extraction fails
    """
    if "youtube.com" not in video_url and "youtu.be" not in video_url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")

    try:
        video_id = get_video_id(video_url)
        print("Extracting text from video ID:", video_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse video ID: {str(e)}")

    # Extract actual transcript from the video with enhanced error handling
    try:
        extracted_text = await extract_text(video_id)
        print("Raw extracted text length:", len(extracted_text))
        
        # Check if we got an error message instead of transcript
        if extracted_text.startswith("Error:"):
            raise HTTPException(status_code=500, detail=extracted_text)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Handle any unexpected errors during transcript extraction
        error_msg = str(e).lower()
        if "ip" in error_msg or "blocked" in error_msg or "rate" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="Rate limited or IP blocked. Please try again later or use a different network."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to extract transcript: {str(e)}"
            )

    # Clean the text by removing excessive whitespace and newlines
    cleaned_text = extracted_text.replace("\n", " ").replace("\r", " ").strip()
    # Remove multiple spaces with single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    print("Length of extracted text:", len(cleaned_text))
    
    # Validate the extracted text
    if len(cleaned_text) == 0:
        raise HTTPException(status_code=500, detail="No text found in the YouTube video.")
    
    if len(cleaned_text) < 10:
        raise HTTPException(
            status_code=500, 
            detail="Extracted text is too short. The video may not have proper captions."
        )

    # Limit text length to prevent processing issues
    max_length = 100000
    if len(cleaned_text) > max_length:
        cleaned_text = cleaned_text[:max_length]
        print(f"Text truncated to {max_length} characters")

    return {"text": cleaned_text}


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