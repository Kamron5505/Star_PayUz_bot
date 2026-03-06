# -*- coding: utf-8 -*-
"""
Инициализация базы данных
"""
import database

# Инициализируем базу данных
database.init_db()
print("✅ База данных инициализирована!")

# Загружаем товары
import load_products
load_products.init_products()