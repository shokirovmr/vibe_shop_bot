from telebot import TeleBot
from telebot.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from django.utils.translation import activate, gettext as _

from apps.bot.utils.language import set_language_code
from apps.bot.logger import logger
from apps.bot.keyboard import get_main_buttons
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.order import Order, OrderItem
from apps.shop.models.users import BotUsers
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def handle_order(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    logger.info(f"User {message.from_user.id} is going to order.")
    cart = Cart.objects.filter(user__telegram_id=message.from_user.id).first()
    if not cart:
        bot.send_message(message.chat.id, _("🛒 Your cart is empty."), reply_markup=get_main_buttons())
        return

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = KeyboardButton(_("Share Contact"), request_contact=True)
    keyboard.add(button)
    bot.send_message(message.chat.id, _("Please share your contact."), reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_contact, bot, cart)


def handle_contact(message: Message, bot: TeleBot, cart: Cart):
    if not message.contact:
        bot.send_message(message.chat.id, _("Contact not received. Please try again."), reply_markup=get_main_buttons())
        return

    # Ask for location
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = KeyboardButton(_("Share Location"), request_location=True)
    keyboard.add(button)
    bot.send_message(message.chat.id, _("Please share your location."), reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_location, bot, cart, message.contact)


def handle_location(message: Message, bot: TeleBot, cart: Cart, contact):
    if not message.location:
        bot.send_message(message.chat.id, _("Location not received. Please try again."),
                         reply_markup=get_main_buttons())
        return

    user = BotUsers.objects.get(telegram_id=message.from_user.id)
    order = Order.objects.create(
        user=user,
        phone=contact.phone_number,
        longitude = message.location.longitude,
        latitude = message.location.latitude
    )

    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # cart.delete()
    bot.send_message(message.chat.id, _("🛒 Your order has been accepted."), reply_markup=get_main_buttons())


def handle_payment_method(message: Message, bot: TeleBot, cart: Cart, order: Order):
    activate(set_language_code(message.from_user.id))
    logger.info(f"User {message.from_user.id} is going to pay for the order.")
    order_id = order.id
    cart_id = cart.id

    inline_keyboard = InlineKeyboardMarkup()
    inline_button = InlineKeyboardButton(text=_("PayMe"), callback_data=f"payme_{order_id}_{cart_id}")
    inline_keyboard.add(inline_button)

    bot.send_message(message.chat.id, _("Please select a payment method."), reply_markup=inline_keyboard)

def payment_callback_handler(call: CallbackQuery, bot: TeleBot):
    order_id, cart_id = map(int, call.data.split("_")[1:])
    order = Order.objects.get(id=order_id)
    cart = Cart.objects.get(id=cart_id)
    bot.send_message(call.message.chat.id, _("🛒 Your order has been paid."), reply_markup=get_main_buttons())
    order.is_paid = True
    order.save()
    cart.delete()
    bot.answer_callback_query(call.id, _("Payment successful."))