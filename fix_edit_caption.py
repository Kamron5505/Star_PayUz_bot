#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для замены всех вызовов edit_caption на safe_edit_message
"""

import re

with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем все вызовы edit_caption
# Паттерн: await callback.message.edit_caption(caption=текст, ...)
pattern1 = r'await callback\.message\.edit_caption\(caption=([^,]+),\s*reply_markup=([^,]+),\s*parse_mode="HTML"\)'
replacement1 = r'await safe_edit_message(callback, \1, reply_markup=\2)'

pattern2 = r'await callback\.message\.edit_caption\(caption=([^,]+),\s*parse_mode="HTML"\)'
replacement2 = r'await safe_edit_message(callback, \1)'

pattern3 = r'await callback\.message\.edit_caption\(caption=([^,]+),\s*reply_markup=([^)]+)\)'
replacement3 = r'await safe_edit_message(callback, \1, reply_markup=\2)'

# Применяем замены
content = re.sub(pattern1, replacement1, content)
content = re.sub(pattern2, replacement2, content)
content = re.sub(pattern3, replacement3, content)

# Также нужно заменить вызовы с другими параметрами
# Более общий паттерн
pattern_general = r'await callback\.message\.edit_caption\((.*?)\)'
def replace_general(match):
    params = match.group(1)
    # Парсим параметры
    if 'reply_markup=' in params and 'parse_mode=' in params:
        # Ищем caption, reply_markup, parse_mode
        caption_match = re.search(r'caption=([^,]+)', params)
        reply_markup_match = re.search(r'reply_markup=([^,]+)', params)
        if caption_match and reply_markup_match:
            return f'await safe_edit_message(callback, {caption_match.group(1)}, reply_markup={reply_markup_match.group(1)})'
    elif 'reply_markup=' in params:
        # Только caption и reply_markup
        caption_match = re.search(r'caption=([^,]+)', params)
        reply_markup_match = re.search(r'reply_markup=([^,]+)', params)
        if caption_match and reply_markup_match:
            return f'await safe_edit_message(callback, {caption_match.group(1)}, reply_markup={reply_markup_match.group(1)})'
    else:
        # Только caption
        caption_match = re.search(r'caption=([^,]+)', params)
        if caption_match:
            return f'await safe_edit_message(callback, {caption_match.group(1)})'
    return match.group(0)  # Если не нашли, оставляем как есть

content = re.sub(pattern_general, replace_general, content)

# Сохраняем изменения
with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Заменены вызовы edit_caption на safe_edit_message")
print("⚠️ Проверьте код вручную, так как автоматическая замена может быть не идеальной")