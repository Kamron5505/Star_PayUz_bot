# -*- coding: utf-8 -*-
"""
Переводы для бота Star_payuz с обычными эмодзи
Используем только обычные эмодзи, так как премиум эмодзи не работают с новым ботом
"""

# Базовые переводы с обычными эмодзи
BASE_TRANSLATIONS = {
    "uz": {
        "welcome": "👋 Привет, {name}!\n\n🌟 Добро пожаловать в Star_payuz!\n\n💎 <b>Premium услуги</b> - По самым низким ценам!\n\n⚡ <b>Быстрая доставка</b> - 5-30 минут\n✅ <b>Надежный сервис</b> - Поддержка 24/7\n🔥 <b>Лучшие цены</b> - Самые низкие на рынке!\n\n👇 Выберите услугу и оформите заказ!",
        "welcome_subscribed": "👋 Привет, {name}!\n\n🌟 Добро пожаловать в Star_payuz!\n\n💎 <b>Premium услуги</b> - По самым низким ценам!\n\n⚡ <b>Быстрая доставка</b> - 5-30 минут\n✅ <b>Надежный сервис</b> - Поддержка 24/7\n🔥 <b>Лучшие цены</b> - Самые низкие на рынке!\n\n👇 Выберите услугу и оформите заказ!",
        "not_subscribed": "⚠️ Вы не подписаны на канал!",
        "service_selected": "✅ Вы выбрали: {service}\n\n💰 Цена: {price:,} UZS\n\n👇 Выберите способ оплаты:",
        "back_menu": "◀️ Главное меню",
        "help_button": "ℹ️ Помощь",
        "contact_button": "📞 Связаться",
        "stats_button": "📊 Статистика",
        "language_changed": "✅ Язык изменен!",
        "choose_language": "🌐 Выберите язык:",
        "nft_gift_buy": "🎁 Купить NFT gift",
        "nft_gift_market": "🎁 NFT gift маркет",
        "stars_buy": "🌟 Купить Stars",
        "stars_sell": "🌟 Продать Stars",
        "premium_buy": "💎 Купить Premium",
        "robux": "🎮 Robux",
        "virtual_number": "📱 Виртуальный номер",
        "statistics": "📊 <b>Статистика бота:</b>\n\n👥 <b>Всего пользователей:</b> {count}"
    },
    "ru": {
        "welcome": "👋 Привет, {name}!\n\n🌟 Добро пожаловать в Star_payuz!\n\n💎 <b>Premium услуги</b> - По самым низким ценам!\n\n⚡ <b>Быстрая доставка</b> - 5-30 минут\n✅ <b>Надежный сервис</b> - Поддержка 24/7\n🔥 <b>Лучшие цены</b> - Самые низкие на рынке!\n\n👇 Выберите услугу и оформите заказ!",
        "welcome_subscribed": "👋 Привет, {name}!\n\n🌟 Добро пожаловать в Star_payuz!\n\n💎 <b>Premium услуги</b> - По самым низким ценам!\n\n⚡ <b>Быстрая доставка</b> - 5-30 минут\n✅ <b>Надежный сервис</b> - Поддержка 24/7\n🔥 <b>Лучшие цены</b> - Самые низкие на рынке!\n\n👇 Выберите услугу и оформите заказ!",
        "not_subscribed": "⚠️ Вы не подписаны на канал!",
        "service_selected": "✅ Вы выбрали: {service}\n\n💰 Цена: {price:,} UZS\n\n👇 Выберите способ оплаты:",
        "back_menu": "◀️ Главное меню",
        "help_button": "ℹ️ Помощь",
        "contact_button": "📞 Связаться",
        "stats_button": "📊 Статистика",
        "language_changed": "✅ Язык изменен!",
        "choose_language": "🌐 Выберите язык:",
        "nft_gift_buy": "🎁 Купить NFT gift",
        "nft_gift_market": "🎁 NFT gift маркет",
        "stars_buy": "🌟 Купить Stars",
        "stars_sell": "🌟 Продать Stars",
        "premium_buy": "💎 Купить Premium",
        "robux": "🎮 Robux",
        "virtual_number": "📱 Виртуальный номер",
        "statistics": "📊 <b>Статистика бота:</b>\n\n👥 <b>Всего пользователей:</b> {count}"
    }
}

def get_text(lang, key, use_premium=False, **kwargs):
    """Получить перевод с обычными эмодзи (use_premium игнорируется)"""
    text = BASE_TRANSLATIONS.get(lang, BASE_TRANSLATIONS["uz"]).get(key, key)
    
    if kwargs:
        text = text.format(**kwargs)
    
    # Используем только обычные эмодзи
    # Премиум эмодзи не работают с новым ботом
    return text

def get_text_simple(lang, key, **kwargs):
    """Получить простой перевод (без Premium эмодзи) - для кнопок"""
    text = BASE_TRANSLATIONS.get(lang, BASE_TRANSLATIONS["uz"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text