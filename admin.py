# -*- coding: utf-8 -*-
"""
Админ панель Star_payuz
"""
import logging
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config
import database
import keyboards

# Проверка на админа
def is_admin(user_id):
    return user_id in config.ADMIN_IDS

# Функции админ панели будут зарегистрированы в bot.py
