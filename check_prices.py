#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка цен в базе данных
"""

import sqlite3
import config

conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()

# Получим все товары категории stars
cursor.execute("SELECT product_id, name_uz, name_ru, price FROM products WHERE category = 'stars'")
stars_products = cursor.fetchall()

print("=== Товары Stars в базе данных ===")
for product_id, name_uz, name_ru, price in stars_products:
    print(f"{name_uz} / {name_ru}: {price:,} сум")
    
    # Рассчитаем цену за 1 star
    import re
    match = re.search(r'(\d+)\s*Stars', name_uz)
    if match:
        quantity = int(match.group(1))
        if quantity > 0:
            price_per_star = price / quantity
            print(f"  Цена за 1 star: {price_per_star:.0f} сум")
    
    print()

conn.close()

# Проверим config.py
print("\n=== Цены в config.py ===")
print(f"STAR_50: {config.STAR_50:,} сум")
print(f"STAR_100: {config.STAR_100:,} сум")
print(f"STAR_500: {config.STAR_500:,} сум")
print(f"STAR_1000: {config.STAR_1000:,} сум")