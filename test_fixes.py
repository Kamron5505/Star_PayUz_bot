#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправлений
"""

import config

print("=== Тест исправлений ===")
print()

print("1. Проверка цен:")
print(f"   STAR_50 = {config.STAR_50:,} сум (должно быть 13,500)")
print(f"   Цена за 1 star: {config.STAR_50 / 50:.0f} сум (должно быть 270)")
print()

print("2. Проверка админ конфигурации:")
print(f"   ADMIN_IDS: {config.ADMIN_IDS}")
print(f"   ADMIN_LOGIN: {config.ADMIN_LOGIN}")
print(f"   ADMIN_PASSWORD: {config.ADMIN_PASSWORD}")
print()

print("3. Проверка расчета цены:")
stars_count = 50
price_per_star = 270  # Исправлено с 320 на 270
total_price = stars_count * price_per_star
print(f"   {stars_count} stars × {price_per_star} сум/star = {total_price:,} сум")
print(f"   Должно быть: {stars_count} × 270 = 13,500 сум")
print()

print("4. Проверка форматирования:")
print("   Текст с <code> тегами для моноширного шрифта:")
print("   Пример: <code>270 so'm</code> - должно быть моноширным")
print("   Пример: <code>13,500 so'm</code> - должно быть моноширным")
print()

print("=== Инструкция ===")
print("1. Перезапустите бота для применения изменений")
print("2. Проверьте админ панель: /admin")
print("3. Проверьте покупку stars: выберите 50 Stars")
print("4. Проверьте ввод username: должно работать")
print()

print("=== Возможные проблемы ===")
print("1. Бот не перезапущен - изменения не применены")
print("2. Неправильная база данных - проверьте star_payuz.db в star_payuz_bot/")
print("3. Кэш браузера/Telegram - попробуйте очистить кэш")