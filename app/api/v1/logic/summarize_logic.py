import json
import os
from google import genai
from typing import Dict, List, Union, Any, TypedDict, Optional
import re
import math
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from app.services.personalization.prompt_enhancer import enhance_prompt_with_personalization
load_dotenv()
# Configure Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class SummarizeResponse(TypedDict):
    success: bool
    summary: Union[str, List[str], None]
    title: Union[str, None]
    error: Union[str, None]
    format: str
    chunks_processed: int
    original_length: int
    summary_length: int
    estimated_tokens: Union[int, None]
    compression_ratio: Union[float, None]

class TextSummarizer:
    def __init__(self):
        # Gemini's approximate token limit (leaving buffer for prompt and response)
        self.max_tokens_per_request = 25000
        # Approximate characters per token (rough estimate)
        self.chars_per_token = 4
        self.max_chars_per_chunk = self.max_tokens_per_request * self.chars_per_token

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count based on character count"""
        return len(text) // self.chars_per_token

    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks that fit within token limits"""
        if len(text) <= self.max_chars_per_chunk:
            return [text]
        
        chunks = []
        sentences = re.split(r'[.!?]+', text)
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed the limit, start a new chunk
            if len(current_chunk + sentence) > self.max_chars_per_chunk:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
                else:
                    # If a single sentence is too long, split it by words
                    words = sentence.split()
                    word_chunk = ""
                    for word in words:
                        if len(word_chunk + word) > self.max_chars_per_chunk:
                            if word_chunk:
                                chunks.append(word_chunk.strip())
                                word_chunk = word + " "
                            else:
                                # Single word is too long, force split
                                chunks.append(word)
                        else:
                            word_chunk += word + " "
                    if word_chunk:
                        current_chunk = word_chunk
            else:
                current_chunk += sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def create_summary_prompt(self, text: str, format_type: str, length: str = "medium", is_chunk: bool = False, userId: Optional[str] = None) -> str:
        """Create appropriate prompt based on format, length and whether it's a chunk"""
        
        chunk_prefix = "This is part of a larger text. " if is_chunk else ""
        
        # Define length instructions
        length_instructions = {
            "small": "Keep the summary very concise and brief (1-3 sentences for paragraph, 2-4 bullet points for bullets).",
            "medium": "Provide a balanced summary with key points (2-5 sentences for paragraph, 4-7 bullet points for bullets).",
            "large": "Create a detailed and comprehensive summary (4-8 sentences for paragraph, 6-12 bullet points for bullets)."
        }
        
        length_instruction = length_instructions.get(length.lower(), length_instructions["medium"])
        
        if format_type.lower() == "paragraph":
            base_prompt = f"""
            {chunk_prefix}Please provide a comprehensive summary of the following text in paragraph format.
            Also provide a title for the summary.
            The summary should capture the main ideas, key points, and important details in a coherent narrative.
            Make it concise but informative.
            
            LENGTH REQUIREMENT: {length_instruction}
            
            Text to summarize:
            {text}
            
            Please respond in JSON format with:
            {{
                "title": "A brief title for the summary",
                "summary": "The paragraph summary text"
            }}
            """
        elif format_type.lower() == "bullet_points" or format_type.lower() == "bullets":
            base_prompt = f"""
            {chunk_prefix}Please provide a summary of the following text in bullet point format.
            Also provide a title for the summary.
            Extract the main ideas and key points and present them as clear, concise bullet points.
            
            LENGTH REQUIREMENT: {length_instruction}
            
            Text to summarize:
            {text}
            
            Please respond in JSON format with:
            {{
                "title": "A brief title for the summary",
                "summary": ["First bullet point", "Second bullet point", "Third bullet point"]
            }}
            """
        else:
            # Default to paragraph format
            base_prompt = f"""
            {chunk_prefix}Please provide a comprehensive summary of the following text.
            Also provide a title for the summary.
            The summary should capture the main ideas, key points, and important details.
            Make it concise but informative.
            
            LENGTH REQUIREMENT: {length_instruction}
            
            Text to summarize:
            {text}
            
            Please respond in JSON format with:
            {{
                "title": "A brief title for the summary",
                "summary": "The summary text"
            }}
            """
        
        # Enhance the prompt with personalization if userId is provided
        if userId:
            return enhance_prompt_with_personalization(base_prompt, userId)
        
        return base_prompt

    def generate_summary_for_chunk(self, text: str, format_type: str, length: str = "medium", is_chunk: bool = False, userId: Optional[str] = None) -> Dict[str, Any]:
        """Generate summary for a single chunk of text"""
        try:
            prompt = self.create_summary_prompt(text, format_type, length, is_chunk, userId)
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt, config={"response_mime_type": "application/json"})
            if response.text is None:
                raise ValueError("No text received from LLM.")
            data = json.loads(response.text)
            return {
                "title": data.get("title", ""),
                "summary": data.get("summary", "")
            }
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    def combine_chunk_summaries(self, summaries: List[Dict[str, Any]], format_type: str, length: str = "medium", userId: Optional[str] = None) -> Dict[str, Any]:
        """Combine multiple chunk summaries into a final summary"""
        if len(summaries) == 1:
            return summaries[0]
        
        # Extract titles and summaries
        titles = [s.get("title", "") for s in summaries]
        summary_texts = [s.get("summary", "") for s in summaries]
        
        # Create a combined title
        combined_title = f"Summary of {len(summaries)} sections"
        if titles and any(titles):
            # Use the first non-empty title as base
            first_title = next((t for t in titles if t), "")
            if first_title:
                combined_title = first_title
        
        # Define length instructions for combining
        length_instructions = {
            "small": "Keep the combined summary very concise and brief.",
            "medium": "Provide a balanced combined summary with key points.",
            "large": "Create a detailed and comprehensive combined summary."
        }
        
        length_instruction = length_instructions.get(length.lower(), length_instructions["medium"])
        
        if format_type.lower() == "paragraph":
            combined_text = "\n\n".join(summary_texts)
            base_prompt = f"""
            The following are summaries of different parts of a larger text. 
            Please combine them into a single, coherent paragraph summary that flows naturally.
            Remove any redundancy and ensure the summary captures all key points.
            
            LENGTH REQUIREMENT: {length_instruction}
            
            Summaries to combine:
            {combined_text}
            
            Please respond in JSON format with:
            {{
                "title": "{combined_title}",
                "summary": "Single coherent paragraph summary"
            }}
            """
        elif format_type.lower() == "bullet_points" or format_type.lower() == "bullets":
            # Flatten all bullet points from all summaries
            all_bullets = []
            for summary in summary_texts:
                if isinstance(summary, list):
                    all_bullets.extend(summary)
                elif isinstance(summary, str):
                    # Split by bullet points if it's a string
                    bullets = [line.strip().lstrip('•').strip() for line in summary.split('\n') if line.strip()]
                    all_bullets.extend(bullets)
            
            combined_text = "\n".join([f"• {bullet}" for bullet in all_bullets])
            base_prompt = f"""
            The following are bullet points from summaries of different parts of a larger text.
            Please combine them into a single, organized list of bullet points.
            Remove duplicates, merge similar points, and organize them logically.
            
            LENGTH REQUIREMENT: {length_instruction}
            
            Bullet points to combine:
            {combined_text}
            
            Please respond in JSON format with:
            {{
                "title": "{combined_title}",
                "summary": ["First organized bullet point", "Second organized bullet point", "etc"]
            }}
            """
        else:
            combined_text = "\n\n".join(summary_texts)
            base_prompt = f"""
            The following are summaries of different parts of a larger text.
            Please combine them into a single, comprehensive summary.
            Remove any redundancy and ensure all key points are covered.
            
            LENGTH REQUIREMENT: {length_instruction}
            
            Summaries to combine:
            {combined_text}
            
            Please respond in JSON format with:
            {{
                "title": "{combined_title}",
                "summary": "Combined comprehensive summary"
            }}
            """
        
        # Enhance the prompt with personalization if userId is provided
        if userId:
            prompt = enhance_prompt_with_personalization(base_prompt, userId)
        else:
            prompt = base_prompt
        
        try:
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt, config={"response_mime_type": "application/json"})
            if response.text is None:
                raise ValueError("No text received from LLM.")
            return json.loads(response.text)
        except Exception as e:
            # If combining fails, return fallback structure
            return {
                "title": combined_title,
                "summary": summary_texts[0] if summary_texts else ""
            }

    def summarize_text(self, text: str, format_type: str = "paragraph", length: str = "medium", userId: Optional[str] = None) -> Dict[str, Any]:
        """Main method to summarize text with automatic chunking if needed"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if not format_type:
            format_type = "paragraph"
        
        if not length:
            length = "medium"
        
        # Clean the text
        text = text.strip()
        
        # Check if text needs to be chunked
        if len(text) <= self.max_chars_per_chunk:
            # Text is small enough, summarize directly
            return self.generate_summary_for_chunk(text, format_type, length, False, userId)
        else:
            # Text is too large, need to chunk it
            chunks = self.split_text_into_chunks(text)
            print(f"Text split into {len(chunks)} chunks for processing")
            
            # Generate summaries for each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks, 1):
                print(f"Processing chunk {i}/{len(chunks)}")
                summary = self.generate_summary_for_chunk(chunk, format_type, length, True, userId)
                chunk_summaries.append(summary)
            
            # Combine all chunk summaries into final summary
            final_summary = self.combine_chunk_summaries(chunk_summaries, format_type, length, userId)
            return final_summary

# Initialize the summarizer
text_summarizer = TextSummarizer()

async def summarize_text_logic(request) -> SummarizeResponse:
    """
    Async wrapper for text summarization logic
    
    Args:
        request: The request object containing text and format_type
    
    Returns:
        SummarizeResponse containing success status, summary, and metadata
    """
    try:
        # Extract text, format, and userId from request
        text = request.text
        format_type = request.format if hasattr(request, 'format') else "paragraph"
        length = request.length if hasattr(request, 'length') else "medium"
        userId = request.userId if hasattr(request, 'userId') else None
        
        # Validate inputs
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Text cannot be empty",
                "summary": None,
                "title": None,
                "format": format_type,
                "chunks_processed": 0,
                "original_length": 0,
                "summary_length": 0,
                "estimated_tokens": None,
                "compression_ratio": None
            }
        
        # Validate format type
        valid_formats = ["paragraph", "bullet_points", "bullets"]
        if format_type.lower() not in valid_formats:
            format_type = "paragraph"  # Default to paragraph
        
        # Validate length
        valid_lengths = ["small", "medium", "large"]
        if length.lower() not in valid_lengths:
            length = "medium"  # Default to medium
        
        original_length = len(text)
        estimated_tokens = text_summarizer.estimate_tokens(text)
        
        # Run summarization in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                text_summarizer.summarize_text, 
                text, 
                format_type,
                length,
                userId
            )
        
        # Extract title and summary from result
        title = result.get("title", "Summary")
        summary = result.get("summary", "")
        
        summary_length = len(str(summary)) if summary else 0
        chunks_needed = len(text_summarizer.split_text_into_chunks(text))
        
        return {
            "success": True,
            "error": None,
            "summary": summary,
            "title": title,
            "format": format_type,
            "chunks_processed": chunks_needed,
            "original_length": original_length,
            "summary_length": summary_length,
            "estimated_tokens": estimated_tokens,
            "compression_ratio": round(summary_length / original_length, 2) if original_length > 0 else 0
        }
        
    except Exception as e:
        # Initialize default values for error response
        format_type = getattr(request, 'format', 'paragraph') if hasattr(request, 'format') else 'paragraph'
        text = getattr(request, 'text', '') if hasattr(request, 'text') else ''
        
        return {
            "success": False,
            "error": f"Error during summarization: {str(e)}",
            "summary": None,
            "title": None,
            "format": format_type,
            "chunks_processed": 0,
            "original_length": len(text) if text else 0,
            "summary_length": 0,
            "estimated_tokens": None,
            "compression_ratio": None
        }

def summarize_text_sync(text: str, format_type: str = "paragraph", length: str = "medium", userId: Optional[str] = None) -> Dict[str, Union[str, int, float, bool, None]]:
    """
    Synchronous version of text summarization logic
    
    Args:
        text (str): The text to summarize
        format_type (str): Format for summary - 'paragraph' or 'bullet_points'
        length (str): Length of summary - 'small', 'medium', or 'large'
        userId (Optional[str]): Optional user ID for personalization
    
    Returns:
        Dict containing success status, summary, and metadata
    """
    try:
        # Validate inputs
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Text cannot be empty",
                "summary": None,
                "title": None,
                "format": format_type,
                "chunks_processed": 0,
                "original_length": 0,
                "summary_length": 0
            }
        
        # Validate format type
        valid_formats = ["paragraph", "bullet_points", "bullets"]
        if format_type.lower() not in valid_formats:
            format_type = "paragraph"  # Default to paragraph
        
        # Validate length
        valid_lengths = ["small", "medium", "large"]
        if length.lower() not in valid_lengths:
            length = "medium"  # Default to medium
        
        original_length = len(text)
        estimated_tokens = text_summarizer.estimate_tokens(text)
        
        # Run summarization
        result = text_summarizer.summarize_text(text, format_type, length, userId)
        
        # Extract title and summary from result
        title = result.get("title", "Summary")
        summary = result.get("summary", "")
        
        summary_length = len(str(summary)) if summary else 0
        chunks_needed = len(text_summarizer.split_text_into_chunks(text))
        
        return {
            "success": True,
            "error": None,
            "summary": summary,
            "title": title,
            "format": format_type,
            "chunks_processed": chunks_needed,
            "original_length": original_length,
            "summary_length": summary_length,
            "estimated_tokens": estimated_tokens,
            "compression_ratio": round(summary_length / original_length, 2) if original_length > 0 else 0
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error during summarization: {str(e)}",
            "summary": None,
            "title": None,
            "format": format_type,
            "chunks_processed": 0,
            "original_length": len(text) if text else 0,
            "summary_length": 0
        }
