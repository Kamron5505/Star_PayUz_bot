#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация бота Star_payuz с ВСЕМИ ценами
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "8748508957:AAHiCFJsccw90Z-ZE28NRys4SvSTZ9GxQU0")

# Администраторы
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "8784918764").split(",")]
ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "Kamron5505")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "5505")

# База данных
# Получаем абсолютный путь к БД
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.getenv("DATABASE_FILE", os.path.join(BASE_DIR, "star_payuz.db"))

# Каналы для проверки подписки
CHANNEL_UZ = os.getenv("CHANNEL_UZ", "@StarPayUzz")
CHANNEL_RU = os.getenv("CHANNEL_RU", "@StarPayUzz")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1003595453312"))
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/StarPayUzz")

# Баннер бота
# Получаем абсолютные пути к файлам
BANNER_FILE = os.path.join(BASE_DIR, "start.png")
PREMIUM_VIDEO = os.path.join(BASE_DIR, "premium.png")
STARS_PHOTO = os.path.join(BASE_DIR, "stars.png")

# Реквизиты для оплаты
CARD_NUMBER = os.getenv("CARD_NUMBER", "9860 1801 0171 2578")
CARD_OWNER = os.getenv("CARD_OWNER", "ISXAKOVA AZIZA")

# ============================================
# ВСЕ ЦЕНЫ В UZS (Узбекских сумах)
# ============================================

# Telegram Stars (50-1000 stars) - 245 сум за 1 star
STAR_50 = 12250
STAR_75 = 18375
STAR_100 = 24500
STAR_150 = 36750
STAR_200 = 49000
STAR_250 = 61250
STAR_300 = 73500
STAR_350 = 85750
STAR_400 = 98000
STAR_450 = 110250
STAR_500 = 122500
STAR_550 = 134750
STAR_600 = 147000
STAR_650 = 159250
STAR_700 = 171500
STAR_750 = 183750
STAR_800 = 196000
STAR_900 = 220500
STAR_1000 = 245000

# Telegram Premium
PREMIUM_1_MONTH_ACCOUNT = 45000          # 1 месяц (с аккаунтом)
PREMIUM_12_MONTHS_ACCOUNT = 290000       # 12 месяцев (с аккаунтом)
PREMIUM_3_MONTHS_NO_ACCOUNT = 160000     # 3 месяца (без аккаунта)
PREMIUM_6_MONTHS_NO_ACCOUNT = 225000     # 6 месяцев (без аккаунта)
PREMIUM_12_MONTHS_NO_ACCOUNT = 370000    # 12 месяцев (без аккаунта)

# Boost (минимальное количество: 10)
BOOST_1_DAY = 1000        # за 1 штуку
BOOST_7_DAYS = 3000       # за 1 штуку
BOOST_15_DAYS = 5000      # за 1 штуку
BOOST_30_DAYS = 10000     # за 1 штуку
BOOST_60_DAYS = 15000     # за 1 штуку
BOOST_90_DAYS = 25000     # за 1 штуку
BOOST_MIN_QUANTITY = 10   # минимальное количество

# Telegram Gifts
# 13 stars подарки
GIFT_15_STARS_1 = 3185    # 💝 | 13 ⭐️
GIFT_15_STARS_2 = 3185    # 🧸 | 13 ⭐️

# 21 stars подарки
GIFT_25_STARS_1 = 5145    # 🎁 | 21 ⭐️
GIFT_25_STARS_2 = 5145    # 🌹 | 21 ⭐️

# 43 stars подарки
GIFT_50_STARS_1 = 10535   # 🎂 | 43 ⭐️
GIFT_50_STARS_2 = 10535   # 🚀 | 43 ⭐️
GIFT_50_STARS_3 = 10535   # 🍾 | 43 ⭐️
GIFT_50_STARS_4 = 10535   # 💐 | 43 ⭐️

# 85 stars подарки
GIFT_100_STARS_1 = 20825  # 💎 | 85 ⭐️
GIFT_100_STARS_2 = 20825  # 🏆 | 85 ⭐️
GIFT_100_STARS_3 = 20825  # 💍 | 85 ⭐️

# Старые переменные для совместимости
GIFT_15_STARS = GIFT_15_STARS_1
GIFT_25_STARS = GIFT_25_STARS_1
GIFT_50_STARS = GIFT_50_STARS_1
GIFT_100_STARS = GIFT_100_STARS_1

# Robux - новые цены
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
    "robux": "🎮 Robux"
}

# Старые цены для совместимости
PRICES = {
    "premium_1month": PREMIUM_1_MONTH_ACCOUNT,
    "telegram_stars": STAR_100,
    "nft_gifts": GIFT_50_STARS,
    "robux": ROBUX_120
}

# Способы оплаты
PAYMENT_METHODS = {
    "humo": "Humo karta"
}
