#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой запуск бота
"""

import asyncio
import logging
from aiogram import Bot

async def check_and_start():
    """Проверяем токен и запускаем бота"""
    
    # Импортируем конфиг
    import config
    
    print("🔧 Проверка конфигурации...")
    print(f"🤖 Токен: {config.BOT_TOKEN[:10]}...")
    print(f"👑 Админы: {config.ADMIN_IDS}")
    print(f"📢 Канал: {config.CHANNEL_ID}")
    
    # Проверяем токен
    try:
        bot = Bot(token=config.BOT_TOKEN)
        me = await bot.get_me()
        print(f"\n✅ Токен рабочий!")
        print(f"🤖 Имя бота: {me.first_name}")
        print(f"👤 Username: @{me.username}")
        await bot.session.close()
        
        # Запускаем основной бот
        print("\n🚀 Запуск основного бота...")
        from bot import main
        await main()
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        if "Unauthorized" in str(e):
            print("⚠️ Токен неверный! Получите новый у @BotFather")
        else:
            print(f"🐛 Ошибка: {type(e).__name__}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(check_and_start())