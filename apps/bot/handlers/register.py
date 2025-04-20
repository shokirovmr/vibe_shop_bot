from django.utils.translation import activate, gettext as _
from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from apps.bot.handlers.cart import handle_cart, handle_clear
from apps.bot.handlers.info import handle_info
from apps.bot.handlers.language import handle_language, handle_language_selection
from apps.bot.handlers.order import handle_order, payment_callback_handler
from apps.bot.handlers.products import handle_category
from apps.bot.keyboard import get_main_buttons
from apps.bot.logger import logger
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code


def handle_message(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    logger.info(f"Received message: {message.text}")

    if message.text == _("Language") or message.text == "/lang":
        handle_language(message, bot)
    elif message.text == _("Cart"):
        handle_cart(message, bot)
    elif message.text == _("Products"):
        handle_category(message, bot)
    elif message.text == _("Info"):
        handle_info(message, bot)
    elif message.text == _("Clear"):
        handle_clear(message, bot)
    elif message.text == _("Order"):
        handle_order(message, bot)
    elif message.text == _("Donate"):
        ...

    else:
        logger.info(f"User {message.from_user.id} sent an unknown command.")
        bot.send_message(
            message.chat.id, _("Unknown command."), reply_markup=get_main_buttons()
        )
        update_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_active=True,
        )


def handle_callback_query(call: CallbackQuery, bot: TeleBot):
    activate(set_language_code(call.from_user.id))
    logger.info(f"User {call.from_user.id} triggered callback: {call.data}")
    logger.info(f"Received callback query: {call.data}")

    if call.data == "lang_ru" or call.data == "lang_uz":
        handle_language_selection(call, bot)
        logger.info(f"User {call.from_user.id} selected a language.")
    elif call.data.startswith("payme_"):
        payment_callback_handler(call, bot)

    else:
        bot.answer_callback_query(call.id, _("Unknown action."))
        logger.info(f"User {call.from_user.id} performed an unknown action.")
