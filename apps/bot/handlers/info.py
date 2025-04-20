from django.utils.translation import activate, gettext as _
from telebot import TeleBot, types
from telebot.types import Message, CallbackQuery

from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.shop.models.info import Info


def handle_info(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected info.")
    infos = Info.objects.filter(is_active=True)
    for info in infos:
        bot.send_message(
            message.chat.id,
            f"{info.title}\n\n{info.description}",
            parse_mode="Markdown",
        )
