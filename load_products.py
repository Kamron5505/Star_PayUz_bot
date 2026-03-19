#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка товаров в базу данных
"""
import database
import config

def init_products():
    """Инициализировать товары"""
    
    # Проверяем есть ли уже товары
    existing = database.get_all_products()
    if existing and len(existing) > 0:
        print(f"✅ Товары уже загружены ({len(existing)} товаров)")
        return
    
    print("📦 Загружаем товары...")
    
    # Premium товары
    premium_products = [
        ("premium", "1 oy", "1 месяц", 
         "Telegram Premium 1 месяц (с аккаунтом)", "Telegram Premium 1 месяц (с аккаунтом)", 
         config.PREMIUM_1_MONTH_ACCOUNT),
        
        ("premium", "12 oylik", "12 месяцев",
         "Telegram Premium 12 месяцев (с аккаунтом)", "Telegram Premium 12 месяцев (с аккаунтом)",
         config.PREMIUM_12_MONTHS_ACCOUNT),
        
        ("premium", "3 oy", "3 месяца",
         "Telegram Premium 3 месяца (без аккаунта)", "Telegram Premium 3 месяца (без аккаунта)",
         config.PREMIUM_3_MONTHS_NO_ACCOUNT),
        
        ("premium", "6 oy", "6 месяцев",
         "Telegram Premium 6 месяцев (без аккаунта)", "Telegram Premium 6 месяцев (без аккаунта)",
         config.PREMIUM_6_MONTHS_NO_ACCOUNT),
        
        ("premium", "12 oy", "12 месяцев",
         "Telegram Premium 12 месяцев (без аккаунта)", "Telegram Premium 12 месяцев (без аккаунта)",
         config.PREMIUM_12_MONTHS_NO_ACCOUNT),
    ]
    
    # Stars товары
    stars_products = [
        ("stars", "⭐️ 50 Stars", "⭐️ 50 Stars", "50 Telegram Stars", "50 Telegram Stars", config.STAR_50),
        ("stars", "⭐️ 100 Stars", "⭐️ 100 Stars", "100 Telegram Stars", "100 Telegram Stars", config.STAR_100),
        ("stars", "⭐️ 500 Stars", "⭐️ 500 Stars", "500 Telegram Stars", "500 Telegram Stars", config.STAR_500),
        ("stars", "⭐️ 1000 Stars", "⭐️ 1000 Stars", "1000 Telegram Stars", "1000 Telegram Stars", config.STAR_1000),
    ]
    
    # Boost товары
    boost_products = [
        ("boost", "⚡️ 1 kun", "⚡️ 1 день", "Telegram Boost 1 день", "Telegram Boost 1 день", config.BOOST_1_DAY),
        ("boost", "⚡️ 7 kun", "⚡️ 7 дней", "Telegram Boost 7 дней", "Telegram Boost 7 дней", config.BOOST_7_DAYS),
        ("boost", "⚡️ 15 kun", "⚡️ 15 дней", "Telegram Boost 15 дней", "Telegram Boost 15 дней", config.BOOST_15_DAYS),
        ("boost", "⚡️ 30 kun", "⚡️ 30 дней", "Telegram Boost 30 дней", "Telegram Boost 30 дней", config.BOOST_30_DAYS),
        ("boost", "⚡️ 60 kun", "⚡️ 60 дней", "Telegram Boost 60 дней", "Telegram Boost 60 дней", config.BOOST_60_DAYS),
        ("boost", "⚡️ 90 kun", "⚡️ 90 дней", "Telegram Boost 90 дней", "Telegram Boost 90 дней", config.BOOST_90_DAYS),
    ]
    
    # Gifts товары
    gifts_products = [
        ("gifts", "💝 13 ⭐️ – Hadya", "💝 13 ⭐️ – Подарок", "Telegram Gift 13 Stars", "Telegram Gift 13 Stars", config.GIFT_15_STARS_1),
        ("gifts", "🧸 13 ⭐️ – Hadya", "🧸 13 ⭐️ – Подарок", "Telegram Gift 13 Stars", "Telegram Gift 13 Stars", config.GIFT_15_STARS_2),
        ("gifts", "🎁 21 ⭐️ – Hadya", "🎁 21 ⭐️ – Подарок", "Telegram Gift 21 Stars", "Telegram Gift 21 Stars", config.GIFT_25_STARS_1),
        ("gifts", "🌹 21 ⭐️ – Hadya", "🌹 21 ⭐️ – Подарок", "Telegram Gift 21 Stars", "Telegram Gift 21 Stars", config.GIFT_25_STARS_2),
        ("gifts", "🎂 43 ⭐️ – Hadya", "🎂 43 ⭐️ – Подарок", "Telegram Gift 43 Stars", "Telegram Gift 43 Stars", config.GIFT_50_STARS_1),
        ("gifts", "🚀 43 ⭐️ – Hadya", "🚀 43 ⭐️ – Подарок", "Telegram Gift 43 Stars", "Telegram Gift 43 Stars", config.GIFT_50_STARS_2),
        ("gifts", "🍾 43 ⭐️ – Hadya", "🍾 43 ⭐️ – Подарок", "Telegram Gift 43 Stars", "Telegram Gift 43 Stars", config.GIFT_50_STARS_3),
        ("gifts", "💐 43 ⭐️ – Hadya", "💐 43 ⭐️ – Подарок", "Telegram Gift 43 Stars", "Telegram Gift 43 Stars", config.GIFT_50_STARS_4),
        ("gifts", "💎 85 ⭐️ – Hadya", "💎 85 ⭐️ – Подарок", "Telegram Gift 85 Stars", "Telegram Gift 85 Stars", config.GIFT_100_STARS_1),
        ("gifts", "🏆 85 ⭐️ – Hadya", "🏆 85 ⭐️ – Подарок", "Telegram Gift 85 Stars", "Telegram Gift 85 Stars", config.GIFT_100_STARS_2),
        ("gifts", "💍 85 ⭐️ – Hadya", "💍 85 ⭐️ – Подарок", "Telegram Gift 85 Stars", "Telegram Gift 85 Stars", config.GIFT_100_STARS_3),
    ]
    
    # Robux товары - новые цены
    robux_products = [
        ("robux", "💵 40 rbx", "💵 40 rbx", "Roblox 40 Robux", "Roblox 40 Robux", config.ROBUX_40),
        ("robux", "💵 80 rbx", "💵 80 rbx", "Roblox 80 Robux", "Roblox 80 Robux", config.ROBUX_80),
        ("robux", "💵 120 rbx", "💵 120 rbx", "Roblox 120 Robux", "Roblox 120 Robux", config.ROBUX_120),
        ("robux", "💵 160 rbx", "💵 160 rbx", "Roblox 160 Robux", "Roblox 160 Robux", config.ROBUX_160),
        ("robux", "💵 200 rbx", "💵 200 rbx", "Roblox 200 Robux", "Roblox 200 Robux", config.ROBUX_200),
        ("robux", "💵 240 rbx", "💵 240 rbx", "Roblox 240 Robux", "Roblox 240 Robux", config.ROBUX_240),
        ("robux", "💵 500 rbx", "💵 500 rbx", "Roblox 500 Robux", "Roblox 500 Robux", config.ROBUX_500),
        ("robux", "💵 1 000 rbx", "💵 1 000 rbx", "Roblox 1000 Robux", "Roblox 1000 Robux", config.ROBUX_1000),
        ("robux", "💵 2 000 rbx", "💵 2 000 rbx", "Roblox 2000 Robux", "Roblox 2000 Robux", config.ROBUX_2000),
        ("robux", "💵 5 250 rbx", "💵 5 250 rbx", "Roblox 5250 Robux", "Roblox 5250 Robux", config.ROBUX_5250),
        ("robux", "💵 11 000 rbx", "💵 11 000 rbx", "Roblox 11000 Robux", "Roblox 11000 Robux", config.ROBUX_11000),
        ("robux", "💵 24 000 rbx", "💵 24 000 rbx", "Roblox 24000 Robux", "Roblox 24000 Robux", config.ROBUX_24000),
    ]
    
    # Добавляем все товары
    all_products = premium_products + stars_products + boost_products + gifts_products + robux_products
    
    for product in all_products:
        database.add_product(*product)
    
    print(f"✅ Загружено {len(all_products)} товаров!")
    
    # Показываем загруженные товары по категориям
    for category in ["premium", "stars", "boost", "gifts", "robux"]:
        products = database.get_products_by_category(category)
        print(f"\n📦 {category.upper()} ({len(products)} товаров):")
        for product in products:
            product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
            print(f"  {product_id}. {name_uz} - {price:,} UZS")
