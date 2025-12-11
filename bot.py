import os
import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # стандартная библиотека Python 3.9+

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ------------------ НАСТРОЙКИ ------------------

# 1) Токен бота берём из переменной окружения TELEGRAM_BOT_TOKEN
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 2) Время события (ПРИМЕР!)
#   ЗАМЕНИ на нужную тебе дату/время
#   Формат: год, месяц, день, час, минута, секунда
#   Часовой пояс здесь Europe/Berlin — можешь поменять при желании.
TARGET_DATETIME = datetime(
    2025, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("Europe/Berlin")
)

# 3) Фраза, когда событие уже наступило
EVENT_PASSED_TEXT = (
    "🏔️ Время вышло — значит, пора в дорогу! "
    "Счастливого пути, мягкого снега, тёплой сауны и минимум падений 🙌"
)

# 4) Набор цитат про поездку (можешь редактировать / дополнять)
QUOTES = [
    "🏂 «Каждый день ожидания — это ещё один виртуальный спуск в голове. Главное, чтобы в реале ты так же красиво ехал.»",
    "🎿 «Пора бы уже чемодан собрать… хотя бы мысленно. Носки — влево, сноуборд — в сердце.»",
    "🏔 «Где-то в Австрии уже подготавливают склон специально под твой эпичный падёж.»",
    "🔥 «Сначала ты горишь желанием поехать, потом — ноги на склоне, а потом — в сауне.»",
    "🍻 «Главное в горнолыжном отдыхе — держать баланс: днём на доске, вечером между сауной и глинтвейном.»",
]

# ------------------ ЛОГИ ------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ------------------ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ------------------

def main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с одной кнопкой."""
    buttons = [
        [
            InlineKeyboardButton(
                "⏳ нажми меня", callback_data="countdown"
            )
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def get_countdown_text() -> str:
    """Формирует текст с обратным отсчётом до события."""
    now = datetime.now(ZoneInfo("Europe/Berlin"))

    delta: timedelta = TARGET_DATETIME - now
    total_seconds = int(delta.total_seconds())

    if total_seconds <= 0:
        # Событие уже наступило
        return EVENT_PASSED_TEXT

    days = delta.days
    remaining_seconds = total_seconds - days * 24 * 3600
    hours = remaining_seconds // 3600
    remaining_seconds %= 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    parts = []
    if days:
        parts.append(f"{days} дн.")
    if hours or days:
        parts.append(f"{hours} ч.")
    if minutes or hours or days:
        parts.append(f"{minutes} мин.")
    parts.append(f"{seconds} сек.")

    countdown_str = " ".join(parts)

    return (
        "⏳ До поездки осталось:\n"
        f"{countdown_str}\n\n"
        f"Дата выезда: {TARGET_DATETIME.strftime('%d.%m.%Y %H:%M:%S')} "
        f"(Europe/Berlin)"
    )


def get_random_quote() -> str:
    """Возвращает случайную цитату про поездку."""
    return random.choice(QUOTES)


# ------------------ HANDLERS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    text = (
        "Привет! Я бот-таймер ⏳\n\n"
        "Жмякни кнопку ниже, чтобы узнать, сколько осталось до поездки."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_keyboard())
    else:
        await update.effective_chat.send_message(
            text, reply_markup=main_keyboard()
        )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    text = (
        "Я показываю, сколько осталось до поездки.\n\n"
        "Просто нажми кнопку под сообщением."
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопку."""
    query = update.callback_query
    await query.answer()  # убрать "часики" у кнопки

    if query.data == "countdown":
        countdown_text = get_countdown_text()
        quote_text = get_random_quote()

        # Сначала отправляем оставшееся время
        await query.message.reply_text(countdown_text)
        # Потом отдельным сообщением — цитату
        await query.message.reply_text(quote_text, reply_markup=main_keyboard())
    else:
        await query.message.reply_text(
            "Что-то пошло не так, но ты можешь попробовать ещё раз 🙂",
            reply_markup=main_keyboard(),
        )


# ------------------ MAIN ------------------

def main():
    if not TOKEN:
        raise RuntimeError(
            "Не найден токен! Установи переменную окружения TELEGRAM_BOT_TOKEN"
        )

    application = ApplicationBuilder().token(TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))

    # Нажатия на кнопку
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Бот запускается...")
    application.run_polling()


if __name__ == "__main__":
    main()
