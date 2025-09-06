from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)
import time
import requests

class GetYouTubeTranscript:
    def __init__(self, id: str) -> None:
        self.video_id = id

    def safe_get_transcript(self, video_id, retries=10, delay=2):
        original_get = requests.get

        def custom_get(*args, **kwargs):
            kwargs['headers'] = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
            }
            return original_get(*args, **kwargs)


        requests.get = custom_get  # Monkey patch
        try:
            for attempt in range(retries):
                try:
                    print(f"[Attempt {attempt + 1}] Trying to fetch transcript for: {video_id}")
                    transcripts = YouTubeTranscriptApi.get_transcript(video_id)
                    return transcripts

                except Exception as e:
                    error_msg = str(e).lower()
                    print(f"[Attempt {attempt + 1}] Error: {e}")

                    if "no element found" in error_msg or "response text is not valid json" in error_msg:
                        print(f"[Attempt {attempt + 1}] Transient error, retrying...")
                    elif "429" in error_msg or "rate limit" in error_msg:
                        print(f"[Attempt {attempt + 1}] Rate limit hit, retrying...")
                    else:
                        print(f"[Attempt {attempt + 1}] Unhandled error. Breaking retry loop.")
                        raise e
                    time.sleep(delay)
            raise RuntimeError(f"Failed to fetch transcript for {video_id} after {retries} attempts.")
        finally:
            requests.get = original_get  # Restore original

    def get_youtube_transcript(self) -> str:
        try:
            transcript = self.safe_get_transcript(self.video_id)
            return "".join([item['text'] for item in transcript])
        except TranscriptsDisabled:
            return "Error: Transcripts are disabled for this video."
        except NoTranscriptFound:
            return "Error: No transcript found for this video."
        except VideoUnavailable:
            return "Error: The video is unavailable or private."
        except CouldNotRetrieveTranscript as e:
            return f"Error: Could not retrieve transcript due to parsing issues. Reason: {str(e)}"
        except Exception as e:
            return f"Error: {e} (video_id: {self.video_id})"
