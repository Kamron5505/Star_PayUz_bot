#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация бота Star_payuz с ВСЕМИ ценами
"""

# Токен бота
BOT_TOKEN = "8748508957:AAHiCFJsccw90Z-ZE28NRys4SvSTZ9GxQU0"

# Администраторы
ADMIN_IDS = [8784918764]  # Замени на свой ID
ADMIN_LOGIN = "Kamron5505"
ADMIN_USERNAME = "Kamron5505"  # Для совместимости
ADMIN_PASSWORD = "5505"

# База данных
DATABASE_FILE = "star_payuz.db"
DATABASE_URL = "sqlite:///database.db"

# Каналы для проверки подписки
CHANNEL_UZ = "@Star_payuz"
CHANNEL_RU = "@Star_payuz_otziv"
CHANNEL_ID = -1003595453312  # Числовой ID канала
CHANNEL_URL = "https://t.me/Star_payuz"

# Баннер бота
import os

# Получаем абсолютные пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BANNER_FILE = os.path.join(BASE_DIR, "start.png")
CARD_IMAGE = os.path.join(BASE_DIR, "humo.png")
PREMIUM_VIDEO = os.path.join(BASE_DIR, "premium.png")
STARS_PHOTO = os.path.join(BASE_DIR, "stars.png")

# Реквизиты для оплаты
CARD_NUMBER = "9860 1801 0171 2578"
CARD_OWNER = "ISXAKOVA AZIZA"
CARD_PHONE = "+998 93 582 10 00"
CARD_BOT = "@CardKamron"

# ============================================
# ВСЕ ЦЕНЫ В UZS (Узбекских сумах)
# ============================================

# Telegram Stars (50-1000 stars)
STAR_50 = 13500
STAR_75 = 20250
STAR_100 = 27000
STAR_150 = 40500
STAR_200 = 54000
STAR_250 = 67500
STAR_300 = 81000
STAR_350 = 94500
STAR_400 = 108000
STAR_450 = 121500
STAR_500 = 135000
STAR_550 = 148500
STAR_600 = 162000
STAR_650 = 175500
STAR_700 = 189000
STAR_750 = 202500
STAR_800 = 216000
STAR_900 = 243000
STAR_1000 = 270000

# Telegram Premium
PREMIUM_1_MONTH_ACCOUNT = 47000          # 1 месяц (с аккаунтом)
PREMIUM_12_MONTHS_ACCOUNT = 290000       # 12 месяцев (с аккаунтом)
PREMIUM_3_MONTHS_NO_ACCOUNT = 175000     # 3 месяца (без аккаунта)
PREMIUM_6_MONTHS_NO_ACCOUNT = 235000     # 6 месяцев (без аккаунта)
PREMIUM_12_MONTHS_NO_ACCOUNT = 395000    # 12 месяцев (без аккаунта)

# Boost (минимальное количество: 10)
BOOST_1_DAY = 1000        # за 1 штуку
BOOST_7_DAYS = 3000       # за 1 штуку
BOOST_15_DAYS = 5000      # за 1 штуку
BOOST_30_DAYS = 10000     # за 1 штуку
BOOST_60_DAYS = 15000     # за 1 штуку
BOOST_90_DAYS = 25000     # за 1 штуку
BOOST_MIN_QUANTITY = 10   # минимальное количество

# Telegram Gifts
# 15 stars подарки
GIFT_15_STARS_1 = 4000    # 💝 | 15 ⭐️
GIFT_15_STARS_2 = 4000    # 🧸 | 15 ⭐️

# 25 stars подарки
GIFT_25_STARS_1 = 6000    # 🎁 | 25 ⭐️
GIFT_25_STARS_2 = 6000    # 🌹 | 25 ⭐️

# 50 stars подарки
GIFT_50_STARS_1 = 13000   # 🎂 | 50 ⭐️
GIFT_50_STARS_2 = 13000   # 🚀 | 50 ⭐️
GIFT_50_STARS_3 = 13000   # 🍾 | 50 ⭐️
GIFT_50_STARS_4 = 13000   # 💐 | 50 ⭐️

# 100 stars подарки
GIFT_100_STARS_1 = 22000  # 💎 | 100 ⭐️
GIFT_100_STARS_2 = 22000  # 🏆 | 100 ⭐️
GIFT_100_STARS_3 = 22000  # 💍 | 100 ⭐️

# Старые переменные для совместимости
GIFT_15_STARS = GIFT_15_STARS_1
GIFT_25_STARS = GIFT_25_STARS_1
GIFT_50_STARS = GIFT_50_STARS_1
GIFT_100_STARS = GIFT_100_STARS_1

# Virtual Numbers (виртуальные номера)
PHONE_KENYA = 12000       # Кения
PHONE_BANGLADESH = 12500  # Бангладеш
PHONE_PAKISTAN = 16000    # Пакистан
PHONE_USA = 21000         # США
PHONE_UZBEKISTAN = 30000  # Узбекистан
PHONE_TURKEY = 32000      # Турция

# Robux
ROBUX_40 = 11000
ROBUX_80 = 20000
ROBUX_120 = 30000
ROBUX_160 = 40000
ROBUX_200 = 50000
ROBUX_240 = 60000
ROBUX_500 = 80000
ROBUX_1000 = 160000
ROBUX_2000 = 315000
ROBUX_5250 = 710000
ROBUX_11000 = 1400000
ROBUX_24000 = 2800000

# ============================================
# СЛОВАРИ ЦЕН ДЛЯ УДОБСТВА
# ============================================

# Цены Stars в словаре
STARS_PRICES = {
    50: STAR_50,
    75: STAR_75,
    100: STAR_100,
    150: STAR_150,
    200: STAR_200,
    250: STAR_250,
    300: STAR_300,
    350: STAR_350,
    400: STAR_400,
    450: STAR_450,
    500: STAR_500,
    550: STAR_550,
    600: STAR_600,
    650: STAR_650,
    700: STAR_700,
    750: STAR_750,
    800: STAR_800,
    900: STAR_900,
    1000: STAR_1000
}

# Цены Premium в словаре
PREMIUM_PRICES = {
    "1_month_account": PREMIUM_1_MONTH_ACCOUNT,
    "12_months_account": PREMIUM_12_MONTHS_ACCOUNT,
    "3_months_no_account": PREMIUM_3_MONTHS_NO_ACCOUNT,
    "6_months_no_account": PREMIUM_6_MONTHS_NO_ACCOUNT,
    "12_months_no_account": PREMIUM_12_MONTHS_NO_ACCOUNT
}

# Цены Boost в словаре (за 1 штуку)
BOOST_PRICES_PER_UNIT = {
    "1_day": BOOST_1_DAY,
    "7_days": BOOST_7_DAYS,
    "15_days": BOOST_15_DAYS,
    "30_days": BOOST_30_DAYS,
    "60_days": BOOST_60_DAYS,
    "90_days": BOOST_90_DAYS
}

# Цены Gifts в словаре
GIFTS_PRICES = {
    "15_stars_1": GIFT_15_STARS_1,  # 💝
    "15_stars_2": GIFT_15_STARS_2,  # 🧸
    "25_stars_1": GIFT_25_STARS_1,  # 🎁
    "25_stars_2": GIFT_25_STARS_2,  # 🌹
    "50_stars_1": GIFT_50_STARS_1,  # 🎂
    "50_stars_2": GIFT_50_STARS_2,  # 🚀
    "50_stars_3": GIFT_50_STARS_3,  # 🍾
    "50_stars_4": GIFT_50_STARS_4,  # 💐
    "100_stars_1": GIFT_100_STARS_1,  # 💎
    "100_stars_2": GIFT_100_STARS_2,  # 🏆
    "100_stars_3": GIFT_100_STARS_3,  # 💍
}

# Цены Virtual Numbers в словаре
VIRTUAL_NUMBERS_PRICES = {
    "kenya": PHONE_KENYA,
    "bangladesh": PHONE_BANGLADESH,
    "pakistan": PHONE_PAKISTAN,
    "usa": PHONE_USA,
    "uzbekistan": PHONE_UZBEKISTAN,
    "turkey": PHONE_TURKEY
}

# Цены Robux в словаре
ROBUX_PRICES = {
    40: ROBUX_40,
    80: ROBUX_80,
    120: ROBUX_120,
    160: ROBUX_160,
    200: ROBUX_200,
    240: ROBUX_240,
    500: ROBUX_500,
    1000: ROBUX_1000,
    2000: ROBUX_2000,
    5250: ROBUX_5250,
    11000: ROBUX_11000,
    24000: ROBUX_24000
}

# ============================================
# КАТЕГОРИИ ТОВАРОВ
# ============================================

PRODUCT_CATEGORIES = {
    "premium": "💎 Premium",
    "stars": "🌟 Stars", 
    "boost": "⚡️ Boost",
    "gifts": "🎁 Gifts",
    "virtual_numbers": "📱 Virtual numbers",
    "robux": "🎮 Robux"
}

# Старые цены для совместимости
PRICES = {
    "premium_1month": PREMIUM_1_MONTH_ACCOUNT,
    "premium_12month": PREMIUM_12_MONTHS_ACCOUNT,
    "telegram_stars": STAR_100,  # Пример: 100 stars
    "stars_sell": 14000,  # Цена продажи stars (если нужно)
    "nft_gifts": GIFT_50_STARS,  # Пример: 50 stars gift
    "nft_market": 120000,  # Рыночная цена NFT
    "robux": ROBUX_120,  # Пример: 120 robux
    "virtual_numbers": PHONE_KENYA  # Пример: Кения
}

# Способы оплаты
# Оставляем только HUMO карту, как просил пользователь
PAYMENT_METHODS = {
    "humo": "Humo karta"
}

# ============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ЦЕНАМИ
# ============================================

def calculate_stars_price(quantity):
    """Рассчитать цену для произвольного количества stars"""
    if quantity < 50:
        return None  # Минимальное количество 50
    if quantity > 1000:
        return None  # Максимальное количество 1000
    
    # Базовая цена: 270 сум за 1 star
    base_price_per_star = 270
    return quantity * base_price_per_star

def calculate_boost_price(days, quantity):
    """Рассчитать цену для boost"""
    if quantity < BOOST_MIN_QUANTITY:
        return None
    
    boost_prices = {
        1: BOOST_1_DAY,
        7: BOOST_7_DAYS,
        15: BOOST_15_DAYS,
        30: BOOST_30_DAYS,
        60: BOOST_60_DAYS,
        90: BOOST_90_DAYS
    }
    
    price_per_unit = boost_prices.get(days)
    if not price_per_unit:
        return None
    
    return price_per_unit * quantity

def get_price_by_category(category, item_key):
    """Получить цену по категории и ключу товара"""
    price_dicts = {
        "stars": STARS_PRICES,
        "premium": PREMIUM_PRICES,
        "boost": BOOST_PRICES_PER_UNIT,
        "gifts": GIFTS_PRICES,
        "virtual_numbers": VIRTUAL_NUMBERS_PRICES,
        "robux": ROBUX_PRICES
    }
    
    return price_dicts.get(category, {}).get(item_key)

# ============================================
# ИНФОРМАЦИЯ О ЦЕНАХ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
# ============================================

def get_prices_info(lang="ru"):
    """Получить информацию о ценах на все услуги"""
    if lang == "uz":
        return f"""
💰 <b>Barcha xizmatlar narxlari (UZS):</b>

⭐️ <b>Telegram Stars:</b>
   50 stars - {STAR_50:,} so'm
   100 stars - {STAR_100:,} so'm
   500 stars - {STAR_500:,} so'm
   1000 stars - {STAR_1000:,} so'm

💎 <b>Telegram Premium:</b>
   1 oy (akkaunt orqali) - {PREMIUM_1_MONTH_ACCOUNT:,} so'm
   1 yil (akkaunt orqali) - {PREMIUM_12_MONTHS_ACCOUNT:,} so'm
   3 oy (akkauntsiz) - {PREMIUM_3_MONTHS_NO_ACCOUNT:,} so'm
   12 oy (akkauntsiz) - {PREMIUM_12_MONTHS_NO_ACCOUNT:,} so'm

⚡️ <b>Boost:</b>
   1 kun (10 ta) - {BOOST_1_DAY * BOOST_MIN_QUANTITY:,} so'm
   7 kun (10 ta) - {BOOST_7_DAYS * BOOST_MIN_QUANTITY:,} so'm
   30 kun (10 ta) - {BOOST_30_DAYS * BOOST_MIN_QUANTITY:,} so'm

🎁 <b>Gifts:</b>
   15 ⭐️ sovg'a - {GIFT_15_STARS:,} so'm
   50 ⭐️ sovg'a - {GIFT_50_STARS:,} so'm
   100 ⭐️ sovg'a - {GIFT_100_STARS:,} so'm

📱 <b>Virtual raqamlar:</b>
   Keniya - {PHONE_KENYA:,} so'm
   USA - {PHONE_USA:,} so'm
   O'zbekiston - {PHONE_UZBEKISTAN:,} so'm

🎮 <b>Robux:</b>
   120 Robux - {ROBUX_120:,} so'm
   500 Robux - {ROBUX_500:,} so'm
   1000 Robux - {ROBUX_1000:,} so'm
"""
    else:
        return f"""
💰 <b>Цены на все услуги (UZS):</b>

⭐️ <b>Telegram Stars:</b>
   50 stars - {STAR_50:,} сум
   100 stars - {STAR_100:,} сум
   500 stars - {STAR_500:,} сум
   1000 stars - {STAR_1000:,} сум

💎 <b>Telegram Premium:</b>
   1 месяц (через аккаунт) - {PREMIUM_1_MONTH_ACCOUNT:,} сум
   1 год (через аккаунт) - {PREMIUM_12_MONTHS_ACCOUNT:,} сум
   3 месяца (без аккаунта) - {PREMIUM_3_MONTHS_NO_ACCOUNT:,} сум
   12 месяцев (без аккаунта) - {PREMIUM_12_MONTHS_NO_ACCOUNT:,} сум

⚡️ <b>Boost:</b>
   1 день (10 шт) - {BOOST_1_DAY * BOOST_MIN_QUANTITY:,} сум
   7 дней (10 шт) - {BOOST_7_DAYS * BOOST_MIN_QUANTITY:,} сум
   30 дней (10 шт) - {BOOST_30_DAYS * BOOST_MIN_QUANTITY:,} сум

🎁 <b>Gifts:</b>
   15 ⭐️ подарок - {GIFT_15_STARS:,} сум
   50 ⭐️ подарок - {GIFT_50_STARS:,} сум
   100 ⭐️ подарок - {GIFT_100_STARS:,} сум

📱 <b>Виртуальные номера:</b>
   Кения - {PHONE_KENYA:,} сум
   США - {PHONE_USA:,} сум
   Узбекистан - {PHONE_UZBEKISTAN:,} сум

🎮 <b>Robux:</b>
   120 Robux - {ROBUX_120:,} сум
   500 Robux - {ROBUX_500:,} сум
   1000 Robux - {ROBUX_1000:,} сум
"""
