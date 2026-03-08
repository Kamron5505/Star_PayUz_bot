#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест админ панели
"""

import config

print("=== Тест конфигурации админа ===")
print(f"ADMIN_IDS: {config.ADMIN_IDS}")
print(f"ADMIN_LOGIN: {config.ADMIN_LOGIN}")
print(f"ADMIN_PASSWORD: {config.ADMIN_PASSWORD}")
print(f"ADMIN_USERNAME: {config.ADMIN_USERNAME}")
print()

# Проверим ID
test_id = 8784918764
if test_id in config.ADMIN_IDS:
    print(f"✅ ID {test_id} есть в списке администраторов")
else:
    print(f"❌ ID {test_id} НЕТ в списке администраторов")

print()
print("=== Инструкция по входу ===")
print("1. Отправьте боту команду /admin")
print("2. Введите логин: Kamron5505")
print("3. Введите пароль: 5505")
print("4. После успешной авторизации откроется админ панель")
print()
print("=== Возможные проблемы ===")
print("1. Убедитесь, что ID правильный: 8784918764")
print("2. Убедитесь, что бот запущен")
print("3. Проверьте, что вы отправили команду /admin от правильного аккаунта")
print("4. Логин: Kamron5505, Пароль: 5505")