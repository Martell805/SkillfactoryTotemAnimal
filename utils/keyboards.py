from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def make_answer_keyboard(options: list[str], q_index: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"ans_{q_index}_{i}")]
        for i, opt in enumerate(options)
    ]
    return InlineKeyboardMarkup(buttons)


def make_result_keyboard(animal_key: str, user_name: str) -> InlineKeyboardMarkup:
    share_text = (
        f"Моё тотемное животное в Московском зоопарке — {animal_key.replace('_', ' ')}! "
        f"Узнай своё: https://t.me/MosZooQuizBot"
    )
    share_url = f"https://t.me/share/url?url=https://t.me/MosZooQuizBot&text={share_text}"

    buttons = [
        [InlineKeyboardButton("🐾 Узнать о программе опеки", callback_data="guardianship")],
        [InlineKeyboardButton("📤 Поделиться результатом", url=share_url)],
        [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="contact")],
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="restart")],
        [InlineKeyboardButton("⭐ Оставить отзыв", callback_data="feedback")],
    ]
    return InlineKeyboardMarkup(buttons)


def make_after_guardianship_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            "🌐 Перейти на сайт зоопарка",
            url="https://moscowzoo.ru/my-zoo/become-a-guardian/"
        )],
        [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="contact")],
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="restart")],
    ]
    return InlineKeyboardMarkup(buttons)


def make_feedback_keyboard() -> InlineKeyboardMarkup:
    ratings = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    buttons = [[InlineKeyboardButton(r, callback_data=f"rate_{i+1}")] for i, r in enumerate(ratings)]
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_result")])
    return InlineKeyboardMarkup(buttons)


def make_start_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🚀 Начать викторину!", callback_data="start_quiz")],
        [InlineKeyboardButton("ℹ️ О программе опеки", callback_data="guardianship_intro")],
    ]
    return InlineKeyboardMarkup(buttons)


def make_contact_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📧 Написать на email", url="mailto:zooclub@moscowzoo.ru")],
        [InlineKeyboardButton("🌐 Сайт зоопарка", url="https://moscowzoo.ru/my-zoo/become-a-guardian/")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_result")],
    ]
    return InlineKeyboardMarkup(buttons)
