#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Очистка базы данных от старых записей
"""

import sqlite3
import config

print("=== Очистка базы данных ===")

conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()

# 1. Удаляем старые заказы
print("1. Удаление старых заказов...")
cursor.execute("DELETE FROM orders WHERE user_id = 7281878643")
deleted_orders = cursor.rowcount
print(f"   Удалено заказов: {deleted_orders}")

# 2. Удаляем старого пользователя (если это не текущий админ)
print("2. Удаление старого пользователя...")
cursor.execute("DELETE FROM users WHERE user_id = 7281878643")
deleted_users = cursor.rowcount
print(f"   Удалено пользователей: {deleted_users}")

# 3. Проверяем текущих пользователей
print("3. Текущие пользователи в базе:")
cursor.execute("SELECT user_id, username FROM users ORDER BY user_id")
users = cursor.fetchall()
for user_id, username in users:
    print(f"   User ID: {user_id}, Username: {username}")

# 4. Проверяем текущие заказы
print("4. Текущие заказы в базе:")
cursor.execute("SELECT order_id, user_id, status FROM orders")
orders = cursor.fetchall()
if orders:
    for order_id, user_id, status in orders:
        print(f"   Order #{order_id}: User ID {user_id}, Status: {status}")
else:
    print("   Заказов нет")

conn.commit()
conn.close()

print("\n✅ База данных очищена!")
print("\n=== Инструкция ===")
print("1. Перезапустите бота")
print("2. Протестируйте отправку чека об оплате")
print("3. Проверьте, приходят ли сообщения правильно")