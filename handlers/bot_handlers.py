import logging
from datetime import datetime

from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from data.quiz_data import ANIMALS, GUARDIANSHIP_INFO, QUESTIONS
from utils.quiz_logic import (
    calculate_result,
    get_result_message,
    get_question_text,
    get_question_options,
    total_questions,
)
from utils.keyboards import (
    make_answer_keyboard,
    make_result_keyboard,
    make_after_guardianship_keyboard,
    make_feedback_keyboard,
    make_start_keyboard,
    make_contact_keyboard,
)

logger = logging.getLogger(__name__)

ANIMAL_IMAGES = {
    "амурский_тигр":  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Amur_Tiger_Panthera_tigris_altaica_Cub_2_Edit.jpg/1280px-Amur_Tiger_Panthera_tigris_altaica_Cub_2_Edit.jpg",
    "снежный_барс":   "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Snow_leopard_portrait.jpg/1280px-Snow_leopard_portrait.jpg",
    "бурый_медведь":  "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/2011_Kluane_Hike_063_%285802555956%29.jpg/1280px-2011_Kluane_Hike_063_%285802555956%29.jpg",
    "волк":           "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/1280px-Collage_of_Nine_Dogs.jpg",
    "дикобраз":       "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Porcupine-BiosphereReserve.jpg/1280px-Porcupine-BiosphereReserve.jpg",
    "фламинго":       "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flamingos_Laguna_Colorada.jpg/1280px-Flamingos_Laguna_Colorada.jpg",
    "сурикат":        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Meerkat_%28Suricata_suricatta%29_Tswalu.jpg/1280px-Meerkat_%28Suricata_suricatta%29_Tswalu.jpg",
    "лев":            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lion_waiting_in_Namibia.jpg/1280px-Lion_waiting_in_Namibia.jpg",
}

feedback_storage: list[dict] = []


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие и главное меню."""
    user = update.effective_user
    context.user_data.clear()

    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Добро пожаловать в *Московский зоопарк* — один из старейших зоопарков Европы!\n\n"
        "🐾 Я помогу вам узнать, какое животное зоопарка — ваше тотемное.\n\n"
        "Пройдите короткую викторину из 8 вопросов и узнайте, кто вы:\n"
        "гордый *Амурский тигр*, общительный *Фламинго* или, может, мудрый *Дикобраз*? 😄\n\n"
        "Готовы? Вперёд!"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=make_start_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "ℹ️ *Как пользоваться ботом:*\n\n"
        "1️⃣ Нажмите «Начать викторину» или введите /quiz\n"
        "2️⃣ Отвечайте на вопросы, нажимая на кнопки\n"
        "3️⃣ Получите своё тотемное животное!\n"
        "4️⃣ Поделитесь результатом с друзьями 🎉\n\n"
        "*Доступные команды:*\n"
        "/start — главное меню\n"
        "/quiz — начать викторину\n"
        "/help — эта справка\n"
        "/about — о программе опеки\n"
        "/contact — связаться с зоопарком\n"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        GUARDIANSHIP_INFO,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=make_after_guardianship_keyboard(),
        disable_web_page_preview=True,
    )


async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📞 *Связаться с Московским зоопарком:*\n\n"
        "📧 Email: zooclub@moscowzoo.ru\n"
        "📱 Телефон: +7 (499) 252-35-80\n"
        "🌐 Сайт: moscowzoo.ru\n\n"
        "Сотрудники зоопарка ответят на все ваши вопросы о программе опеки!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=make_contact_keyboard(),
    )


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запускает викторину напрямую по команде."""
    context.user_data["answers"] = []
    context.user_data["q_index"] = 0
    await _send_question(update.message, context, 0)


async def _send_question(message, context: ContextTypes.DEFAULT_TYPE, q_index: int) -> None:
    text = get_question_text(q_index)
    options = get_question_options(q_index)
    keyboard = make_answer_keyboard(options, q_index)
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    # Начать викторину
    if data in ("start_quiz", "restart"):
        context.user_data["answers"] = []
        context.user_data["q_index"] = 0
        await query.message.reply_text(
            "🎬 Отлично! Начинаем! Отвечайте честно — врать тотему не стоит 😄",
            parse_mode=ParseMode.MARKDOWN,
        )
        await _send_question(query.message, context, 0)
        return

    if data.startswith("ans_"):
        _, q_str, a_str = data.split("_")
        q_index = int(q_str)
        a_index = int(a_str)

        answers: list = context.user_data.setdefault("answers", [])
        if len(answers) != q_index:
            return
        answers.append(a_index)

        next_q = q_index + 1
        if next_q < total_questions():
            context.user_data["q_index"] = next_q
            await _send_question(query.message, context, next_q)
        else:
            await _show_result(query, context)
        return

    if data in ("guardianship", "guardianship_intro"):
        await query.message.reply_text(
            GUARDIANSHIP_INFO,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=make_after_guardianship_keyboard(),
            disable_web_page_preview=True,
        )
        return

    if data == "contact":
        animal_key = context.user_data.get("result_animal", "")
        animal_name = ANIMALS.get(animal_key, {}).get("name", "")
        contact_text = (
            "📞 *Связаться с Московским зоопарком:*\n\n"
            "📧 Email: zooclub@moscowzoo.ru\n"
            "📱 Телефон: +7 (499) 252-35-80\n\n"
        )
        if animal_name:
            contact_text += (
                f"💌 При обращении сотрудник зоопарка уже будет знать, "
                f"что вы интересуетесь опекой над *{animal_name}*!\n\n"
            )
        contact_text += "Мы рады ответить на все ваши вопросы 🐾"
        await query.message.reply_text(
            contact_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=make_contact_keyboard(),
        )
        return

    if data == "feedback":
        await query.message.reply_text(
            "⭐ Насколько вам понравилась викторина?\nВыберите оценку:",
            reply_markup=make_feedback_keyboard(),
        )
        return

    if data.startswith("rate_"):
        rating = int(data.split("_")[1])
        user = query.from_user
        feedback_storage.append({
            "user_id": user.id,
            "username": user.username,
            "rating": rating,
            "animal": context.user_data.get("result_animal", ""),
            "timestamp": datetime.utcnow().isoformat(),
        })
        stars = "⭐" * rating
        await query.message.reply_text(
            f"Спасибо за оценку {stars}!\nВаш отзыв поможет нам сделать бота лучше 🐾",
        )
        return

    if data == "back_to_result":
        animal_key = context.user_data.get("result_animal")
        if animal_key:
            result_text = get_result_message(animal_key)
            await query.message.reply_text(
                result_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=make_result_keyboard(animal_key, query.from_user.first_name),
            )
        return


async def _show_result(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    answers = context.user_data.get("answers", [])
    animal_key = calculate_result(answers)
    context.user_data["result_animal"] = animal_key

    animal = ANIMALS[animal_key]
    result_text = get_result_message(animal_key)
    keyboard = make_result_keyboard(animal_key, query.from_user.first_name)

    # Отправляем изображение животного
    image_url = ANIMAL_IMAGES.get(animal_key)
    try:
        await query.message.reply_photo(
            photo=image_url,
            caption=result_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )
    except Exception as e:
        logger.warning("Не удалось отправить фото: %s. Отправляю текст.", e)
        await query.message.reply_text(
            result_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )

    guardianship_teaser = (
        f"🌿 *Хотите поддержать {animal['name']}?*\n\n"
        f"Стоимость опеки: *{animal['guardianship_price']}*\n"
        "Нажмите кнопку ниже, чтобы узнать о программе опеки 👇"
    )
    await query.message.reply_text(
        guardianship_teaser,
        parse_mode=ParseMode.MARKDOWN,
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Не знаю такой команды 🤔\nНапишите /help, чтобы увидеть список доступных команд.",
    )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Нажмите /start, чтобы начать викторину, или /help для справки 🐾",
    )
