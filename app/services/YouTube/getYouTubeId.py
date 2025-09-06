import re

class GetYoutubeURL():
    def __init__(self, input_url) -> None:
        self.input_url = input_url

    def get_youtube_video_id(self) -> str | None:
        
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:&|\/|\?|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, self.input_url)
            if match:
                return match.group(1)
        return None