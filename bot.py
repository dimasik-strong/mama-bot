import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Получаем ключи из переменных окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Используем get для безопасности
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")   # например: @annapushok_recipes
PDF_PATH = os.environ.get("PDF_PATH", "novogodnee_menyu_PDF.pdf")  # По умолчанию 'recipes.pdf'

BTN_CHECK = "check_sub"

def kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("Проверить подписку", callback_data=BTN_CHECK)],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Чтобы получить сборник рецептов:\n"
        "1) Подпишитесь на канал\n"
        "2) Нажмите «Проверить подписку»\n\n"
        "После подтверждения я отправлю файл.",
        reply_markup=kb()
    )

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()

    user_id = q.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        status = getattr(member, "status", None)

        if status in ("member", "administrator", "creator", "owner"):
            await q.edit_message_text("Подписка подтверждена. Отправляю сборник…")
            # Безопасное открытие файла
            with open(PDF_PATH, "rb") as document:
                await context.bot.send_document(chat_id=user_id, document=document)
        else:
            await q.edit_message_text(
                "Похоже, вы ещё не подписались. Подпишитесь и нажмите «Проверить подписку» ещё раз.",
                reply_markup=kb()
            )
    except Exception:
        await q.edit_message_text(
            "Не смог проверить подписку автоматически.\n"
            "Проверьте, что бот добавлен в канал администратором и канал указан верно.",
            reply_markup=kb()
        )

def main() -> None:
    # ✅ ВАЖНО: Проверка наличия обязательных ключей
    if not TELEGRAM_TOKEN:
        print("ОШИБКА: Не найден TELEGRAM_TOKEN. Укажите его в секретах GitHub.")
        return
    if not CHANNEL_USERNAME:
        print("ОШИБКА: Не найден CHANNEL_USERNAME. Укажите его в секретах GitHub.")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_sub, pattern=f"^{BTN_CHECK}$"))
    app.run_polling()

# ✅ ВАЖНО: Исправленная строка запуска (была ошибка)
if __name__ == "__main__":
    main()