from google import genai
from app.models.BaseModel.common import Question
import os
from dotenv import load_dotenv
import json
from typing import Optional
from app.services.personalization.prompt_enhancer import enhance_prompt_with_personalization

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class GetQuestions:
    def get_questions(self, text: str, numbers: int, difficulty: str = "Medium", quiz_type: str = "mix", userId: Optional[str] = None, language: Optional[str] = "English") -> tuple[list[Question], str]:
        current_id = 1

        if quiz_type == "mix":
            types = ['mcq', 'truefalse', 'short']
            base = numbers // 3
            remainder = numbers % 3

            type_counts = {t: base for t in types}
            for i in range(remainder):
                type_counts[types[i]] += 1

            combined = []
            for t in types:
                batch, current_id = self.get_questions_for_type(text, type_counts[t], difficulty, t, current_id, userId)
                combined.extend(batch)
            title = self.get_title_for_quiz(text, userId, language)
            return (combined, title)
        else:
            batch, _ = self.get_questions_for_type(text, numbers, difficulty, quiz_type, current_id, userId)
            return (batch, self.get_title_for_quiz(text, userId, language))


    def get_questions_for_type(self, text: str, count: int, difficulty: str, quiz_type: str, start_id: int, userId: Optional[str] = None, language: Optional[str] = "English") -> tuple[list[Question], int]:
        instruction = self._get_quiz_type_instruction(quiz_type)

        base_prompt = f"""
Generate {count} {quiz_type.upper()} questions from the given context.
Each question should match the structure below:

{{
  "id": integer (starting from 1) should be unique for each question,
  "question": string,
  "type": "{quiz_type}",
  "difficulty": "{difficulty}",
  {"\"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"]," if quiz_type == "mcq" else ""}
  "correct": {"an integer index (0-3)" if quiz_type == "mcq" else "true/false" if quiz_type == "truefalse" else "string"},
  "explanation": "Why the correct answer is right"
}}

❗ Rules:
- The field name must be `"options"` (not `"option"`), and only present for `"mcq"` type.
- Ensure all 4 options are meaningful and distinct for `"mcq"`.
- **IMPORTANT FOR MCQ**: Randomize the position of the correct answer across all questions. Do NOT always put the correct answer in position 1 (index 1/Option B). Mix it up - sometimes use index 0 (Option A), sometimes 1 (Option B), sometimes 2 (Option C), sometimes 3 (Option D). Aim for roughly equal distribution across all positions.
- Return only a valid JSON array (no markdown, no commentary).
- Strictly follow the key structure and types.

🧠 Psychology & Engagement Instructions:

- Use simplified and student-friendly language for both questions and options so it's easy to understand even for beginners.
- Frame the questions in a way that psychologically **hooks the user** — by creating **mild suspense**, **surprise**, or **personal connection**.
- Add subtle **curiosity triggers** that make the user want to learn more after each question.
- Ensure that the quiz **adds value** — by either introducing a new insight or reinforcing important ideas in an interesting way.
- The goal is not just assessment, but to **make the user feel smarter and curious to explore more**.

⚠️ CRITICAL LANGUAGE REQUIREMENT: You MUST respond STRICTLY in {language}. All node labels, title, and content must be written in {language} only. This is a strict requirement - follow it without exception.

Context:
{text}
"""

        # Enhance the prompt with personalization if userId is provided
        if userId:
            prompt = enhance_prompt_with_personalization(base_prompt, userId)
        else:
            prompt = base_prompt


        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            if response.text is None:
                print("❌ No text received from Gemini.")
                return ([], start_id)

            
            # print(response.text)

            raw = json.loads(response.text)

            data = []
            for i, qa in enumerate(raw, start=start_id):
                try:
                    qa["id"] = i
                    print(f"✅ Processing question #{i} {qa['id']}")
                    data.append(Question(**qa))
                except Exception as e:
                    print(f"❌ Skipping malformed question #{i}: — Error: {e}")

            return data, start_id + len(data)
            

        except Exception as e:
            print("❌ Generation error:", e)
            return ([], start_id)

    def get_title_for_quiz(self, text: str, userId: Optional[str] = None, language: Optional[str] = "English") -> str:
        base_prompt = f"""Generate a concise and engaging title for a quiz based on the following context:
{text}

⚠️ CRITICAL LANGUAGE REQUIREMENT: You MUST respond STRICTLY in {language}. All node labels, title, and content must be written in {language} only. This is a strict requirement - follow it without exception.

The title should be catchy, relevant, and reflect the main theme or topic of the content. It should not exceed 10 words and should be suitable for a quiz format.
Return only the title as a string without any additional text or formatting.
        """

        # Enhance the prompt with personalization if userId is provided
        if userId:
            prompt = enhance_prompt_with_personalization(base_prompt, userId)
        else:
            prompt = base_prompt

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    "response_mime_type": "text/plain"
                }
            )

            if response.text is None:
                print("❌ No text received from Gemini for title generation.")
                return "Untitled Quiz"

            return response.text.strip()

        except Exception as e:
            print("❌ Title generation error:", e)
            return "Untitled Quiz"
        
    def _get_quiz_type_instruction(self, quiz_type: str) -> str:
        match quiz_type.lower():
            case 'short':
                return "- Short: Answer should be a concise sentence or phrase."
            case 'truefalse':
                return "- True/False: Statement with correct answer as true or false."
            case 'mcq':
                return "- MCQ: 4 options, correct answer must be specified by index (0-3), only one correct."
            case _:
                return "- Unknown type. Supported types: 'short', 'truefalse', 'mcq'."
