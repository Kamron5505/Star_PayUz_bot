#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки премиум эмодзи
"""

import premium_messages

print("=== Тест премиум эмодзи ===")
print()

# Тест узбекской версии
print("Узбекская версия:")
uz_text = premium_messages.get_premium_welcome("TestUser", lang="uz")
print(uz_text[:300] + "...")
print()

# Тест русской версии  
print("Русская версия:")
ru_text = premium_messages.get_premium_welcome("TestUser", lang="ru")
print(ru_text[:300] + "...")
print()

# Проверим наличие тегов
print("=== Проверка тегов ===")
print(f"Теги <tg-emoji> в узбекской версии: {'<tg-emoji' in uz_text}")
print(f"Теги <tg-emoji> в русской версии: {'<tg-emoji' in ru_text}")
print()

# Посчитаем теги
uz_count = uz_text.count('<tg-emoji')
ru_count = ru_text.count('<tg-emoji')
print(f"Количество тегов в узбекской версии: {uz_count}")
print(f"Количество тегов в русской версии: {ru_count}")
print()

# Проверим конкретный emoji-id
target_emoji_id = "5936259309812846957"
print(f"=== Проверка emoji-id {target_emoji_id} ===")
print(f"В узбекской версии: {target_emoji_id in uz_text}")
print(f"В русской версии: {target_emoji_id in ru_text}")

if target_emoji_id in uz_text:
    # Найдем контекст
    import re
    pattern = f'emoji-id="{re.escape(target_emoji_id)}">([^<]+)</tg-emoji>'
    match = re.search(pattern, uz_text)
    if match:
        print(f"Emoji символ: {match.group(1)}")