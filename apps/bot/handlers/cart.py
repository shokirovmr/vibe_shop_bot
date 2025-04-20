from telebot import TeleBot
from telebot.types import Message, KeyboardButton, ReplyKeyboardMarkup
from django.utils.translation import activate, gettext as _

from apps.bot.utils.language import set_language_code
from apps.bot.keyboard import get_main_buttons
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.users import BotUsers


def handle_cart(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    user = BotUsers.objects.get(telegram_id=message.from_user.id)
    cart = Cart.objects.filter(user=user).first()
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        bot.send_message(message.chat.id, _("🛒 Your cart is empty."), reply_markup=get_main_buttons())
        return

    text = _("🛒 Your Cart:\n")
    for item in cart_items:
        text += f"{item.product.title} - {item.quantity} x {item.product.price} = {item.quantity * item.product.price}\n"
    text += f"Total={cart.amount}"

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(_("Order")))
    keyboard.add(KeyboardButton(_("Clear")))
    keyboard.add(KeyboardButton(_("Home")))

    bot.send_message(message.chat.id, text, reply_markup=keyboard)


def handle_clear(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    user = BotUsers.objects.get(telegram_id=message.from_user.id)
    cart = Cart.objects.filter(user=user).first()
    cart.delete()
    bot.send_message(message.chat.id, _("🛒 Your cart has been cleared."), reply_markup=get_main_buttons())
    return