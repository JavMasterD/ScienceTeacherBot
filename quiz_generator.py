
import random

class QuizGenerator:
    def __init__(self, questions_data):
        self.questions_data = questions_data

    def get_random_question(self, chat_id, grade, term):
        key = f"{chat_id}_{grade}_{term}"
        questions = self.questions_data.get(key, [])
        if not questions:
            return None

        # إذا كانت الأسئلة بصيغة string فقط
        if isinstance(questions[0], str):
            return {"question": random.choice(questions), "options": [], "answer": ""}

        return random.choice(questions)
