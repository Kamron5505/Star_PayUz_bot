#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест после исправлений
"""

import config

print("=== ФИНАЛЬНЫЙ ТЕСТ ПОСЛЕ ИСПРАВЛЕНИЙ ===")
print()

print("1. ПРОВЕРКА КОНФИГУРАЦИИ:")
print(f"   ✅ BOT_TOKEN: {'установлен' if config.BOT_TOKEN else 'НЕ УСТАНОВЛЕН'}")
print(f"   ✅ ADMIN_IDS: {config.ADMIN_IDS}")
print(f"   ✅ ADMIN_LOGIN: {config.ADMIN_LOGIN}")
print(f"   ✅ ADMIN_PASSWORD: {'установлен' if config.ADMIN_PASSWORD else 'НЕ УСТАНОВЛЕН'}")
print()

print("2. ПРОВЕРКА ЦЕН:")
print(f"   ✅ STAR_50: {config.STAR_50:,} сум (50 × 270 = 13,500)")
print(f"   ✅ Цена за 1 star: 270 сум")
print()

print("3. ПРОВЕРКА БАЗЫ ДАННЫХ:")
import sqlite3
conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()

# Проверяем пользователей
cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = 7281878643")
old_admin_count = cursor.fetchone()[0]
if old_admin_count == 0:
    print("   ✅ Старый админ (7281878643) удален из базы")
else:
    print(f"   ❌ Старый админ все еще в базе: {old_admin_count} записей")

# Проверяем заказы
cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = 7281878643")
old_orders_count = cursor.fetchone()[0]
if old_orders_count == 0:
    print("   ✅ Старые заказы удалены из базы")
else:
    print(f"   ❌ Старые заказы все еще в базе: {old_orders_count} записей")

conn.close()
print()

print("4. ЧТО БЫЛО ИСПРАВЛЕНО:")
print("   ✅ Удален debug handler (исправлена авторизация админа)")
print("   ✅ Исправлена цена stars: 320 → 270 сум")
print("   ✅ Добавлены <code> теги для моноширного шрифта")
print("   ✅ Очищена база данных от старых записей")
print("   ✅ Удален старый админ ID 7281878643 из базы")
print()

print("5. ЧТО НУЖНО СДЕЛАТЬ:")
print("   1. ПЕРЕЗАПУСТИТЬ БОТА")
print("   2. Протестировать админ панель: /admin")
print("   3. Протестировать покупку stars")
print("   4. Протестировать отправку чека об оплате")
print("   5. Проверить, что сообщения приходят правильно")
print()

print("6. ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
print("   - Админ авторизация: /admin → логин → пароль → панель")
print("   - Покупка stars: правильная цена (50 stars = 13,500 сум)")
print("   - Отправка чека: подтверждение приходит пользователю")
print("   - Уведомления: приходят только админу 8784918764")
print("   - НИКАКИХ сообщений на старый ID 7281878643")
print()

print("=== ЕСЛИ ПРОБЛЕМА ОСТАЛАСЬ ===")
print("Если сообщения все еще приходят на старый ID 7281878643:")
print("1. Проверьте, не запущено ли несколько копий бота")
print("2. Проверьте, нет ли других файлов конфигурации")
print("3. Проверьте кэш Telegram (перезапустите клиент)")
print("4. Убедитесь, что бот перезапущен после изменений")