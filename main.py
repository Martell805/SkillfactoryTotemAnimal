import logging
import os

from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.bot_handlers import (
    about_command,
    button_callback,
    contact_command,
    help_command,
    quiz_command,
    start_command,
    text_message,
    unknown_command,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("quiz", "Начать викторину"),
        BotCommand("about", "О программе опеки"),
        BotCommand("contact", "Связаться с зоопарком"),
        BotCommand("help", "Справка"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Команды бота установлены.")


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError(
            "Токен бота не найден. Установите переменную окружения BOT_TOKEN "
            "или создайте файл .env с BOT_TOKEN=<ваш_токен>"
        )

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("contact", contact_command))

    app.add_handler(CallbackQueryHandler(button_callback))

    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    logger.info("Бот запускается...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
