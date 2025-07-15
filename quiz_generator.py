import random

class QuizGenerator:
    def __init__(self, questions_data):
        """
        questions_data: dict
        التنسيق المتوقع:
        {
            "grade_term_key": [
                {"question": "ما هو...", "options": ["أ", "ب", "ج", "د"], "answer": "أ"},
                ...
            ],
            ...
        }
        """
        self.questions_data = questions_data

    def get_random_question(self, chat_id, grade, term):
        key = f"{chat_id}_{grade}_{term}"
        if key not in self.questions_data or not self.questions_data[key]:
            return None
        question_entry = random.choice(self.questions_data[key])
        return question_entry

    def generate_quiz(self, chat_id, grade, term, num_questions=10):
        key = f"{chat_id}_{grade}_{term}"
        if key not in self.questions_data or not self.questions_data[key]:
            return []
        questions_pool = self.questions_data[key][:]
        random.shuffle(questions_pool)
        return questions_pool[:num_questions]
