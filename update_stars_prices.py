#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление цен на Stars (1 star = 270 сум вместо 320)
"""

import config

# Новые цены (количество * 270)
new_prices = {
    50: 50 * 270,      # 13,500
    75: 75 * 270,      # 20,250
    100: 100 * 270,    # 27,000
    150: 150 * 270,    # 40,500
    200: 200 * 270,    # 54,000
    250: 250 * 270,    # 67,500
    300: 300 * 270,    # 81,000
    350: 350 * 270,    # 94,500
    400: 400 * 270,    # 108,000
    450: 450 * 270,    # 121,500
    500: 500 * 270,    # 135,000
    550: 550 * 270,    # 148,500
    600: 600 * 270,    # 162,000
    650: 650 * 270,    # 175,500
    700: 700 * 270,    # 189,000
    750: 750 * 270,    # 202,500
    800: 800 * 270,    # 216,000
    900: 900 * 270,    # 243,000
    1000: 1000 * 270,  # 270,000
}

print("=== Обновление цен на Stars ===")
print(f"Старая цена: 1 star = 320 сум")
print(f"Новая цена: 1 star = 270 сум")
print()

# Обновим config.py
with open('config.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Обновим переменные STAR_XX
for quantity, new_price in new_prices.items():
    old_var = f"STAR_{quantity} = "
    new_var = f"STAR_{quantity} = {new_price}"
    
    # Найдем и заменим
    import re
    pattern = re.compile(f'STAR_{quantity} = \\d+')
    if pattern.search(content):
        content = pattern.sub(new_var, content)
        print(f"✅ STAR_{quantity}: {new_price:,} сум")
    else:
        print(f"⚠️ STAR_{quantity} не найден")

# Сохраним обновленный config.py
with open('config.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ config.py обновлен!")

# Теперь обновим цены в базе данных
print("\n=== Обновление цен в базе данных ===")
import sqlite3

conn = sqlite3.connect('star_payuz.db')
cursor = conn.cursor()

# Получим все товары категории stars
cursor.execute("SELECT product_id, name_uz, price FROM products WHERE category = 'stars'")
stars_products = cursor.fetchall()

updated_count = 0
for product_id, name_uz, old_price in stars_products:
    # Извлечем количество из названия
    import re
    match = re.search(r'(\d+)\s*Stars', name_uz)
    if match:
        quantity = int(match.group(1))
        new_price = quantity * 270
        
        # Обновим цену
        cursor.execute("UPDATE products SET price = ? WHERE product_id = ?", (new_price, product_id))
        print(f"✅ {name_uz}: {old_price:,} → {new_price:,} сум")
        updated_count += 1
    else:
        print(f"⚠️ Не могу определить количество для: {name_uz}")

conn.commit()
conn.close()

print(f"\n✅ Обновлено {updated_count} товаров в базе данных")

# Проверим сообщения в коде где указано "320 сум"
print("\n=== Проверка сообщений в коде ===")
import os

code_files = ['bot.py', 'premium_messages.py', 'universal_messages.py']
for file in code_files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if '320' in file_content:
                print(f"⚠️ В файле {file} есть упоминание 320 сум")
                # Найдем строки
                lines = file_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if '320' in line and ('sum' in line.lower() or 'so\'m' in line.lower() or 'сум' in line.lower()):
                        print(f"   Строка {i}: {line.strip()[:80]}...")
            else:
                print(f"✅ В файле {file} нет упоминания 320 сум")

print("\n🎉 Обновление завершено!")