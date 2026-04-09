# -*- coding: utf-8 -*-
"""
Клавиатуры бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import config

def language_keyboard():
    """Выбор языка"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ]
    ])
    return keyboard

def main_menu(lang="uz"):
    """Главное меню — Bot API 9.4 style + icon_custom_emoji_id"""

    def btn(text, callback_data, style=None, emoji_id=None):
        data = {"text": text, "callback_data": callback_data}
        if style:
            data["style"] = style
        if emoji_id:
            data["icon_custom_emoji_id"] = emoji_id
        return InlineKeyboardButton(**data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [btn("Stars olish",         "category_stars",   style="success", emoji_id="5936259309812846957")],
        [
            btn("Premium olish",    "category_premium", style="primary", emoji_id="5276130429919847610"),
            btn("Gift olish",       "category_gifts",   style="primary", emoji_id="5199749070830197566"),
        ],
        [
            btn("Boost",            "category_boost",   style="default", emoji_id="5460991276948143687"),
            btn("Robux",            "category_robux",   style="default", emoji_id="5456658208997267458"),
        ],
        [
            btn("Balans to'ldirish","statistics",       style="default", emoji_id="5276461636322877553"),
            btn("Profil",           "my_orders",        style="default", emoji_id="6035084557378654059"),
        ],
        [btn("Yordam",             "help",             style="default", emoji_id="5327794604408328596")],
    ])
    return keyboard

def payment_methods():
    """Способы оплаты"""
    # Добавляем премиум-эмодзи к способу оплаты
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"💎 {method_name}",
                    callback_data=f"payment_{method_id}"
                )
            ]
            for method_id, method_name in config.PAYMENT_METHODS.items()
        ]
        + [[InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]]
    )
    return keyboard

def subscription_check(lang="uz"):
    """Проверка подписки"""
    from translations import get_text_simple
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text_simple(lang, "subscribe_button"), url=config.CHANNEL_URL)],
        [InlineKeyboardButton(text=get_text_simple(lang, "check_subscribe"), callback_data="check_subscription")]
    ])
    return keyboard

def admin_menu():
    """Админ панель"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📝 Заказы")],
            [KeyboardButton(text="🗑 Удалить заказы"), KeyboardButton(text="📣 Опубликовать заказ")],
            [KeyboardButton(text="📤 Отзыв юбориш"), KeyboardButto@ismoil_grn(text="📢 Рассылка")],
            [KeyboardButton(text="➕ Товар қўшиш"), KeyboardButton(text="📦 Товарлар рўйхати")],
            [KeyboardButton(text="✏️ Нарх ўзгартириш"), KeyboardButton(text="📢 Канал созлаш")],
            [KeyboardButton(text="2⭐ Звезда нархи"), KeyboardButton(text="◀️ Выход")]
        ],
        resize_keyboard=True
    )
    return keyboard

def order_actions(order_id):
    """Действия с заказом"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}")
        ]
    ])
    return keyboard

def back_to_menu(lang="uz"):
    """Кнопка назад"""
    from translations import get_text_simple
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")]
    ])
    return keyboard

def products_keyboard(products, lang="uz"):
    """Клавиатура с товарами (с ценами на кнопках)"""
    from translations import get_text_simple
    
    buttons = []
    row = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        
        # Выбираем название на нужном языке
        name = name_uz if lang == "uz" else name_ru
        
        # Добавляем цену к названию кнопки
        button_text = f"{name} - {price:,} UZS"
        row.append(InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}"))
        
        # Добавляем по 2 кнопки в ряд
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    # Добавляем последний ряд если он не пустой
    if row:
        buttons.append(row)
    
    # Добавляем кнопку назад
    buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
