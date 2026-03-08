#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест потока сообщений
"""

import config
import database

print("=== Тест потока сообщений ===")
print()

print("1. Проверка конфигурации админов:")
print(f"   ADMIN_IDS: {config.ADMIN_IDS}")
print(f"   Должен быть только один ID: 8784918764")
print()

print("2. Проверка базы данных:")
print("   Заказы в базе данных:")
import sqlite3
conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()
cursor.execute('SELECT order_id, user_id, status FROM orders')
orders = cursor.fetchall()
for order_id, user_id, status in orders:
    print(f"   Order #{order_id}: User ID {user_id}, Status: {status}")
    if user_id == 7281878643:
        print(f"   ⚠️ ВНИМАНИЕ: Заказ принадлежит старому админу (7281878643)!")
        print(f"   Это может быть причиной проблемы!")
conn.close()
print()

print("3. Проверка пользователей в базе:")
conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()
cursor.execute('SELECT user_id, username FROM users WHERE user_id IN (7281878643, 8784918764)')
users = cursor.fetchall()
for user_id, username in users:
    print(f"   User ID: {user_id}, Username: {username}")
    if user_id == 7281878643:
        print(f"   ⚠️ Старый админ все еще в базе данных!")
conn.close()
print()

print("=== Возможные решения ===")
print("1. Удалить старые заказы из базы данных")
print("2. Удалить старого пользователя из базы данных")
print("3. Проверить, нет ли в коде жестко прописанного ID 7281878643")
print()

print("=== Инструкция по исправлению ===")
print("1. Очистить базу данных от старых записей")
print("2. Перезапустить бота")
print("3. Протестировать отправку чека об оплате")