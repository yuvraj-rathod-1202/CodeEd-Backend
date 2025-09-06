import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.models.BaseModel.generateQuestionsBaseModel import Question
import json
from dotenv import load_dotenv
import openai

load_dotenv()                             
openai.api_key = os.getenv("OPENAI_API_KEY")


class GetQuestions:
    """
    Generates question-answer pairs from a passage of text, using OpenAI Chat Completion.
    """

    MODEL_NAME = "gpt-4.1"

    def get_questions(self, text: str, numbers: int = 5) -> list[Question]:
        """
        Generates `numbers` question-answer pairs from `text` and returns them
        as a list[Question].  If the answer is multiple-choice, the correct
        option should be first in the list, matching your original spec.
        """
        
        prompt = (
            f"Generate {numbers} question-answer pairs from the text below. "
            "If a question is multiple-choice, include the correct option first. "
            "Respond ONLY with JSON having a single top-level key `qa_pairs`, "
            "whose value is an array of objects with fields `question` and `answer`."
            "\n\nTEXT:\n"
            f"{text}"
        )

        
        try:
            completion = openai.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
            
                response_format={"type": "json_object"},
            
                temperature=0.7,
            )

            
            content = completion.choices[0].message.content

            if content is not None:
                raw: list[dict] = json.loads(content)["qa_pairs"]
            else:
                raw = []
            return [Question(**qa) for qa in raw]

        except Exception as err:
            print("Generation error:", err)
            return []


if __name__ == "__main__":
    passage = (
        "The heart is a muscular organ that pumps blood throughout the body. "
        "It has four chambers: two atria and two ventricles. Blood flows "
        "through the heart in a specific sequence, starting in the right "
        "atrium and ending in the aorta."
    )

    generator = GetQuestions()
    qa_pairs = generator.get_questions(passage, numbers=3)

    # for qa in qa_pairs:
    #     print(f"Q: {qa.question}")
    #     print(f"A: {qa.answer}\n")
