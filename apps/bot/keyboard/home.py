from django.utils.translation import gettext as _
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_buttons():
    buttons = [
        [KeyboardButton(_("Language")), KeyboardButton(_("Cart"))],
        [KeyboardButton(_("Products")), KeyboardButton(_("Info"))],
        [KeyboardButton(_("Donate"))]
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*sum(buttons, []))
    return markup
