#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск бота с отладкой админ панели
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database
import keyboards
from translations import get_text, get_text_simple
from premium_messages import (
    get_premium_welcome,
    get_premium_service_selected,
    get_premium_payment_info,
    get_premium_order_accepted,
    get_premium_help,
    get_premium_category_name
)

# Включаем подробное логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class OrderStates(StatesGroup):
    waiting_for_phone_number = State()
    waiting_for_username = State()
    waiting_for_message = State()
    waiting_for_anonymous = State()
    waiting_for_payment_proof = State()
    waiting_for_roblox_login = State()
    waiting_for_roblox_password = State()
    waiting_for_stars_count = State()
    waiting_for_channel_link = State()  # Для бустов - ссылка на канал

class AdminAuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

print("=== ЗАПУСК БОТА С ОТЛАДКОЙ ===")
print(f"Админ ID: {config.ADMIN_IDS}")
print(f"Логин: {config.ADMIN_LOGIN}")
print(f"Пароль: {config.ADMIN_PASSWORD}")

# Импортируем остальные функции из bot.py
print("Импортируем обработчики из bot.py...")

# Копируем основные обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    print(f"[DEBUG] /start from {message.from_user.id}")
    # ... остальной код /start

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    """Обработчик команды /admin"""
    print(f"[DEBUG ADMIN] /admin command from user {message.from_user.id}")
    print(f"[DEBUG ADMIN] ADMIN_IDS: {config.ADMIN_IDS}")
    
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ панели!")
        print(f"[DEBUG ADMIN] Access denied for {message.from_user.id}")
        return
    
    # Проверяем авторизацию
    data = await state.get_data()
    print(f"[DEBUG ADMIN] State data: {data}")
    
    if data.get('admin_authorized'):
        # Уже авторизован
        print(f"[DEBUG ADMIN] Already authorized")
        await message.answer(
            "🔐 <b>Админ панель Star_payuz</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboards.admin_menu(),
            parse_mode="HTML"
        )
    else:
        # Запрашиваем логин
        print(f"[DEBUG ADMIN] Requesting login")
        await message.answer(
            "🔐 <b>Вход в админ панель</b>\n\n"
            "Введите логин:",
            parse_mode="HTML"
        )
        await state.set_state(AdminAuthStates.waiting_for_login)
        print(f"[DEBUG ADMIN] State set to waiting_for_login")

@dp.message(AdminAuthStates.waiting_for_login)
async def admin_login_received(message: types.Message, state: FSMContext):
    """Получение логина"""
    login = message.text.strip()
    
    print(f"[DEBUG ADMIN LOGIN] Login attempt: '{login}' from {message.from_user.id}")
    print(f"[DEBUG ADMIN LOGIN] Expected login: '{config.ADMIN_LOGIN}'")
    
    if login == config.ADMIN_LOGIN:
        print(f"[DEBUG ADMIN LOGIN] Login correct")
        await state.update_data(admin_login=login)
        await message.answer(
            "✅ <b>Логин принят</b>\n\n"
            "Введите пароль:",
            parse_mode="HTML"
        )
        await state.set_state(AdminAuthStates.waiting_for_password)
        print(f"[DEBUG ADMIN LOGIN] State set to waiting_for_password")
    else:
        print(f"[DEBUG ADMIN LOGIN] Wrong login")
        await message.answer(
            "❌ <b>Неверный логин!</b>\n\n"
            "Попробуйте еще раз или /cancel для отмены",
            parse_mode="HTML"
        )

@dp.message(AdminAuthStates.waiting_for_password)
async def admin_password_received(message: types.Message, state: FSMContext):
    """Получение пароля"""
    password = message.text.strip()
    
    print(f"[DEBUG ADMIN PASSWORD] Password attempt from {message.from_user.id}")
    print(f"[DEBUG ADMIN PASSWORD] Expected password: '{config.ADMIN_PASSWORD}'")
    
    # Удаляем сообщение с паролем для безопасности
    try:
        await message.delete()
    except:
        pass
    
    if password == config.ADMIN_PASSWORD:
        print(f"[DEBUG ADMIN PASSWORD] Password correct")
        await state.update_data(admin_authorized=True)
        await state.set_state(None)
        
        await bot.send_message(
            message.from_user.id,
            "✅ <b>Успешная авторизация!</b>\n\n"
            "🔐 <b>Админ панель Star_payuz</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboards.admin_menu(),
            parse_mode="HTML"
        )
    else:
        print(f"[DEBUG ADMIN PASSWORD] Wrong password")
        await bot.send_message(
            message.from_user.id,
            "❌ <b>Неверный пароль!</b>\n\n"
            "Попробуйте еще раз: /admin",
            parse_mode="HTML"
        )
        await state.clear()

async def main():
    """Основная функция"""
    print("\n🚀 Бот запускается...")
    print("Отправьте /admin для теста админ панели")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())