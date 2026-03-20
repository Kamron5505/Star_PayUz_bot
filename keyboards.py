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
    """Главное меню"""
    from translations import get_text_simple
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Premium", callback_data="category_premium")],
        [InlineKeyboardButton(text="🌟 Stars", callback_data="category_stars")],
        [InlineKeyboardButton(text="⚡️ Boost", callback_data="category_boost")],
        [InlineKeyboardButton(text="🎁 Gifts", callback_data="category_gifts")],
        [InlineKeyboardButton(text="🎮 Robux", callback_data="category_robux")],
        [
            InlineKeyboardButton(text=get_text_simple(lang, "help_button"), callback_data="help"),
            InlineKeyboardButton(text=get_text_simple(lang, "contact_button"), callback_data="contact")
        ],
        [
            InlineKeyboardButton(text=get_text_simple(lang, "stats_button"), callback_data="statistics"),
            InlineKeyboardButton(text="🌐 Язык", callback_data="change_language")
        ],
        [InlineKeyboardButton(text="📋 Buyurtmalarim" if lang == "uz" else "📋 Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton(text="👥 Referal" if lang == "uz" else "👥 Реферал", callback_data="referral")]
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
            [KeyboardButton(text="📤 Отзыв юбориш"), KeyboardButton(text="📢 Рассылка")],
            [KeyboardButton(text="◀️ Выход")]
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
