#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление админ авторизации - упрощенная версия
"""

import re

print("=== Исправление админ авторизации ===")

with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Найдем и заменим обработчики админ авторизации на упрощенную версию
# Сначала найдем определение состояний AdminAuthStates
admin_auth_start = content.find('class AdminAuthStates(StatesGroup):')
if admin_auth_start != -1:
    print("✅ Найдено определение AdminAuthStates")
    
    # Найдем конец класса состояний
    admin_auth_end = content.find('\n\n', admin_auth_start)
    if admin_auth_end == -1:
        admin_auth_end = content.find('\nasync def', admin_auth_start)
    
    if admin_auth_end != -1:
        print("✅ Будет заменена авторизация на упрощенную версию")
        
        # Создаем новую упрощенную версию
        new_admin_auth = '''# Простая админ авторизация (вместо FSM)
admin_auth_data = {}  # user_id -> {'step': 'login' or 'password', 'login': '...'}

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    print(f"[DEBUG] /admin command from user {message.from_user.id}")
    
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ панели!")
        return
    
    # Проверяем, есть ли уже данные авторизации
    from bot import admin_auth_data
    user_id = message.from_user.id
    
    if user_id in admin_auth_data and admin_auth_data[user_id].get('authorized'):
        # Уже авторизован
        await message.answer(
            "🔐 <b>Админ панель Star_payuz</b>\\n\\n"
            "Выберите действие:",
            reply_markup=keyboards.admin_menu(),
            parse_mode="HTML"
        )
    else:
        # Начинаем авторизацию
        admin_auth_data[user_id] = {'step': 'login'}
        await message.answer(
            "🔐 <b>Вход в админ панель</b>\\n\\n"
            "Введите логин:",
            parse_mode="HTML"
        )

@dp.message(F.text)
async def admin_auth_handler(message: types.Message):
    """Обработчик авторизации админа"""
    from bot import admin_auth_data
    user_id = message.from_user.id
    
    if user_id not in admin_auth_data:
        return  # Не в процессе авторизации
    
    auth_data = admin_auth_data[user_id]
    
    if auth_data['step'] == 'login':
        # Проверяем логин
        if message.text.strip() == config.ADMIN_LOGIN:
            auth_data['step'] = 'password'
            auth_data['login'] = message.text.strip()
            await message.answer(
                "✅ <b>Логин принят</b>\\n\\n"
                "Введите пароль:",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Неверный логин!</b>\\n\\n"
                "Попробуйте еще раз: /admin",
                parse_mode="HTML"
            )
            del admin_auth_data[user_id]
    
    elif auth_data['step'] == 'password':
        # Проверяем пароль
        if message.text.strip() == config.ADMIN_PASSWORD:
            # Успешная авторизация
            auth_data['authorized'] = True
            auth_data['step'] = 'authorized'
            
            # Удаляем сообщение с паролем
            try:
                await message.delete()
            except:
                pass
            
            await message.answer(
                "✅ <b>Успешная авторизация!</b>\\n\\n"
                "🔐 <b>Админ панель Star_payuz</b>\\n\\n"
                "Выберите действие:",
                reply_markup=keyboards.admin_menu(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Неверный пароль!</b>\\n\\n"
                "Попробуйте еще раз: /admin",
                parse_mode="HTML"
            )
            del admin_auth_data[user_id]'''
        
        # Заменяем старую авторизацию на новую
        # Нужно найти и удалить старые обработчики
        print("⚠️ Для полного исправления нужно заменить код авторизации вручную")
        print("Создан файл simplified_admin_auth.py с упрощенной версией")
        
        # Сохраним упрощенную версию в отдельный файл
        with open('simplified_admin_auth.py', 'w', encoding='utf-8') as f:
            f.write(new_admin_auth)
        
        print("✅ Файл simplified_admin_auth.py создан")
        print("📋 Инструкция:")
        print("1. Откройте bot.py")
        print("2. Найдите и удалите старые обработчики админ авторизации")
        print("3. Скопируйте код из simplified_admin_auth.py в bot.py")
        print("4. Добавьте 'from bot import admin_auth_data' в начало файла")
    else:
        print("❌ Не могу найти конец определения AdminAuthStates")
else:
    print("❌ Не найдено определение AdminAuthStates")