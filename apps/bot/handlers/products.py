from django.db.models import Q
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from django.utils.translation import activate, gettext as _

from apps.bot.handlers.cart import handle_cart
from apps.bot.keyboard import get_main_buttons
from apps.bot.utils import update_or_create_user
from apps.bot.utils.language import set_language_code
from apps.bot.logger import logger
from apps.shop.models.cart import Cart, CartItem
from apps.shop.models.products import Product
from apps.shop.models.category import Category
from apps.shop.models.users import BotUsers


def handle_category(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    logger.info(f"User {message.from_user.id} requested products.")

    categories = Category.objects.filter(is_active=True)
    logger.info(f"Fetched categories: {[category.name for category in categories]}")

    if not categories.exists():
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton(text=_("Home")), KeyboardButton(text=_("Cart")))
    for category in categories:
        keyboard.add(KeyboardButton(text=category.name))

    bot.send_message(message.chat.id, _("Select a category:"), reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_product, bot)


def handle_product(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    category_name = message.text.strip()
    logger.info(f"User {message.from_user.id} selected category: {category_name}")

    if category_name == _("Home"):
        bot.send_message(
            message.chat.id, _("Continue shopping!"), reply_markup=get_main_buttons()
        )
        return

    if category_name == _("Cart"):
        return handle_cart(message, bot)
    products = Product.objects.filter(
        Q(category__name=category_name) | Q(category__name_ru=category_name) | Q(category__name_uz=category_name),
        is_active=True, quantity__gt=0)

    if not products.exists():
        logger.info(f"No products available in category {category_name}.")
        bot.send_message(message.chat.id, _("No products available in this category."))
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton(text=_("Home")), KeyboardButton(text=_("Cart")))
    for product in products:
        logger.info(f"Adding product to keyboard: {product.title}")
        keyboard.add(KeyboardButton(text=product.title))

    bot.send_message(message.chat.id, _("Select a product:"), reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_product_count, bot)


def handle_product_count(message: Message, bot: TeleBot):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )
    logger.info(f"User {message.from_user.id} selected a product count.")

    if message.text == _("Home"):
        bot.send_message(
            message.chat.id, _("Welcome to the bot!"), reply_markup=get_main_buttons()
        )
        return

    if message.text == _("Cart"):
        return handle_cart(message, bot)

    product = Product.objects.filter(
        Q(title_uz=message.text) | Q(title_ru=message.text) | Q(title=message.text),
        quantity__gt=0,
        is_active=True,
    ).first()

    if not product:
        bot.send_message(message.chat.id, _("Product not found."))
        return

    if product.quantity == 0:
        bot.send_message(message.chat.id, _("Product is out of stock."))
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=_("Back")))
    row = []
    max_count = min(product.quantity, 10)
    for count in range(1, max_count + 1):
        row.append(KeyboardButton(text=str(count)))
        if count % 2 == 0:
            keyboard.add(*row)
            row = []

    if row:
        keyboard.add(*row)
    keyboard.add(KeyboardButton(text=_("Home")))

    caption = _("{title}\n\n\t\t{description}\n\nPrice: {price} UZS").format(
        title=product.title, description=product.description, price=product.price
    )

    bot.send_photo(message.chat.id, product.image, caption=caption)

    bot.send_message(
        message.chat.id, _("Please select the quantity:"), reply_markup=keyboard
    )

    bot.register_next_step_handler(
        message, lambda msg: create_cart_item(msg, bot, product)
    )


def create_cart_item(message: Message, bot: TeleBot, product: Product):
    activate(set_language_code(message.from_user.id))
    update_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_active=True,
    )

    if message.text == _("Home"):
        bot.send_message(
            message.chat.id, _("Welcome to the bot!"), reply_markup=get_main_buttons()
        )
        return

    if message.text == _("Back"):
        return handle_category(message, bot, category_name=product.category.name)

    try:
        quantity = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, _("Invalid quantity selected."))
        return

    if quantity <= 0 or quantity > product.quantity:
        bot.send_message(message.chat.id, _("Invalid quantity selected."))
        return

    user = BotUsers.objects.get(telegram_id=message.from_user.id)

    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = quantity
    cart_item.save()
    bot.send_message(message.chat.id, _("Product added to cart."))

    handle_category(message, bot)
