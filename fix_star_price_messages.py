#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление сообщений с ценой 1 star = 320 сум на 270 сум
"""

import re

print("=== Исправление сообщений в bot.py ===")

with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменим все упоминания 320 сум на 270 сум
# 1. "320 so'm" → "270 so'm"
# 2. "320 сум" → "270 сум"
# 3. "320 so'm" в тегах <code> → "270 so'm"
# 4. "320 сум" в тегах <code> → "270 сум"

old_content = content

# Замена для узбекского
content = re.sub(r'320\s*so\'m', '270 so\'m', content, flags=re.IGNORECASE)
content = re.sub(r'320\s*so‘m', '270 so‘m', content, flags=re.IGNORECASE)
content = re.sub(r'320\s*so`m', '270 so`m', content, flags=re.IGNORECASE)

# Замена для русского
content = re.sub(r'320\s*сум', '270 сум', content, flags=re.IGNORECASE)

# Замена в конкретных контекстах
content = content.replace('1 star = 320 so\'m', '1 star = 270 so\'m')
content = content.replace('1 star = 320 сум', '1 star = 270 сум')
content = content.replace('1 star narxi: 320 so\'m', '1 star narxi: 270 so\'m')
content = content.replace('Цена 1 star: 320 сум', 'Цена 1 star: 270 сум')

# Сохраним
with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Сообщения в bot.py обновлены")

# Проверим изменения
print("\n=== Проверка изменений ===")
old_lines = old_content.split('\n')
new_lines = content.split('\n')

changed_count = 0
for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
    if old_line != new_line and ('320' in old_line or '270' in new_line):
        print(f"Строка {i+1}:")
        print(f"  Было: {old_line[:80]}...")
        print(f"  Стало: {new_line[:80]}...")
        print()
        changed_count += 1

print(f"✅ Изменено {changed_count} строк")

# Также проверим другие файлы
other_files = ['premium_messages.py', 'universal_messages.py']
for file in other_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            if '320' in file_content:
                print(f"\n⚠️ В файле {file} все еще есть 320:")
                # Заменим
                file_content = file_content.replace('320', '270')
                with open(file, 'w', encoding='utf-8') as fw:
                    fw.write(file_content)
                print(f"✅ Исправлено в {file}")
    except FileNotFoundError:
        pass

print("\n🎉 Все сообщения обновлены!")