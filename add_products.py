#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление товаров в базу данных
"""

import sqlite3
import config
from datetime import datetime

def add_products():
    """Добавить товары в базу данных"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    # Очистим старые товары (если есть)
    cursor.execute('DELETE FROM products')
    print("✅ Старые товары удалены")
    
    # Товары для категории Stars
    stars_products = [
        # (category, name_uz, name_ru, description_uz, description_ru, price)
        ("stars", "50 Stars", "50 Stars", "50 Telegram Stars", "50 Telegram Stars", 16000),
        ("stars", "75 Stars", "75 Stars", "75 Telegram Stars", "75 Telegram Stars", 22000),
        ("stars", "100 Stars", "100 Stars", "100 Telegram Stars", "100 Telegram Stars", 32000),
        ("stars", "200 Stars", "200 Stars", "200 Telegram Stars", "200 Telegram Stars", 64000),
        ("stars", "500 Stars", "500 Stars", "500 Telegram Stars", "500 Telegram Stars", 160000),
        ("stars", "1000 Stars", "1000 Stars", "1000 Telegram Stars", "1000 Telegram Stars", 230000),
    ]
    
    # Товары для категории Premium
    premium_products = [
        ("premium", "Premium 1 oy (akkaunt)", "Premium 1 месяц (аккаунт)", 
         "Telegram Premium 1 oy - akkaunt orqali", "Telegram Premium 1 месяц - через аккаунт", 50000),
        ("premium", "Premium 12 oy (akkaunt)", "Premium 12 месяцев (аккаунт)", 
         "Telegram Premium 12 oy - akkaunt orqali", "Telegram Premium 12 месяцев - через аккаунт", 290000),
        ("premium", "Premium 3 oy (akkauntsiz)", "Premium 3 месяца (без аккаунта)", 
         "Telegram Premium 3 oy - gift qilib jo'natiladi", "Telegram Premium 3 месяца - отправляется как подарок", 175000),
        ("premium", "Premium 6 oy (akkauntsiz)", "Premium 6 месяцев (без аккаунта)", 
         "Telegram Premium 6 oy - gift qilib jo'natiladi", "Telegram Premium 6 месяцев - отправляется как подарок", 235000),
        ("premium", "Premium 12 oy (akkauntsiz)", "Premium 12 месяцев (без аккаунта)", 
         "Telegram Premium 12 oy - gift qilib jo'natiladi", "Telegram Premium 12 месяцев - отправляется как подарок", 395000),
    ]
    
    # Товары для категории Boost
    boost_products = [
        ("boost", "Boost 1 kun", "Boost 1 день", 
         "Kanal uchun boost - 1 kun", "Буст для канала - 1 день", 1000),
        ("boost", "Boost 7 kun", "Boost 7 дней", 
         "Kanal uchun boost - 7 kun", "Буст для канала - 7 дней", 3000),
        ("boost", "Boost 15 kun", "Boost 15 дней", 
         "Kanal uchun boost - 15 kun", "Буст для канала - 15 дней", 5000),
        ("boost", "Boost 30 kun", "Boost 30 дней", 
         "Kanal uchun boost - 30 kun", "Буст для канала - 30 дней", 10000),
        ("boost", "Boost 60 kun", "Boost 60 дней", 
         "Kanal uchun boost - 60 kun", "Буст для канала - 60 дней", 15000),
        ("boost", "Boost 90 kun", "Boost 90 дней", 
         "Kanal uchun boost - 90 kun", "Буст для канала - 90 дней", 25000),
    ]
    
    # Товары для категории Gifts
    gifts_products = [
        ("gifts", "15 Stars Gift", "15 Stars Gift", 
         "15 Stars sovg'a", "15 Stars подарок", 5000),
        ("gifts", "25 Stars Gift", "25 Stars Gift", 
         "25 Stars sovg'a", "25 Stars подарок", 7000),
        ("gifts", "50 Stars Gift", "50 Stars Gift", 
         "50 Stars sovg'a", "50 Stars подарок", 15000),
        ("gifts", "100 Stars Gift", "100 Stars Gift", 
         "100 Stars sovg'a", "100 Stars подарок", 25000),
    ]
    
    # Товары для категории Virtual Numbers
    virtual_numbers_products = [
        ("virtual_numbers", "Virtual raqam 1 oy", "Виртуальный номер 1 месяц", 
         "Virtual telefon raqami - 1 oy", "Виртуальный телефонный номер - 1 месяц", 50000),
        ("virtual_numbers", "Virtual raqam 3 oy", "Виртуальный номер 3 месяца", 
         "Virtual telefon raqami - 3 oy", "Виртуальный телефонный номер - 3 месяца", 120000),
        ("virtual_numbers", "Virtual raqam 6 oy", "Виртуальный номер 6 месяцев", 
         "Virtual telefon raqami - 6 oy", "Виртуальный телефонный номер - 6 месяцев", 200000),
    ]
    
    # Товары для категории Robux
    robux_products = [
        ("robux", "400 Robux", "400 Robux", 
         "Roblox uchun 400 Robux", "400 Robux для Roblox", 50000),
        ("robux", "800 Robux", "800 Robux", 
         "Roblox uchun 800 Robux", "800 Robux для Roblox", 90000),
        ("robux", "1200 Robux", "1200 Robux", 
         "Roblox uchun 1200 Robux", "1200 Robux для Roblox", 130000),
        ("robux", "2000 Robux", "2000 Robux", 
         "Roblox uchun 2000 Robux", "2000 Robux для Roblox", 200000),
    ]
    
    # Объединяем все товары
    all_products = (stars_products + premium_products + boost_products + 
                   gifts_products + virtual_numbers_products + robux_products)
    
    # Добавляем товары
    for product in all_products:
        category, name_uz, name_ru, desc_uz, desc_ru, price = product
        cursor.execute('''
            INSERT INTO products (category, name_uz, name_ru, description_uz, description_ru, price, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, name_uz, name_ru, desc_uz, desc_ru, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    
    # Проверим сколько добавили
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
    # Покажем по категориям
    cursor.execute('SELECT category, COUNT(*) FROM products GROUP BY category')
    categories = cursor.fetchall()
    
    print(f"\n✅ Добавлено товаров: {count}")
    print("\n📊 По категориям:")
    for category, cat_count in categories:
        print(f"  {category}: {cat_count} товаров")
    
    conn.close()
    return count

if __name__ == "__main__":
    print("🛒 Добавление товаров в базу данных...")
    count = add_products()
    print(f"\n🎉 Готово! Добавлено {count} товаров.")