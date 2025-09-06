"""
Test script to verify the summarize functionality
"""
import asyncio
import os
from app.api.v1.logic.summarize_logic import summarize_text_logic
from app.models.BaseModel.summrize import summarize_textRequest

# Set up environment variable for testing (replace with your actual API key)
# os.environ["GEMINI_API_KEY"] = "your-api-key-here"

async def test_summarize():
    # Test request
    request = summarize_textRequest(
        text="This is a test text for summarization. It contains multiple sentences to test the summarization functionality. The text talks about artificial intelligence and machine learning, which are important topics in modern technology.",
        format="paragraph"
    )
    
    try:
        result = await summarize_text_logic(request)
        print("✅ Summarization test successful!")
        print(f"📝 Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_summarize())
