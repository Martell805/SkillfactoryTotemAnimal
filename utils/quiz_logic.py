import logging
from data.quiz_data import QUESTIONS, ANIMALS

logger = logging.getLogger(__name__)


def calculate_result(answers: list[int]) -> str:
    scores: dict[str, int] = {animal: 0 for animal in ANIMALS}

    for q_index, answer_index in enumerate(answers):
        if q_index >= len(QUESTIONS):
            break
        question = QUESTIONS[q_index]
        if answer_index < len(question["options"]):
            option = question["options"][answer_index]
            for animal, points in option["scores"].items():
                scores[animal] = scores.get(animal, 0) + points

    winner = max(scores, key=lambda k: scores[k])
    logger.info("Quiz scores: %s | Winner: %s", scores, winner)
    return winner


def get_result_message(animal_key: str) -> str:
    animal = ANIMALS[animal_key]
    return (
        f"{animal['emoji']} *Ваше тотемное животное — {animal['name']}!*\n\n"
        f"{animal['description']}\n\n"
        f"{animal['fun_fact']}"
    )


def get_question_text(q_index: int) -> str:
    question = QUESTIONS[q_index]
    total = len(QUESTIONS)
    return f"*Вопрос {q_index + 1} из {total}*\n\n{question['text']}"


def get_question_options(q_index: int) -> list[str]:
    return [opt["text"] for opt in QUESTIONS[q_index]["options"]]


def total_questions() -> int:
    return len(QUESTIONS)
