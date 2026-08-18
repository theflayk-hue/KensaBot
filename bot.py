from telegram import Update, ReplyParameters
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN


CHAT_LINK = "https://t.me/+QUiA6NSQSvJhMWYy"

RULES = """📜 ПРАВИЛА ЧАТА

😀 Будьте дружелюбны и уважайте друг друга.

🚫 Не спамьте и не оскорбляйте участников.

🔞 Маты и контент 18+ запрещены.

📢 Любая реклама запрещена.

⚠️ Не распространяйте личную информацию других людей.

💬 Чат:
https://t.me/+QUiA6NSQSvJhMWYy
"""


# =========================================================
# ПОСТЫ КАНАЛА
# =========================================================

async def channel_post(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    post = update.channel_post

    if not post:
        return

    # Запоминаем текст для конкретного поста
    pending = context.application.bot_data.setdefault(
        "posts",
        {}
    )

    pending[post.message_id] = RULES

    print(
        f"📢 Новый пост в канале: {post.message_id}"
    )


# =========================================================
# АВТОМАТИЧЕСКИЙ ПОСТ В ГРУППЕ ОБСУЖДЕНИЙ
# =========================================================

async def discussion_post(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.message

    if not message:
        return

    # Это должно быть автоматическое сообщение
    # поста канала в связанной группе.
    if not message.is_automatic_forward:
        return

    if not message.forward_origin:
        return

    # ID оригинального поста канала
    original_post_id = getattr(
        message.forward_origin,
        "message_id",
        None,
    )

    if original_post_id is None:
        return

    pending = context.application.bot_data.get(
        "posts",
        {}
    )

    text = pending.get(original_post_id)

    if not text:
        print(
            "⚠️ Не найден пост:",
            original_post_id,
        )
        return

    try:

        # Отвечаем непосредственно на сообщение поста
        # в группе обсуждений.
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            disable_web_page_preview=True,
            reply_parameters=ReplyParameters(
                message_id=message.message_id,
            ),
        )

        print(
            f"✅ Правила добавлены к посту "
            f"{original_post_id}"
        )

        del pending[original_post_id]

    except Exception as error:

        print(
            "❌ Ошибка отправки правил:",
            error,
        )


# =========================================================
# ЗАПУСК
# =========================================================

def main():

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Получаем новые посты канала
    app.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            channel_post,
        )
    )

    # Получаем автоматическую копию поста
    # в связанной группе обсуждений
    app.add_handler(
        MessageHandler(
            filters.ALL,
            discussion_post,
        )
    )

    print("==============================")
    print("   KENSA RULES BOT ЗАПУЩЕН")
    print("==============================")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()