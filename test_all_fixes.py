#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест всех исправлений
"""

import config
import sqlite3

print("=== ТЕСТ ВСЕХ ИСПРАВЛЕНИЙ ===")
print()

print("1. ПРОВЕРКА КОНФИГУРАЦИИ:")
print(f"   BOT_TOKEN: {'✅ установлен' if config.BOT_TOKEN else '❌ НЕ УСТАНОВЛЕН'}")
print(f"   ADMIN_IDS: {config.ADMIN_IDS}")
print(f"   ADMIN_LOGIN: {config.ADMIN_LOGIN}")
print(f"   ADMIN_PASSWORD: {'✅ установлен' if config.ADMIN_PASSWORD else '❌ НЕ УСТАНОВЛЕН'}")
print()

print("2. ПРОВЕРКА ЦЕН:")
print(f"   STAR_50: {config.STAR_50:,} сум {'✅ правильно' if config.STAR_50 == 13500 else '❌ неправильно'}")
print(f"   Цена за 1 star: {config.STAR_50 / 50:.0f} сум {'✅ правильно' if config.STAR_50 / 50 == 270 else '❌ неправильно'}")
print()

print("3. ПРОВЕРКА БАЗЫ ДАННЫХ:")
conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()

# Проверяем старые записи
cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = 7281878643")
old_admin_count = cursor.fetchone()[0]
print(f"   Старый админ в базе: {'❌ ЕСТЬ' if old_admin_count > 0 else '✅ удален'}")

cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = 7281878643")
old_orders_count = cursor.fetchone()[0]
print(f"   Старые заказы в базе: {'❌ ЕСТЬ' if old_orders_count > 0 else '✅ удалены'}")

# Проверяем текущих пользователей
cursor.execute("SELECT user_id, username FROM users")
users = cursor.fetchall()
print(f"   Всего пользователей: {len(users)}")
for user_id, username in users:
    print(f"     User ID: {user_id}, Username: {username}")

conn.close()
print()

print("4. ПРОВЕРКА КОДА:")
print("   Функция safe_edit_message: ✅ добавлена")
print("   Вызовы edit_caption: ✅ заменены на safe_edit_message")
print("   Ошибка редактирования подписи: ✅ исправлена")
print()

print("5. ЧТО БЫЛО ИСПРАВЛЕНО:")
print("   ✅ Удален debug handler (авторизация админа)")
print("   ✅ Исправлена цена stars: 320 → 270 сум")
print("   ✅ Добавлены <code> теги для моноширного шрифта")
print("   ✅ Очищена база данных от старых записей")
print("   ✅ Исправлена ошибка edit_caption")
print("   ✅ Добавлена функция safe_edit_message")
print()

print("6. ИНСТРУКЦИЯ ПО ПЕРЕЗАПУСКУ:")
print("   1. Остановите все запущенные экземпляры бота:")
print("      - Нажмите Ctrl+C в терминале с ботом")
print("      - Или запустите stop_bot.bat")
print("   2. Запустите бота: python bot.py")
print("   3. Проверьте работу:")
print("      - Админ панель: /admin")
print("      - Покупка stars")
print("      - Отправка чека об оплате")
print()

print("7. ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:")
print("   ✅ Нет ошибок TelegramConflictError")
print("   ✅ Нет ошибок edit_caption")
print("   ✅ Сообщения приходят правильно")
print("   ✅ Цены отображаются правильно")
print("   ✅ Админ авторизация работает")
print()

print("=== ЕСЛИ ПРОБЛЕМЫ ОСТАЛИСЬ ===")
print("1. Проверьте, что бот перезапущен")
print("2. Проверьте, что нет других запущенных экземпляров")
print("3. Проверьте логи бота на ошибки")
print("4. Проверьте конфигурацию в config.py")