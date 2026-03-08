#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки нового бота
"""

import asyncio
import config
from aiogram import Bot

async def test_bot():
    print("=== Тест нового бота ===")
    print(f"Токен: {config.BOT_TOKEN[:10]}...")
    print()
    
    try:
        bot = Bot(token=config.BOT_TOKEN)
        
        # Получим информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен успешно!")
        print(f"   ID: {bot_info.id}")
        print(f"   Имя: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   Может читать сообщения группы: {bot_info.can_read_all_group_messages}")
        print(f"   Поддерживает инлайн-режим: {bot_info.supports_inline_queries}")
        print()
        
        # Проверим, что бот активен
        print("Проверка активности бота...")
        try:
            # Попробуем отправить тестовое сообщение самому себе
            test_message = "🤖 <b>Тестовое сообщение от бота</b>\n"
            test_message += "<tg-emoji emoji-id=\"5936259309812846957\">🌟</tg-emoji> <b>Премиум эмодзи тест</b>\n"
            test_message += "💎 <b>Обычный эмодзи тест</b>"
            
            # Отправим сообщение в избранное (Saved Messages)
            # await bot.send_message(bot_info.id, test_message, parse_mode="HTML")
            print("✅ Бот готов к отправке сообщений")
            print("   (Отправка тестового сообщения пропущена для безопасности)")
            
        except Exception as e:
            print(f"⚠️ Ошибка при отправке сообщения: {e}")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        print("Возможные причины:")
        print("1. Неверный токен")
        print("2. Бот заблокирован")
        print("3. Проблемы с сетью")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_bot())