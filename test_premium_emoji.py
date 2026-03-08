#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест премиум эмодзи
"""

print("=== ТЕСТ ПРЕМИУМ ЭМОДЗИ ===")
print()

print("1. Проверка ключевых мест с премиум эмодзи:")
print()

print("2. Примеры премиум эмодзи:")
print("   🌟 (stars): <tg-emoji emoji-id=\"5936259309812846957\">🌟</tg-emoji>")
print("   💰 (деньги): <tg-emoji emoji-id=\"5456390099958773299\">💰</tg-emoji>")
print("   👤 (пользователь): <tg-emoji emoji-id=\"5456390099958773299\">👤</tg-emoji>")
print("   ⚠️ (внимание): <tg-emoji emoji-id=\"5456390099958773299\">⚠️</tg-emoji>")
print("   👇 (вниз): <tg-emoji emoji-id=\"5456390099958773299\">👇</tg-emoji>")
print("   ✅ (галочка): <tg-emoji emoji-id=\"5456390099958773299\">✅</tg-emoji>")
print("   🛍️ (покупки): <tg-emoji emoji-id=\"5458488840022933066\">🛍️</tg-emoji>")
print()

print("3. Где добавлены премиум эмодзи:")
print("   ✅ show_stars_menu - меню выбора stars")
print("   ✅ product_selected для stars - при выборе товара stars")
print("   ✅ custom quantity stars - при вводе количества stars")
print("   ✅ username_received для stars - после ввода username")
print("   ✅ username_received для других услуг")
print()

print("4. Что нужно проверить после перезапуска бота:")
print("   1. Меню Stars: должны быть премиум эмодзи 🌟 и 👇")
print("   2. Выбор товара Stars: должны быть премиум эмодзи 🌟, 💰, 👤, ⚠️")
print("   3. Custom quantity Stars: должны быть премиум эмодзи 💰, 🌟, 👤, ✍️, ⚠️")
print("   4. После ввода username: должны быть премиум эмодзи ✅, 👤, 🌟, 💰, 👇")
print()

print("5. Инструкция:")
print("   1. Остановите бота (Ctrl+C)")
print("   2. Убедитесь, что нет других экземпляров")
print("   3. Запустите бота: python bot.py")
print("   4. Протестируйте покупку stars")
print("   5. Проверьте, что все эмодзи отображаются как премиум")
print()

print("=== ВАЖНО ===")
print("Премиум эмодзи работают только для пользователей с Telegram Premium!")
print("Для пользователей без Premium эмодзи будут отображаться как обычные.")
print("Это нормальное поведение Telegram.")