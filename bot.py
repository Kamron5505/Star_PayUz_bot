# -*- coding: utf-8 -*-
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

import config
import database
import keyboards
from translations import get_text, get_text_simple
from premium_messages import (
    get_premium_welcome,
    get_premium_order_accepted,
    get_premium_help,
)

# Вспомогательная функция для безопасного редактирования сообщений
async def safe_edit_message(callback, text, reply_markup=None, parse_mode="HTML"):
    """Безопасно редактировать сообщение (работает с текстом и фото)"""
    # Сначала пробуем отредактировать текст (для текстовых сообщений)
    try:
        await callback.message.edit_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        return
    except Exception as e1:
        # Если не получилось, пробуем отредактировать подпись (для сообщений с фото)
        try:
            await callback.message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            return
        except Exception as e2:
            # Если и это не получилось, удаляем старое сообщение и отправляем новое
            logging.error(f"Failed to edit message: {e1}, {e2}")
            try:
                await callback.message.delete()
            except:
                pass
            await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class OrderStates(StatesGroup):
    waiting_for_payment_proof = State()
    waiting_for_phone_number = State()
    waiting_for_username = State()
    waiting_for_message = State()
    waiting_for_anonymous = State()
    waiting_for_roblox_login = State()
    waiting_for_roblox_password = State()
    waiting_for_stars_count = State()
    waiting_for_channel_link = State()  # Для бустов - ссылка на канал
    waiting_for_payment_confirmation = State()  # Для подтверждения оплаты Stars
    waiting_for_exact_amount = State()  # Для ввода точной суммы
    waiting_for_delete_order_id = State()  # Для удаления заказа по ID


class BroadcastStates(StatesGroup):
    waiting_for_message = State()

class AdminAuthStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Subscription check error (ID): {e}")
        try:
            member = await bot.get_chat_member(config.CHANNEL_UZ, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e2:
            logging.error(f"Subscription check error (username): {e2}")
            return False  # Если не можем проверить - блокируем

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    is_new = not database.user_exists(user.id)
    database.add_user(user.id, user.username, user.first_name)
    lang = database.get_user_language(user.id)
    
    # Обработка реферальной ссылки
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id == user.id:
                referrer_id = None
        except:
            referrer_id = None
    
    # Формируем упоминание пользователя
    user_mention = f"@{user.username}" if user.username else user.first_name
    
    # Если язык не выбран (первый запуск), показываем выбор языка
    if lang == "uz" and is_new:
        welcome_text = (
            f"👋 <b>Assalomu aleykum, {user_mention}!</b>\n\n"
            f"🌟 <b>Star_payuz</b> - Telegram xizmatlari do'koni\n\n"
            f"🌐 <b>Iltimos, tilni tanlang:</b>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang_ru")
            ]
        ])
        
        try:
            if hasattr(config, 'BANNER_FILE'):
                import os
                banner_path = config.BANNER_FILE
                if os.path.exists(banner_path):
                    photo = types.FSInputFile(banner_path)
                    await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=keyboard, parse_mode="HTML")
                    return
        except Exception as e:
            logging.error(f"Banner error: {e}")
        
        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")
        return
    
    # Проверка подписки
    if not await check_subscription(user.id):
        # Сохраняем реферера для начисления после подписки
        if referrer_id and is_new:
            import sqlite3 as _sqlite3
            _conn = _sqlite3.connect(config.DATABASE_FILE)
            _conn.execute('UPDATE users SET referred_by = ? WHERE user_id = ? AND referred_by IS NULL', (referrer_id, user.id))
            _conn.commit()
            _conn.close()
        if lang == "uz":
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Botdan foydalanish uchun kanalimizga obuna bo'ling!</b>"
            )
        else:
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Для использования бота подпишитесь на наш канал!</b>"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna / Подписаться", url=config.CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish / Проверить", callback_data="check_subscription")]
        ])
        
        try:
            if hasattr(config, 'BANNER_FILE'):
                import os
                banner_path = config.BANNER_FILE
                if os.path.exists(banner_path):
                    photo = types.FSInputFile(banner_path)
                    await message.answer_photo(photo=photo, caption=sub_text, reply_markup=keyboard, parse_mode="HTML")
                    return
        except Exception as e:
            logging.error(f"Banner error: {e}")
        
        await message.answer(sub_text, reply_markup=keyboard, parse_mode="HTML")
        return
    
    # Приветствие для подписанных
    # Начисляем реферал если пользователь уже подписан и пришёл по ссылке
    if referrer_id and is_new:
        rewarded = database.add_referral(referrer_id, user.id)
        if rewarded:
            try:
                ref_lang = database.get_user_language(referrer_id)
                ref_mention = f"@{user.username}" if user.username else user.first_name
                if ref_lang == "uz":
                    ref_text = (
                        f"<tg-emoji emoji-id=\"5368324170671202286\">🎉</tg-emoji> <b>Yangi referal!</b>\n\n"
                        f"<tg-emoji emoji-id=\"5472308992514464048\">👤</tg-emoji> {ref_mention} sizning havolangiz orqali qo'shildi\n"
                        f"<tg-emoji emoji-id=\"5368324170671202286\">⭐</tg-emoji> <b>+0.50 yulduz</b> hisobingizga qo'shildi!"
                    )
                else:
                    ref_text = (
                        f"<tg-emoji emoji-id=\"5368324170671202286\">🎉</tg-emoji> <b>Новый реферал!</b>\n\n"
                        f"<tg-emoji emoji-id=\"5472308992514464048\">👤</tg-emoji> {ref_mention} присоединился по вашей ссылке\n"
                        f"<tg-emoji emoji-id=\"5368324170671202286\">⭐</tg-emoji> <b>+0.50 звезды</b> зачислено на ваш счёт!"
                    )
                await bot.send_message(referrer_id, ref_text, parse_mode="HTML")
            except:
                pass
    welcome_text = get_premium_welcome(user_mention, lang)
    
    photo_sent = False
    try:
        if hasattr(config, 'BANNER_FILE'):
            import os
            banner_path = config.BANNER_FILE
            if os.path.exists(banner_path):
                photo = types.FSInputFile(banner_path)
                await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
                photo_sent = True
                logging.info(f"Banner sent from file: {banner_path}")
            else:
                logging.warning(f"Banner file not found: {banner_path}")
    except Exception as e:
        logging.error(f"Banner error: {e}")
    
    if not photo_sent:
        await message.answer(welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery):
    lang = callback.data.replace("lang_", "")
    database.set_user_language(callback.from_user.id, lang)
    user_mention = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
    
    # Проверяем подписку после выбора языка
    if not await check_subscription(callback.from_user.id):
        if lang == "uz":
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Botdan foydalanish uchun kanalimizga obuna bo'ling!</b>"
            )
        else:
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Для использования бота подпишитесь на наш канал!</b>"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna / Подписаться", url=config.CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish / Проверить", callback_data="check_subscription")]
        ])
        
        await safe_edit_message(callback, sub_text, reply_markup=keyboard)
    else:
        # Показываем продающее приветствие
        await callback.answer(get_text_simple(lang, "language_changed"))
        welcome_text = get_premium_welcome(user_mention, lang)
        await safe_edit_message(callback, welcome_text, reply_markup=keyboards.main_menu(lang))

@dp.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    user_mention = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
    
    if await check_subscription(callback.from_user.id):
        # Начисляем реферальный бонус если есть реферер
        conn = __import__('sqlite3').connect(config.DATABASE_FILE)
        cur = conn.cursor()
        cur.execute('SELECT referred_by FROM users WHERE user_id = ?', (callback.from_user.id,))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            rewarded = database.add_referral(row[0], callback.from_user.id)
            if rewarded:
                try:
                    ref_lang = database.get_user_language(row[0])
                    if ref_lang == "uz":
                        ref_text = (
                            f"<tg-emoji emoji-id=\"5368324170671202286\">🎉</tg-emoji> <b>Yangi referal!</b>\n\n"
                            f"<tg-emoji emoji-id=\"5472308992514464048\">👤</tg-emoji> {user_mention} sizning havolangiz orqali qo'shildi\n"
                            f"<tg-emoji emoji-id=\"5368324170671202286\">⭐</tg-emoji> <b>+0.50 yulduz</b> hisobingizga qo'shildi!"
                        )
                    else:
                        ref_text = (
                            f"<tg-emoji emoji-id=\"5368324170671202286\">🎉</tg-emoji> <b>Новый реферал!</b>\n\n"
                            f"<tg-emoji emoji-id=\"5472308992514464048\">👤</tg-emoji> {user_mention} присоединился по вашей ссылке\n"
                            f"<tg-emoji emoji-id=\"5368324170671202286\">⭐</tg-emoji> <b>+0.50 звезды</b> зачислено на ваш счёт!"
                        )
                    await bot.send_message(row[0], ref_text, parse_mode="HTML")
                except:
                    pass

        await callback.message.delete()
        welcome_text = get_premium_welcome(user_mention, lang)
        try:
            if hasattr(config, 'BANNER_FILE'):
                with open(config.BANNER_FILE, 'rb') as photo:
                    await bot.send_photo(callback.from_user.id, photo=photo, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
            else:
                await bot.send_photo(callback.from_user.id, photo=config.BANNER_URL, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
        except Exception as e:
            logging.error(f"Banner error: {e}")
            await bot.send_message(callback.from_user.id, welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    else:
        await callback.answer(get_text_simple(lang, "not_subscribed"), show_alert=True)

@dp.callback_query(F.data == "change_language")
async def change_language(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    await safe_edit_message(callback, get_text(lang, "choose_language"), reply_markup=keyboards.language_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("service_"))
async def service_selected(callback: types.CallbackQuery, state: FSMContext):
    service = callback.data.replace("service_", "")
    lang = database.get_user_language(callback.from_user.id)
    
    # Если выбран Premium - показываем варианты
    if service == "telegram_premium":
        if lang == "uz":
            text = (
                "💎 <b>Telegram Premium</b>\n\n"
                "Qaysi variantni tanlamoqchisiz?\n\n"
                "📌 <b>1 oylik</b> - Telefon raqam bilan (kirish kerak)\n"
                "📌 <b>12 oylik</b> - Telefon raqam bilan (kirish kerak)\n\n"
                "<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Muhim:</b> Akkauntingizga kirishimiz kerak bo'ladi"
            )
        else:
            text = (
                "💎 <b>Telegram Premium</b>\n\n"
                "Какой вариант выбираете?\n\n"
                "📌 <b>1 месяц</b> - По номеру телефона (нужен вход)\n"
                "📌 <b>12 месяцев</b> - По номеру телефона (нужен вход)\n\n"
                "<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Важно:</b> Потребуется вход в ваш аккаунт"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 1 oy / месяц", callback_data="premium_1month")],
            [InlineKeyboardButton(text="📅 12 oy / месяцев", callback_data="premium_12month")],
            [InlineKeyboardButton(text="◀️ Orqaga / Назад", callback_data="back_to_menu")]
        ])
        
        await safe_edit_message(callback, text, reply_markup=keyboard)
        await callback.answer()
        return
    
    # Для остальных услуг - обычный процесс
    price = config.PRICES.get(service, 0)
    
    service_names = {
        "telegram_stars": get_text_simple(lang, "stars_buy"),
        "stars_sell": get_text_simple(lang, "stars_sell"),
        "nft_gifts": get_text_simple(lang, "nft_gift_buy"),
        "nft_market": get_text_simple(lang, "nft_gift_market"),
        "robux": get_text_simple(lang, "robux"),
        "virtual_numbers": get_text_simple(lang, "virtual_number")
    }
    
    service_name = service_names.get(service, service)
    
    # Для Stars и NFT подарков - запрашиваем username
    if service in ["telegram_stars", "nft_gifts", "nft_market"]:
        if lang == "uz":
            text = (
                f"✅ Siz tanladingiz: <b>{service_name}</b>\n\n"
                f"💰 <b>Narxi:</b> <b>{price:,} UZS</b>\n\n"
                f"👤 <b>Iltimos, username yuboring:</b>\n"
                f"Format: @username yoki username\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Muhim:</b> Stars yoki sovg'a shu akkauntga yuboriladi"
            )
        else:
            text = (
                f"✅ Вы выбрали: <b>{service_name}</b>\n\n"
                f"💰 <b>Цена:</b> <b>{price:,} UZS</b>\n\n"
                f"👤 <b>Пожалуйста, отправьте username:</b>\n"
                f"Формат: @username или username\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Важно:</b> Stars или подарок будет отправлен на этот аккаунт"
            )
        
        await safe_edit_message(callback, text)
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(service=service, service_name=service_name, price=price)
    else:
        # Для остальных услуг - сразу к оплате
        text = get_premium_service_selected(service_name, price, lang)
        await safe_edit_message(callback, text, reply_markup=keyboards.payment_methods())
        await state.update_data(service=service, service_name=service_name, price=price)
    
    await callback.answer()

@dp.callback_query(F.data.startswith("premium_"))
async def premium_period_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор периода Premium"""
    period = callback.data.replace("premium_", "")
    lang = database.get_user_language(callback.from_user.id)
    
    if period == "1month":
        price = config.PRICES.get("premium_1month", 50000)
        if lang == "uz":
            service_name = "💎 Telegram Premium (1 oy)"
        else:
            service_name = "💎 Telegram Premium (1 месяц)"
    else:  # 12month
        price = config.PRICES.get("premium_12month", 500000)
        if lang == "uz":
            service_name = "💎 Telegram Premium (12 oy)"
        else:
            service_name = "💎 Telegram Premium (12 месяцев)"
    
    if lang == "uz":
        text = (
            f"✅ Siz tanladingiz: <b>{service_name}</b>\n\n"
            f"💰 <b>Narxi:</b> <b>{price:,} UZS</b>\n\n"
            f"📱 <b>Iltimos, telefon raqamingizni yuboring:</b>\n"
            f"Format: +998901234567\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Muhim:</b> Akkauntingizga kirish uchun kod yuboriladi"
        )
    else:
        text = (
            f"✅ Вы выбрали: <b>{service_name}</b>\n\n"
            f"💰 <b>Цена:</b> <b>{price:,} UZS</b>\n\n"
            f"📱 <b>Пожалуйста, отправьте номер телефона:</b>\n"
            f"Формат: +998901234567\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Важно:</b> На номер придет код для входа в аккаунт"
        )
    
    await safe_edit_message(callback, text)
    await state.set_state(OrderStates.waiting_for_phone_number)
    await state.update_data(
        service=f"premium_{period}",
        service_name=service_name,
        price=price
    )
    await callback.answer()

@dp.message(OrderStates.waiting_for_phone_number)
async def phone_number_received(message: types.Message, state: FSMContext):
    """Получение номера телефона"""
    lang = database.get_user_language(message.from_user.id)
    phone = message.text.strip()
    
    # Простая валидация номера
    if not phone.startswith('+') or len(phone) < 10:
        if lang == "uz":
            await message.answer(
                "❌ <b>Noto'g'ri format!</b>\n\n"
                "Iltimos, to'g'ri formatda yuboring:\n"
                "+998901234567",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Неверный формат!</b>\n\n"
                "Пожалуйста, отправьте в правильном формате:\n"
                "+998901234567",
                parse_mode="HTML"
            )
        return
    
    # Сохраняем номер и переходим к оплате
    await state.update_data(phone_number=phone)
    data = await state.get_data()
    service_name = data.get('service_name')
    price = data.get('price')
    
    if lang == "uz":
        text = (
            f"✅ <b>Telefon raqam qabul qilindi!</b>\n\n"
            f"📱 <b>Raqam:</b> <code>{phone}</code>\n"
            f"🛍️ <b>Xizmat:</b> {service_name}\n"
            f"💰 <b>Summa:</b> <b>{price:,} UZS</b>\n\n"
            f"👇 <b>To'lov usulini tanlang:</b>"
        )
    else:
        text = (
            f"✅ <b>Номер телефона принят!</b>\n\n"
            f"📱 <b>Номер:</b> <code>{phone}</code>\n"
            f"🛍️ <b>Услуга:</b> {service_name}\n"
            f"💰 <b>Сумма:</b> <b>{price:,} UZS</b>\n\n"
            f"👇 <b>Выберите способ оплаты:</b>"
        )
    
    await message.answer(text, reply_markup=keyboards.payment_methods(), parse_mode="HTML")
    await state.set_state(None)  # Сбрасываем состояние ожидания номера

@dp.message(OrderStates.waiting_for_username)
async def username_received(message: types.Message, state: FSMContext):
    """Получение username для Stars или NFT подарков"""
    lang = database.get_user_language(message.from_user.id)
    username = message.text.strip()

    # Убираем @ если есть
    if username.startswith('@'):
        username = username[1:]

    # Простая валидация
    if len(username) < 3:
        if lang == "uz":
            await message.answer(
                "❌ <b>Noto'g'ri username!</b>\n\n"
                "Iltimos, to'g'ri formatda yuboring:\n"
                "@username yoki username",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Неверный username!</b>\n\n"
                "Пожалуйста, отправьте в правильном формате:\n"
                "@username или username",
                parse_mode="HTML"
            )
        return

    # Сохраняем username
    await state.update_data(username=username)
    data = await state.get_data()
    service = data.get('service')

    # Получаем категорию
    data = await state.get_data()
    category = data.get('category', '')

    # Если это Gifts подарок - запрашиваем сообщение
    if category == "gifts":
        if lang == "uz":
            text = (
                f"<tg-emoji emoji-id=\"5429381339851796035\">✅</tg-emoji> <b>Username qabul qilindi!</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Username: @{username}</b>\n\n"
                f"<tg-emoji emoji-id=\"5190859184312167965\">💌</tg-emoji> <b>Iltimos, xabar yuboring:</b>\n"
                f"Bu xabar sovg'a bilan birga yuboriladi\n\n"
                f"<tg-emoji emoji-id=\"5334882760735598374\">📝</tg-emoji> <b>Xabar uzunligi: 0-30 belgi</b>\n"
                f"<i>Agar xabar kerak bo'lmasa, <code>-</code> yuboring</i>"
            )
        else:
            text = (
                f"<tg-emoji emoji-id=\"5429381339851796035\">✅</tg-emoji> <b>Username принят!</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Username: @{username}</b>\n\n"
                f"<tg-emoji emoji-id=\"5190859184312167965\">💌</tg-emoji> <b>Пожалуйста, отправьте сообщение:</b>\n"
                f"Это сообщение будет отправлено вместе с подарком\n\n"
                f"<tg-emoji emoji-id=\"5334882760735598374\">📝</tg-emoji> <b>Длина сообщения: 0-30 символов</b>\n"
                f"<i>Если сообщение не нужно, отправьте <code>-</code></i>"
            )

        await message.answer(text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_message)
    else:
        # Для Stars и других услуг
        data = await state.get_data()
        service_name = data.get('service_name')
        price = data.get('price')
        category = data.get('category', '')
        stars_count = data.get('stars_count', 0)

        if category == "stars" and stars_count > 0:
            # Для Stars показываем сводку заказа с кнопками подтверждения
            import random
            import string
            order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            await state.update_data(order_id=order_id)

            if lang == "uz":
                text = (
                    f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>To'lov ma'lumotlari</b>\n\n"
                    f"<code>▪️ Turi: ⭐ Telegram Stars\n"
                    f"▪️ Username: @{username}\n"
                    f"▪️ Soni: {stars_count}\n"
                    f"▪️ Summa: {price:,}\n"
                    f"▪️ ID: [{order_id}]</code>\n\n"
                    f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Ma'lumotlarni tekshirib, to'lovni tasdiqlashingiz bilan buyurtma sizga avtomatik yuboriladi, agar to'lov 5 daqiqa ichida amalga oshirilmasa, buyurtma avtomatik ravishda bekor qilinadi.</b>"
                )
            else:
                text = (
                    f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Информация об оплате</b>\n\n"
                    f"<code>▪️ Тип: ⭐ Telegram Stars\n"
                    f"▪️ Username: @{username}\n"
                    f"▪️ Количество: {stars_count}\n"
                    f"▪️ Сумма: {price:,}\n"
                    f"▪️ ID: [{order_id}]</code>\n\n"
                    f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Проверьте данные и подтвердите оплату. Заказ будет автоматически отправлен вам. Если оплата не будет произведена в течение 5 минут, заказ будет автоматически отменен.</b>"
                )

            # Создаем кнопки подтверждения и отмены
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить", callback_data="confirm_stars_payment"),
                    InlineKeyboardButton(text="❌ Bekor qilish" if lang == "uz" else "❌ Отменить", callback_data="cancel_stars_payment")
                ]
            ])

            sent_message = await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
            await state.update_data(confirmation_message_id=sent_message.message_id)
            await state.set_state(OrderStates.waiting_for_payment_confirmation)

            # Запускаем таймер на 5 минут
            asyncio.create_task(cancel_order_after_timeout(message.from_user.id, order_id, state, 300))

        elif category == "premium":
            # Для Premium показываем сводку заказа с кнопками подтверждения
            import random
            import string
            order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            await state.update_data(order_id=order_id)

            if lang == "uz":
                text = (
                    f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>To'lov ma'lumotlari</b>\n\n"
                    f"<code>▪️ Turi: 💎 Telegram Premium\n"
                    f"▪️ Username: @{username}\n"
                    f"▪️ Tarif: {service_name}\n"
                    f"▪️ Summa: {price:,}\n"
                    f"▪️ ID: [{order_id}]</code>\n\n"
                    f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Ma'lumotlarni tekshirib, to'lovni tasdiqlashingiz bilan buyurtma sizga avtomatik yuboriladi, agar to'lov 5 daqiqa ichida amalga oshirilmasa, buyurtma avtomatik ravishda bekor qilinadi.</b>"
                )
            else:
                text = (
                    f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Информация об оплате</b>\n\n"
                    f"<code>▪️ Тип: 💎 Telegram Premium\n"
                    f"▪️ Username: @{username}\n"
                    f"▪️ Тариф: {service_name}\n"
                    f"▪️ Сумма: {price:,}\n"
                    f"▪️ ID: [{order_id}]</code>\n\n"
                    f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Проверьте данные и подтвердите оплату. Заказ будет автоматически отправлен вам. Если оплата не будет произведена в течение 5 минут, заказ будет автоматически отменен.</b>"
                )

            # Создаем кнопки подтверждения и отмены
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить", callback_data="confirm_premium_payment"),
                    InlineKeyboardButton(text="❌ Bekor qilish" if lang == "uz" else "❌ Отменить", callback_data="cancel_premium_payment")
                ]
            ])

            sent_message = await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
            await state.update_data(confirmation_message_id=sent_message.message_id)
            await state.set_state(OrderStates.waiting_for_payment_confirmation)

            # Запускаем таймер на 5 минут
            asyncio.create_task(cancel_order_after_timeout(message.from_user.id, order_id, state, 300))

        else:
            # Для других услуг - старая логика
            if lang == "uz":
                text = (
                    f"✅ <b>Username qabul qilindi!</b>\n\n"
                    f"👤 <b>Username:</b> @{username}\n"
                    f"🛍️ <b>Xizmat:</b> {service_name}\n"
                    f"💰 <b>Summa:</b> <b>{price:,} UZS</b>\n\n"
                    f"👇 <b>To'lov usulini tanlang:</b>"
                )
            else:
                text = (
                    f"✅ <b>Username принят!</b>\n\n"
                    f"👤 <b>Username:</b> @{username}\n"
                    f"🛍️ <b>Услуга:</b> {service_name}\n"
                    f"💰 <b>Сумма:</b> <b>{price:,} UZS</b>\n\n"
                    f"👇 <b>Выберите способ оплаты:</b>"
                )

            await message.answer(text, reply_markup=keyboards.payment_methods(), parse_mode="HTML")
            await state.set_state(None)

# Функция для автоматической отмены заказа через 5 минут
async def cancel_order_after_timeout(user_id, order_id, state: FSMContext, timeout_seconds):
    """Отменить заказ если пользователь не подтвердил оплату за указанное время"""
    await asyncio.sleep(timeout_seconds)
    
    # Проверяем, все ли еще ждем подтверждения
    current_state = await state.get_state()
    if current_state == OrderStates.waiting_for_payment_confirmation:
        data = await state.get_data()
        stored_order_id = data.get('order_id')
        
        # Проверяем что это тот же заказ
        if stored_order_id == order_id:
            lang = database.get_user_language(user_id)
            
            if lang == "uz":
                text = (
                    f"❌ <b>To'lov vaqtda amalga oshirilmagani sababli buyurtma avtomatik ravishda bekor qilindi.</b>\n\n"
                    f"Agar xohlasangiz, buyurtmani qaytadan yaratishingiz mumkin."
                )
            else:
                text = (
                    f"❌ <b>Заказ автоматически отменен из-за неоплаты в срок.</b>\n\n"
                    f"Если хотите, вы можете создать заказ заново."
                )
            
            await bot.send_message(user_id, text, parse_mode="HTML")
            await state.clear()

@dp.callback_query(F.data == "confirm_stars_payment")
async def confirm_stars_payment(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение оплаты Stars - показываем карту и просим отправить чек"""
    lang = database.get_user_language(callback.from_user.id)
    data = await state.get_data()
    price = data.get('price', 0)
    username = data.get('username', '')
    
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Quyidagi kartaga <b>{price:,} so'm</b> yuboring va chekini tashlang..."
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Отправьте <b>{price:,} сум</b> на эту карту и отправьте чек..."
        )
    
    # Удаляем сообщение с кнопками
    try:
        await callback.message.delete()
    except:
        pass
    
    # Отправляем БЕЗ картинки, только текст
    await bot.send_message(callback.from_user.id, text, parse_mode="HTML")
    
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await callback.answer()

@dp.callback_query(F.data == "cancel_stars_payment")
async def cancel_stars_payment(callback: types.CallbackQuery, state: FSMContext):
    """Отмена оплаты Stars"""
    lang = database.get_user_language(callback.from_user.id)
    
    if lang == "uz":
        text = (
            f"❌ <b>Buyurtma bekor qilindi.</b>\n\n"
            f"Agar xohlasangiz, buyurtmani qaytadan yaratishingiz mumkin."
        )
    else:
        text = (
            f"❌ <b>Заказ отменен.</b>\n\n"
            f"Если хотите, вы можете создать заказ заново."
        )
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except:
        await callback.message.answer(text, parse_mode="HTML")
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "confirm_premium_payment")
async def confirm_premium_payment(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение оплаты Premium - показываем карту и просим отправить чек"""
    lang = database.get_user_language(callback.from_user.id)
    data = await state.get_data()
    price = data.get('price', 0)
    username = data.get('username', '')
    
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Quyidagi kartaga <b>{price:,} so'm</b> yuboring va chekini tashlang..."
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Отправьте <b>{price:,} сум</b> на эту карту и отправьте чек..."
        )
    
    # Удаляем сообщение с кнопками
    try:
        await callback.message.delete()
    except:
        pass
    
    # Отправляем БЕЗ картинки, только текст
    await bot.send_message(callback.from_user.id, text, parse_mode="HTML")
    
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await callback.answer()

@dp.callback_query(F.data == "cancel_premium_payment")
async def cancel_premium_payment(callback: types.CallbackQuery, state: FSMContext):
    """Отмена оплаты Premium"""
    lang = database.get_user_language(callback.from_user.id)
    
    if lang == "uz":
        text = (
            f"❌ <b>Buyurtma bekor qilindi.</b>\n\n"
            f"Agar xohlasangiz, buyurtmani qaytadan yaratishingiz mumkin."
        )
    else:
        text = (
            f"❌ <b>Заказ отменен.</b>\n\n"
            f"Если хотите, вы можете создать заказ заново."
        )
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except:
        await callback.message.answer(text, parse_mode="HTML")
    
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "confirm_gift_payment")
async def confirm_gift_payment(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение оплаты Gift - показываем карту и просим отправить чек"""
    lang = database.get_user_language(callback.from_user.id)
    data = await state.get_data()
    price = data.get('price', 0)
    username = data.get('username', '')
    
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Quyidagi kartaga <b>{price:,} so'm</b> yuboring va chekini tashlang..."
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Отправьте <b>{price:,} сум</b> на эту карту и отправьте чек..."
        )
    
    # Удаляем сообщение с кнопками
    try:
        await callback.message.delete()
    except:
        pass
    
    # Отправляем БЕЗ картинки, только текст
    await bot.send_message(callback.from_user.id, text, parse_mode="HTML")
    
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await callback.answer()

@dp.callback_query(F.data == "cancel_gift_payment")
async def cancel_gift_payment(callback: types.CallbackQuery, state: FSMContext):
    """Отмена оплаты Gift"""
    lang = database.get_user_language(callback.from_user.id)
    
    if lang == "uz":
        text = (
            f"❌ <b>Buyurtma bekor qilindi.</b>\n\n"
            f"Agar xohlasangiz, buyurtmani qaytadan yaratishingiz mumkin."
        )
    else:
        text = (
            f"❌ <b>Заказ отменен.</b>\n\n"
            f"Если хотите, вы можете создать заказ заново."
        )
    
    try:
        await callback.message.edit_text(text, parse_mode="HTML")
    except:
        await callback.message.answer(text, parse_mode="HTML")
    
    await state.clear()
    await callback.answer()

@dp.message(OrderStates.waiting_for_message)
async def message_received(message: types.Message, state: FSMContext):
    """Получение сообщения для NFT подарка"""
    lang = database.get_user_language(message.from_user.id)
    gift_message = message.text.strip()

    # Если пользователь отправил "-", считаем сообщение пустым
    if gift_message == "-":
        gift_message = ""

    # Проверяем длину сообщения
    if len(gift_message) > 30:
        if lang == "uz":
            await message.answer(
                "❌ <b>Xabar juda uzun!</b>\n\n"
                "Iltimos, 30 belgidan oshmasligi kerak",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Сообщение слишком длинное!</b>\n\n"
                "Пожалуйста, не более 30 символов",
                parse_mode="HTML"
            )
        return

    # Сохраняем сообщение
    await state.update_data(gift_message=gift_message)

    # Спрашиваем анонимность
    display_message = gift_message if gift_message else "—"
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5364323696397790175\">✅</tg-emoji> <b>Xabar qabul qilindi!</b>\n\n"
            f"<tg-emoji emoji-id=\"5190859184312167965\">💌</tg-emoji> <b>Xabar:</b> {display_message}\n\n"
            f"<tg-emoji emoji-id=\"6039856880224832922\">🤔</tg-emoji> <b>Sovg'ani qanday yuborish kerak?</b>\n\n"
            f"<tg-emoji emoji-id=\"5765140653029724793\">🔒</tg-emoji> <b>Anonim</b> - Kimdanligi ko'rinmaydi\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Anonim emas</b> - Sizning akkauntingizdan"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5364323696397790175\">✅</tg-emoji> <b>Сообщение принято!</b>\n\n"
            f"<tg-emoji emoji-id=\"5190859184312167965\">💌</tg-emoji> <b>Сообщение:</b> {display_message}\n\n"
            f"<tg-emoji emoji-id=\"6039856880224832922\">🤔</tg-emoji> <b>Как отправить подарок?</b>\n\n"
            f"<tg-emoji emoji-id=\"5765140653029724793\">🔒</tg-emoji> <b>Анонимно</b> - Не видно от кого\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Не анонимно</b> - От вашего аккаунта"
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 Anonim / Анонимно", callback_data="anonymous_yes")],
        [InlineKeyboardButton(text="👤 Anonim emas / Не анонимно", callback_data="anonymous_no")],
        [InlineKeyboardButton(text="◀️ Orqaga / Назад", callback_data="back_to_menu")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_anonymous)

@dp.callback_query(F.data.startswith("anonymous_"))
async def anonymous_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор анонимности"""
    anonymous = callback.data.replace("anonymous_", "")
    lang = database.get_user_language(callback.from_user.id)
    
    # Сохраняем выбор
    is_anonymous = anonymous == "yes"
    await state.update_data(is_anonymous=is_anonymous)
    
    data = await state.get_data()
    username = data.get('username', '')
    gift_message = data.get('gift_message', '')
    service_name = data.get('service_name')
    price = data.get('price')
    
    # Генерируем ID заказа
    import random
    import string
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    await state.update_data(order_id=order_id)
    
    # Извлекаем эмодзи подарка из названия
    import re
    emoji_match = re.search(r'([💝🧸🎁🌹🎂🚀🍾💐💎🏆💍])', service_name)
    gift_emoji = emoji_match.group(1) if emoji_match else "🎁"
    
    # Извлекаем количество stars
    stars_match = re.search(r'(\d+)\s*⭐', service_name)
    stars_count = stars_match.group(1) if stars_match else "?"
    
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>To'lov ma'lumotlari</b>\n\n"
            f"<code>▪️Turi: {gift_emoji} Telegram Gift</code>\n"
            f"<code>▪️Username: @{username}</code>\n"
            f"<code>▪️Soni: {stars_count} ⭐️</code>\n"
            f"<code>▪️Summa: {price:,}</code>\n"
            f"<code>▪️ID: [{order_id}]</code>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Ma'lumotlarni tekshirib, to'lovni tasdiqlashingiz bilan buyurtma sizga avtomatik yuboriladi, agar to'lov 5 daqiqa ichida amalga oshirilmasa, buyurtma avtomatik ravishda bekor qilinadi.</b>"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Информация об оплате</b>\n\n"
            f"<code>▪️Тип: {gift_emoji} Telegram Gift</code>\n"
            f"<code>▪️Username: @{username}</code>\n"
            f"<code>▪️Количество: {stars_count} ⭐️</code>\n"
            f"<code>▪️Сумма: {price:,}</code>\n"
            f"<code>▪️ID: [{order_id}]</code>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Проверьте данные и подтвердите оплату. Заказ будет автоматически отправлен вам. Если оплата не будет произведена в течение 5 минут, заказ будет автоматически отменен.</b>"
        )
    
    # Создаем кнопки подтверждения и отмены
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить", callback_data="confirm_gift_payment"),
            InlineKeyboardButton(text="❌ Bekor qilish" if lang == "uz" else "❌ Отменить", callback_data="cancel_gift_payment")
        ]
    ])
    
    await safe_edit_message(callback, text, reply_markup=keyboard)
    await state.set_state(OrderStates.waiting_for_payment_confirmation)
    await callback.answer()
    
    # Запускаем таймер на 5 минут
    asyncio.create_task(cancel_order_after_timeout(callback.from_user.id, order_id, state, 300))

@dp.message(OrderStates.waiting_for_roblox_login)
async def roblox_login_received(message: types.Message, state: FSMContext):
    """Получение логина Roblox"""
    lang = database.get_user_language(message.from_user.id)
    roblox_login = message.text.strip()
    
    # Сохраняем логин
    await state.update_data(roblox_login=roblox_login)
    
    # Запрашиваем пароль
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5460960662421257616\">✅</tg-emoji> <b>Login qabul qilindi!</b>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Login:</b> <code>{roblox_login}</code>\n\n"
            f"<tg-emoji emoji-id=\"5271949146113195081\">🔐</tg-emoji> <b>Endi parolni yuboring:</b>\n"
            f"<tg-emoji emoji-id=\"5317023930236549785\">📌</tg-emoji> <b>Misol: MyPassword123 yoki Roblox@2024</b>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Muhim: Parol faqat administrator ko'radi va xavfsiz saqlanadi</b>"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5460960662421257616\">✅</tg-emoji> <b>Логин принят!</b>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Логин:</b> <code>{roblox_login}</code>\n\n"
            f"<tg-emoji emoji-id=\"5271949146113195081\">🔐</tg-emoji> <b>Теперь отправьте пароль:</b>\n"
            f"<tg-emoji emoji-id=\"5317023930236549785\">📌</tg-emoji> <b>Пример: MyPassword123 или Roblox@2024</b>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Важно: Пароль видит только администратор и хранится безопасно</b>"
        )
    
    await message.answer(text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_roblox_password)

@dp.message(OrderStates.waiting_for_roblox_password)
async def roblox_password_received(message: types.Message, state: FSMContext):
    """Получение пароля Roblox"""
    lang = database.get_user_language(message.from_user.id)
    roblox_password = message.text.strip()
    
    # Удаляем сообщение с паролем для безопасности
    try:
        await message.delete()
    except:
        pass
    
    # Сохраняем пароль
    await state.update_data(roblox_password=roblox_password)
    
    data = await state.get_data()
    roblox_login = data.get('roblox_login', '')
    service_name = data.get('service_name')
    price = data.get('price')
    
    import random, string
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    await state.update_data(order_id=order_id)

    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>To'lov ma'lumotlari</b>\n\n"
            f"<code>▪️ Turi: 💵 Robux\n"
            f"▪️ Login: {roblox_login}\n"
            f"▪️ Xizmat: {service_name}\n"
            f"▪️ Summa: {price:,}\n"
            f"▪️ ID: [{order_id}]</code>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Ma'lumotlarni tekshirib, to'lovni tasdiqlashingiz bilan buyurtma sizga avtomatik yuboriladi, agar to'lov 5 daqiqa ichida amalga oshirilmasa, buyurtma avtomatik ravishda bekor qilinadi.</b>"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Информация об оплате</b>\n\n"
            f"<code>▪️ Тип: 💵 Robux\n"
            f"▪️ Логин: {roblox_login}\n"
            f"▪️ Услуга: {service_name}\n"
            f"▪️ Сумма: {price:,}\n"
            f"▪️ ID: [{order_id}]</code>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Проверьте данные и подтвердите оплату. Заказ будет автоматически отправлен вам. Если оплата не будет произведена в течение 5 минут, заказ будет автоматически отменен.</b>"
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить", callback_data="confirm_robux_payment"),
            InlineKeyboardButton(text="❌ Bekor qilish" if lang == "uz" else "❌ Отменить", callback_data="cancel_robux_payment")
        ]
    ])

    sent = await bot.send_message(message.from_user.id, text, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(confirmation_message_id=sent.message_id)
    await state.set_state(OrderStates.waiting_for_payment_confirmation)
    asyncio.create_task(cancel_order_after_timeout(message.from_user.id, order_id, state, 300))

@dp.message(OrderStates.waiting_for_channel_link)
async def channel_link_received(message: types.Message, state: FSMContext):
    """Получение ссылки на канал для буста"""
    lang = database.get_user_language(message.from_user.id)
    channel_link = message.text.strip()

    await state.update_data(channel_link=channel_link)
    data = await state.get_data()
    service_name = data.get('service_name', '')
    price = data.get('price', 0)

    import random, string
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    await state.update_data(order_id=order_id)

    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>To'lov ma'lumotlari</b>\n\n"
            f"<code>▪️ Turi: ⚡️ Telegram Boost\n"
            f"▪️ Kanal: {channel_link}\n"
            f"▪️ Tarif: {service_name}\n"
            f"▪️ Summa: {price:,}\n"
            f"▪️ ID: [{order_id}]</code>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Ma'lumotlarni tekshirib, to'lovni tasdiqlashingiz bilan buyurtma sizga avtomatik yuboriladi, agar to'lov 5 daqiqa ichida amalga oshirilmasa, buyurtma avtomatik ravishda bekor qilinadi.</b>"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Информация об оплате</b>\n\n"
            f"<code>▪️ Тип: ⚡️ Telegram Boost\n"
            f"▪️ Канал: {channel_link}\n"
            f"▪️ Тариф: {service_name}\n"
            f"▪️ Сумма: {price:,}\n"
            f"▪️ ID: [{order_id}]</code>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Проверьте данные и подтвердите оплату. Заказ будет автоматически отправлен вам. Если оплата не будет произведена в течение 5 минут, заказ будет автоматически отменен.</b>"
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash" if lang == "uz" else "✅ Подтвердить", callback_data="confirm_boost_payment"),
            InlineKeyboardButton(text="❌ Bekor qilish" if lang == "uz" else "❌ Отменить", callback_data="cancel_boost_payment")
        ]
    ])

    sent_message = await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(confirmation_message_id=sent_message.message_id)
    await state.set_state(OrderStates.waiting_for_payment_confirmation)
    asyncio.create_task(cancel_order_after_timeout(message.from_user.id, order_id, state, 300))

@dp.callback_query(F.data == "confirm_boost_payment")
async def confirm_boost_payment(callback: types.CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)
    data = await state.get_data()
    price = data.get('price', 0)

    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Quyidagi kartaga <b>{price:,} so'm</b> yuboring va chekini tashlang..."
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Отправьте <b>{price:,} сум</b> на эту карту и отправьте чек..."
        )

    try:
        await callback.message.delete()
    except:
        pass

    await bot.send_message(callback.from_user.id, text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await callback.answer()

@dp.callback_query(F.data == "cancel_boost_payment")
async def cancel_boost_payment(callback: types.CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    if lang == "uz":
        await callback.message.answer("❌ <b>Buyurtma bekor qilindi</b>", reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    else:
        await callback.message.answer("❌ <b>Заказ отменен</b>", reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "confirm_robux_payment")
async def confirm_robux_payment(callback: types.CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)
    data = await state.get_data()
    price = data.get('price', 0)

    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Quyidagi kartaga <b>{price:,} so'm</b> yuboring va chekini tashlang..."
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <code>9860 1801 0171 2578</code>\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Isxakova A.</b>\n\n"
            f"Отправьте <b>{price:,} сум</b> на эту карту и отправьте чек..."
        )

    try:
        await callback.message.delete()
    except:
        pass

    await bot.send_message(callback.from_user.id, text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await callback.answer()

@dp.callback_query(F.data == "cancel_robux_payment")
async def cancel_robux_payment(callback: types.CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    if lang == "uz":
        await callback.message.answer("❌ <b>Buyurtma bekor qilindi</b>", reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    else:
        await callback.message.answer("❌ <b>Заказ отменен</b>", reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    await callback.answer()

@dp.message(OrderStates.waiting_for_stars_count)
async def stars_count_received(message: types.Message, state: FSMContext):
    """Получение количества stars"""
    lang = database.get_user_language(message.from_user.id)
    
    try:
        stars_count = int(message.text.strip())
    except ValueError:
        if lang == "uz":
            await message.answer(
                "❌ <b>Noto'g'ri format!</b>\n\n"
                "Iltimos, faqat raqam yuboring.\n"
                "Misol: 100 yoki 500",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Неверный формат!</b>\n\n"
                "Пожалуйста, отправьте только число.\n"
                "Пример: 100 или 500",
                parse_mode="HTML"
            )
        return
    
    # Проверяем диапазон
    if stars_count < 50:
        if lang == "uz":
            await message.answer(
                "❌ <b>Minimal miqdor 50 stars!</b>\n\n"
                "Iltimos, 50 yoki undan ko'p son kiriting.",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Минимальное количество 50 stars!</b>\n\n"
                "Пожалуйста, введите 50 или больше.",
                parse_mode="HTML"
            )
        return
    
    if stars_count > 1000000:
        if lang == "uz":
            await message.answer(
                "❌ <b>Maksimal miqdor <code>1 000 000</code> stars!</b>\n\n"
                "Iltimos, <code>1 000 000</code> yoki undan kam son kiriting.",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Максимальное количество <code>1 000 000</code> stars!</b>\n\n"
                "Пожалуйста, введите <code>1 000 000</code> или меньше.",
                parse_mode="HTML"
            )
        return
    
    # Рассчитываем сумму
    price_per_star = 245
    total_price = stars_count * price_per_star
    
    # Сохраняем количество и общую сумму
    await state.update_data(
        stars_count=stars_count,
        price=total_price
    )
    
    data = await state.get_data()
    service_name = data.get('service_name', 'Stars')
    
    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"4965219701572503640\">💰</tg-emoji> <b>1 star narxi: 245 so'm</b>\n"
            f"<tg-emoji emoji-id=\"4920593664222168414\">🌟</tg-emoji> <b>{stars_count} stars = {total_price:,} so'm bo'ladi</b>\n\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Qaysi profilga olasiz? Username yozing...</b>\n"
            f"<tg-emoji emoji-id=\"5458382591121964689\">✍️</tg-emoji> <b>Format: @username yoki username</b>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Muhim: Stars shu akkauntga yuboriladi</b>"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"4965219701572503640\">💰</tg-emoji> <b>Цена 1 star: 245 сум</b>\n"
            f"<tg-emoji emoji-id=\"4920593664222168414\">🌟</tg-emoji> <b>{stars_count} stars = {total_price:,} сум</b>\n\n"
            f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>На какой профиль? Напишите username...</b>\n"
            f"<tg-emoji emoji-id=\"5458382591121964689\">✍️</tg-emoji> <b>Формат: @username или username</b>\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Важно: Stars будет отправлен на этот аккаунт</b>"
        )
    
    await message.answer(text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_username)

@dp.callback_query(F.data.startswith("payment_"))
async def payment_selected(callback: types.CallbackQuery, state: FSMContext):
    payment_method = callback.data.replace("payment_", "")
    lang = database.get_user_language(callback.from_user.id)
    data = await state.get_data()
    service_name = data.get('service_name', 'Xizmat')
    price = data.get('price', 0)
    phone_number = data.get('phone_number', '')
    category = data.get('category', '')
    stars_count = data.get('stars_count', 0)
    
    # Красивое сообщение с реквизитами и премиум эмодзи
    if lang == "uz":
        payment_info = (
            f"💎 <b>TRASTBANK — To'lov va rekvizitlar</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇺🇿 ️ <b>To'lov shartlari:</b>\n\n"
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Karta raqami:</b>\n"
            f"<code>{config.CARD_NUMBER}</code>\n\n"
            f"🟢 <b>Karta egasi:</b> {config.CARD_OWNER}\n"
            f"📞 <b>Kartaga ulangan raqam:</b>\n"
            f"<code>{config.CARD_PHONE}</code>\n\n"
            f"🛍️ <b>Xizmat:</b> {service_name}\n"
        )
        
        # Для Stars добавляем детальную информацию
        if category == "stars" and stars_count > 0:
            payment_info += (
                f"🌟 <b>Stars soni:</b> {stars_count} ta\n"
                f"💰 <b>1 star narxi:</b> 245 so'm\n"
                f"💰 <b>Jami summa:</b> <b>{price:,} so'm</b>\n"
            )
        else:
            payment_info += f"💰 <b>To'lov summasi:</b> <b>{price:,} UZS</b>\n"
        
        if phone_number:
            payment_info += f"📱 <b>Sizning raqamingiz:</b> <code>{phone_number}</code>\n"
        
        payment_info += (
            f"\n🧾 <b>To'lov limiti:</b> 0 so'm\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Muhim!</b>\n"
            f"• To'lov qilayotganda bank komissiyasiga albatta e'tibor bering — summa to'liq tushishi shart.\n"
            f"❗ To'lovdan so'ng 12 soat ichida chek adminga yuborilmasa, mablag' qaytarilmaydi.\n\n"
            f"📸 <b>To'lov chekini shu chatga yuboring!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Aloqa:</b> @Star_payuz_admin\n"
            f"🤖 <b>Karta bot:</b> {config.CARD_BOT}"
        )
    else:
        payment_info = (
            f"💎 <b>TRASTBANK — Оплата и реквизиты</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇺🇿 ️<b>Условия оплаты:</b>\n\n"
            f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> <b>Номер карты:</b>\n"
            f"<code>{config.CARD_NUMBER}</code>\n\n"
            f"🟢 <b>Владелец карты:</b> {config.CARD_OWNER}\n"
            f"📞 <b>Номер привязанный к карте:</b>\n"
            f"<code>{config.CARD_PHONE}</code>\n\n"
            f"🛍️ <b>Услуга:</b> {service_name}\n"
        )
        
        # Для Stars добавляем детальную информацию
        if category == "stars" and stars_count > 0:
            payment_info += (
                f"🌟 <b>Количество stars:</b> {stars_count} шт\n"
                f"💰 <b>Цена 1 star:</b> 245 сум\n"
                f"💰 <b>Общая сумма:</b> <b>{price:,} сум</b>\n"
            )
        else:
            payment_info += f"💰 <b>Сумма к оплате:</b> <b>{price:,} UZS</b>\n"
        
        if phone_number:
            payment_info += f"📱 <b>Ваш номер:</b> <code>{phone_number}</code>\n"
        
        payment_info += (
            f"\n🧾 <b>Лимит оплаты:</b> 0 сум\n\n"
            f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Важно!</b>\n"
            f"• При оплате обязательно учитывайте комиссию банка — сумма должна поступить полностью.\n"
            f"❗ Если чек не будет отправлен админу в течение 12 часов после оплаты, средства не возвращаются.\n\n"
            f"📸 <b>Отправьте чек оплаты в этот чат!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Связь:</b> @Star_payuz_admin\n"
            f"🤖 <b>Карта бот:</b> {config.CARD_BOT}"
        )
    
    # Пробуем отправить с картинкой карты
    try:
        import os
        if hasattr(config, 'CARD_IMAGE') and os.path.exists(config.CARD_IMAGE):
            photo = types.FSInputFile(config.CARD_IMAGE)
            # удаляем старое сообщение, отправляем новое с фото
            try:
                await callback.message.delete()
            except Exception:
                pass
            await bot.send_photo(
                callback.from_user.id,
                photo=photo,
                caption=payment_info,
                parse_mode="HTML"
            )
        else:
            # если картинки нет – просто обновляем подпись/текст
            try:
                await safe_edit_message(callback, payment_info)
            except Exception:
                await callback.message.answer(payment_info, parse_mode="HTML")
    except Exception as e:
        # если произошла любая ошибка с отправкой фото – логируем и шлём текст отдельным сообщением
        logging.error(f"Card image error: {e}")
        await bot.send_message(callback.from_user.id, payment_info, parse_mode="HTML")
    
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await state.update_data(payment_method=payment_method)
    await callback.answer()

@dp.message(OrderStates.waiting_for_payment_proof)
async def payment_proof_received(message: types.Message, state: FSMContext):
    lang = database.get_user_language(message.from_user.id)
    data = await state.get_data()
    payment_method = data.get('payment_method', 'unknown')
    product_id = data.get('product_id', 0)
    category = data.get('category', 'unknown')
    service_name = data.get('service_name', 'Xizmat')
    price = data.get('price', 0)
    phone_number = data.get('phone_number', '')
    username = data.get('username', '')
    gift_message = data.get('gift_message', '')
    is_anonymous = data.get('is_anonymous', False)
    stars_count = data.get('stars_count', 0)
    channel_link = data.get('channel_link', '')

    order_id = database.create_order(message.from_user.id, service_name, price, payment_method)

    # Отправляем подтверждение пользователю
    await message.answer(get_premium_order_accepted(order_id, lang), reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")

    # Уведомление админам
    for admin_id in config.ADMIN_IDS:
        try:
            if lang == "uz":
                admin_caption = (
                    f"📝 <b>Buyurtma #{order_id}</b>\n\n"
                    f"👤 Foydalanuvchi: @{message.from_user.username or 'username yoq'}\n"
                    f"🛍️ Xizmat: <b>{service_name}</b>\n"
                )
            else:
                admin_caption = (
                    f"📝 <b>Заказ #{order_id}</b>\n\n"
                    f"👤 Пользователь: @{message.from_user.username or 'username yoq'}\n"
                    f"🛍️ Услуга: <b>{service_name}</b>\n"
                )

            # Для Stars добавляем информацию о количестве
            if category == "stars" and stars_count > 0:
                if lang == "uz":
                    admin_caption += f"⭐️ Stars soni: {stars_count} ta\n"
                    admin_caption += f"💵 1 star narxi: 245 so'm\n"
                    admin_caption += f"💰 Jami summa: {price:,} so'm\n"
                else:
                    admin_caption += f"⭐️ Количество Stars: {stars_count}\n"
                    admin_caption += f"💵 Цена 1 star: 245 сум\n"
                    admin_caption += f"💰 Сумма: {price:,} сум\n"
            else:
                if lang == "uz":
                    admin_caption += f"💰 Summa: {price:,} UZS\n"
                else:
                    admin_caption += f"💰 Сумма: {price:,} UZS\n"

            # Способ оплаты
            payment_method_name = config.PAYMENT_METHODS.get(payment_method, payment_method)
            if lang == "uz":
                admin_caption += f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> To'lov usuli: {payment_method_name}\n"
            else:
                admin_caption += f"<tg-emoji emoji-id=\"5472250091332993630\">💳</tg-emoji> Способ оплаты: {payment_method_name}\n"

            # Если есть номер телефона (для Premium)
            if phone_number:
                if lang == "uz":
                    admin_caption += f"📱 Telefon: <code>{phone_number}</code>\n"
                else:
                    admin_caption += f"📱 Телефон: <code>{phone_number}</code>\n"

            # Если есть username (для Stars или NFT)
            if username:
                if lang == "uz":
                    admin_caption += f"👤 Username: @{username}\n"
                else:
                    admin_caption += f"👤 Username: @{username}\n"

            # Если есть ссылка на канал (для Boost)
            if channel_link:
                if lang == "uz":
                    admin_caption += f"🔗 Kanal: {channel_link}\n"
                else:
                    admin_caption += f"🔗 Канал: {channel_link}\n"

            # Если есть данные Roblox
            roblox_login = data.get('roblox_login', '')
            roblox_password = data.get('roblox_password', '')
            if roblox_login:
                admin_caption += f"👤 Roblox Login: <code>{roblox_login}</code>\n"
            if roblox_password:
                admin_caption += f"🔐 Roblox Parol: <code>{roblox_password}</code>\n"

            # Если есть сообщение (для NFT подарков)
            if gift_message:
                if lang == "uz":
                    admin_caption += f"💌 Xabar: {gift_message}\n"
                else:
                    admin_caption += f"💌 Сообщение: {gift_message}\n"

            # Если есть выбор анонимности (для Gifts подарков)
            if category == "gifts":
                if lang == "uz":
                    admin_caption += f"🔒 Anonim: {'Ha' if is_anonymous else 'Yoq'}\n"
                else:
                    admin_caption += f"🔒 Анонимно: {'Да' if is_anonymous else 'Нет'}\n"

            if lang == "uz":
                admin_caption += f"📅 Sana: {message.date.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                admin_caption += f"📅 Дата: {message.date.strftime('%Y-%m-%d %H:%M:%S')}"

            # Проверяем есть ли фото
            if message.photo:
                await bot.send_photo(
                    admin_id,
                    photo=message.photo[-1].file_id,
                    caption=admin_caption,
                    reply_markup=keyboards.order_actions(order_id),
                    parse_mode="HTML"
                )
            else:
                # Если нет фото, отправляем текстовое сообщение
                await bot.send_message(
                    admin_id,
                    admin_caption,
                    reply_markup=keyboards.order_actions(order_id),
                    parse_mode="HTML"
                )
        except Exception as e:
            logging.error(f"Admin notification error: {e}")

    await state.clear()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    user_mention = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
    welcome_text = get_premium_welcome(user_mention, lang)
    try:
        await safe_edit_message(callback, welcome_text, reply_markup=keyboards.main_menu(lang))
    except:
        await callback.message.delete()
        try:
            if hasattr(config, 'BANNER_FILE'):
                with open(config.BANNER_FILE, 'rb') as photo:
                    await bot.send_photo(callback.from_user.id, photo=photo, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
            else:
                await bot.send_photo(callback.from_user.id, photo=config.BANNER_URL, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
        except Exception as e:
            logging.error(f"Banner error: {e}")
            await bot.send_message(callback.from_user.id, welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("category_"))
async def category_selected(callback: types.CallbackQuery):
    """Выбор категории товаров"""
    category = callback.data.replace("category_", "")
    lang = database.get_user_language(callback.from_user.id)
    
    # Получаем товары из базы данных
    products = database.get_products_by_category(category)
    
    if not products:
        if lang == "uz":
            text = "<b><tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> Bu kategoriyada hozircha mahsulotlar mavjud emas</b>"
        else:
            text = "<b><tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> В этой категории пока нет товаров</b>"
        
        await safe_edit_message(callback, text, reply_markup=keyboards.back_to_menu(lang))
        await callback.answer()
        return
    
    # Особый формат для Premium категории
    if category == "premium":
        await show_premium_menu(callback, products, lang)
        return
    
    # Особый формат для Stars категории
    if category == "stars":
        await show_stars_menu(callback, products, lang)
        return
    
    # Особый формат для Gifts категории
    if category == "gifts":
        await show_gifts_menu(callback, products, lang)
        return
    
    # Особый формат для Boost категории
    if category == "boost":
        await show_boost_menu(callback, products, lang)
        return

    # Особый формат для Robux категории
    if category == "robux":
        await show_robux_menu(callback, products, lang)
        return

    # Получаем название категории
    category_names = {
        "premium": "💎 Premium" if lang == "uz" else "💎 Premium",
        "stars": "🌟 Stars" if lang == "uz" else "🌟 Stars",
        "boost": "⚡️ Boost" if lang == "uz" else "⚡️ Boost",
        "gifts": "🎁 Gifts" if lang == "uz" else "🎁 Gifts",
        "virtual_numbers": "📱 Virtual numbers" if lang == "uz" else "📱 Виртуальные номера",
        "robux": "🎮 Robux" if lang == "uz" else "🎮 Robux"
    }
    
    category_name = category_names.get(category, category)
    
    if lang == "uz":
        text = f"<b>{category_name}</b>\n\n<b>👇 Kerakli mahsulotni tanlang:</b>"
    else:
        text = f"<b>{category_name}</b>\n\n<b>👇 Выберите нужный товар:</b>"
    
    # Вместо редактирования существующего сообщения, отправляем новое
    # и удаляем старое
    try:
        await callback.message.delete()
    except:
        pass  # Игнорируем ошибку, если не можем удалить
    
    # Отправляем новое сообщение
    await callback.message.answer(
        text,
        reply_markup=keyboards.products_keyboard(products, lang),
        parse_mode="HTML"
    )
    await callback.answer()

async def show_premium_menu(callback: types.CallbackQuery, products, lang):
    """Показать простое меню Premium"""
    # Отвечаем на callback сразу, чтобы избежать таймаута
    await callback.answer()
    
    if lang == "uz":
        text = (
            "<tg-emoji emoji-id=\"6271537028307881531\">💎</tg-emoji> <b>Telegram Premium tariflari</b>\n\n"
            "<tg-emoji emoji-id=\"5460734485148483248\">✨</tg-emoji> <code>1 oylik va 1 yillik</code> — <b>profilga kirib olinadi</b>\n\n"
            "<tg-emoji emoji-id=\"5427225953463972959\">🎁</tg-emoji> <code>3 oylik</code> — <b>gift sifatida yuboriladi</b>\n"
            "<tg-emoji emoji-id=\"5429263077927300012\">🎁</tg-emoji> <code>6 oylik</code> — <b>gift sifatida yuboriladi</b>\n"
            "<tg-emoji emoji-id=\"5427315847129478207\">🎁</tg-emoji> <code>12 oylik</code> — <b>gift sifatida yuboriladi</b>\n\n"
            "<tg-emoji emoji-id=\"5765140653029724793\">🔒</tg-emoji> <b>Profilga kirish talab qilinmaydi</b>\n\n"
            "<tg-emoji emoji-id=\"6271712920103555728\">👇</tg-emoji> <b>Kerakli tarifni tanlang</b>"
        )
    else:
        text = (
            "<tg-emoji emoji-id=\"6271537028307881531\">💎</tg-emoji> <b>Telegram Premium тарифы</b>\n\n"
            "<tg-emoji emoji-id=\"5460734485148483248\">✨</tg-emoji> <code>1 месяц и 1 год</code> — <b>вход в профиль</b>\n\n"
            "<tg-emoji emoji-id=\"5427225953463972959\">🎁</tg-emoji> <code>3 месяца</code> — <b>отправляется как подарок</b>\n"
            "<tg-emoji emoji-id=\"5429263077927300012\">🎁</tg-emoji> <code>6 месяцев</code> — <b>отправляется как подарок</b>\n"
            "<tg-emoji emoji-id=\"5427315847129478207\">🎁</tg-emoji> <code>12 месяцев</code> — <b>отправляется как подарок</b>\n\n"
            "<tg-emoji emoji-id=\"5765140653029724793\">🔒</tg-emoji> <b>Вход в профиль не требуется</b>\n\n"
            "<tg-emoji emoji-id=\"6271712920103555728\">👇</tg-emoji> <b>Выберите нужный тариф</b>"
        )
    
    # Создаем клавиатуру с товарами (1 кнопка в ряд для мобильных)
    keyboard_buttons = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        name = name_uz if lang == "uz" else name_ru
        
        # Сокращаем название для кнопки и добавляем цену
        # Используем индекс для определения типа эмодзи
        product_index = len(keyboard_buttons)
        
        if "1 oylik" in name_uz or ("1 месяц" in name_ru and "с аккаунтом" in (desc_ru or "")):
            display_name = "1 oy" if lang == "uz" else "1 месяц"
            button_text = f"💎 {display_name} - {price:,} UZS"
        elif "12 oylik" in name_uz or ("12 месяцев" in name_ru and "с аккаунтом" in (desc_ru or "")):
            # 12 месяцев (с аккаунтом) — алмаз
            display_name = "12 oylik" if lang == "uz" else "12 месяцев"
            button_text = f"💎 {display_name} - {price:,} UZS"
        elif "3 oylik" in name_uz or "3 месяца" in name_ru:
            display_name = "3 oy" if lang == "uz" else "3 месяца"
            button_text = f"🎁 {display_name} - {price:,} UZS"
        elif "6 oylik" in name_uz or "6 месяцев" in name_ru:
            display_name = "6 oy" if lang == "uz" else "6 месяцев"
            button_text = f"🎁 {display_name} - {price:,} UZS"
        elif "12 oy" in name_uz or ("12 месяцев" in name_ru and "без аккаунта" in (desc_ru or "")):
            # 12 месяцев (без аккаунта) — подарок (это как раз 370 000 UZS)
            display_name = "12 oy" if lang == "uz" else "12 месяцев"
            button_text = f"🎁 {display_name} - {price:,} UZS"
        else:
            # Убираем скобки с типом для кнопки
            clean_name = name.replace("(Akkaunt orqali)", "").replace("(Через аккаунт)", "").replace("(Akkauntsiz)", "").replace("(Без аккаунта)", "").strip()
            button_text = f"{clean_name} - {price:,} UZS"
        
        # 1 кнопка в ряд для мобильных
        keyboard_buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}")])
    
    # Добавляем кнопку назад
    keyboard_buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Пробуем отправить фото premium.png если файл существует
    try:
        await callback.message.delete()
    except:
        pass
    
    try:
        # Отправляем фото с текстом и клавиатурой
        await callback.message.answer_photo(
            photo=FSInputFile("premium.png"),
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        # Если фото не найдено, отправляем просто текст
        logging.error(f"Failed to send premium photo: {e}")
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
    await callback.answer()

async def show_stars_menu(callback: types.CallbackQuery, products, lang):
    """Показать специальное меню для Stars"""
    # Отвечаем на callback сразу, чтобы избежать таймаута
    await callback.answer()
    
    if lang == "uz":
        text = (
            "<tg-emoji emoji-id=\"5951810621887484519\">⭐️</tg-emoji> <b>Telegram Stars</b>\n\n"
            "<code>1 star = 245 so'm\n"
            "Min: 50 | Max: 1000000</code>\n\n"
            "<tg-emoji emoji-id=\"6269085886177087845\">➡️</tg-emoji> Tanlang:"
        )
    else:
        text = (
            "<tg-emoji emoji-id=\"5951810621887484519\">⭐️</tg-emoji> <b>Telegram Stars</b>\n\n"
            "<code>1 star = 245 сум\n"
            "Мин: 50 | Макс: 1000000</code>\n\n"
            "<tg-emoji emoji-id=\"6269085886177087845\">➡️</tg-emoji> Выберите:"
        )
    
    # Создаем клавиатуру с товарами (1 кнопка в ряд для мобильных)
    keyboard_buttons = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        name = name_uz if lang == "uz" else name_ru
        
        # Сокращаем название для кнопки и добавляем цену
        if "100 Stars" in name_uz or "100 Stars" in name_ru:
            display_name = "100"
            button_text = f"⭐ {display_name} stars — {price:,} UZS"
        elif "500 Stars" in name_uz or "500 Stars" in name_ru:
            display_name = "500"
            button_text = f"⭐ {display_name} stars — {price:,} UZS"
        elif "1000 Stars" in name_uz or "1000 Stars" in name_ru:
            display_name = "1000"
            button_text = f"⭐ {display_name} stars — {price:,} UZS"
        else:
            # Убираем скобки с типом для кнопки и звезды
            clean_name = name.replace("(sotib olish)", "").replace("(покупка)", "").replace("(sotish)", "").replace("(продажа)", "").replace("⭐", "").strip()
            button_text = f"⭐ {clean_name} — {price:,} UZS"
        
        # 1 кнопка в ряд для мобильных
        keyboard_buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}")])
    
    # Добавляем специальную кнопку для покупки произвольного количества
    if lang == "uz":
        custom_button_text = "⭐ Boshqa miqdor"
    else:
        custom_button_text = "⭐ Другое кол-во"
    
    keyboard_buttons.append([InlineKeyboardButton(text=custom_button_text, callback_data="custom_stars")])
    
    # Добавляем кнопку назад
    keyboard_buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Вместо редактирования, отправляем фото с подписью
    try:
        await callback.message.delete()
    except:
        pass  # Игнорируем ошибку, если не можем удалить
    
    # Проверяем, существует ли файл stars.png
    import os
    if hasattr(config, 'STARS_PHOTO') and os.path.exists(config.STARS_PHOTO):
        # Отправляем фото с подписью
        photo = types.FSInputFile(config.STARS_PHOTO)
        await bot.send_photo(
            callback.from_user.id,
            photo=photo,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Если фото нет, отправляем текстовое сообщение
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_gifts_menu(callback: types.CallbackQuery, products, lang):
    """Показать специальное меню для Gifts с эмодзи"""
    # Отвечаем на callback сразу, чтобы избежать таймаута
    await callback.answer()
    
    if lang == "uz":
        text = (
            "<tg-emoji emoji-id=\"5193085063998224234\">🎁</tg-emoji> <b>Telegram Gifts</b>\n\n"
            "<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> Giftlarni starsga almashtirish mumkun\n"
            "Profil orqali jonatiladi\n\n"
            "<tg-emoji emoji-id=\"5460704794039566340\">🔐</tg-emoji> Admini profili orqali\n"
            "@StarPayUzAdmin dan\n\n"
            "<tg-emoji emoji-id=\"6158862632926319619\">👉</tg-emoji> Kerakli tugmani tanlang:"
        )
    else:
        text = (
            "<tg-emoji emoji-id=\"5193085063998224234\">🎁</tg-emoji> <b>Telegram Gifts</b>\n\n"
            "<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> Подарки можно обменять на stars\n"
            "Отправляются через профиль\n\n"
            "<tg-emoji emoji-id=\"5460704794039566340\">🔐</tg-emoji> Через профиль администратора\n"
            "@StarPayUzAdmin\n\n"
            "<tg-emoji emoji-id=\"6158862632926319619\">👉</tg-emoji> Выберите нужный подарок:"
        )
    
    # Маппинг подарков на премиум эмодзи ID
    gift_emoji_ids = {
        13: [("💝", "5283228279988309088"), ("🧸", "5397915559037785261")],
        21: [("🎁", "5199749070830197566"), ("🌹", "5280947338821524402")],
        43: [("🎂", "5280659198055572187"), ("🚀", "5445284980978621387"), ("🍾", "5451905784734574339"), ("💐", "5280774333243873175")],
        85: [("💎", "5368343974765411150"), ("🏆", "5280769763398671636"), ("💍", "5402100905883488232")]
    }
    
    # Счетчики для каждого количества stars
    counters = {}
    
    # Создаем кнопки - по 2 в ряд
    buttons = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        
        import re
        match = re.search(r'(\d+)\s*⭐', name_uz)
        if not match:
            match = re.search(r'(\d+)\s*stars', name_uz.lower())
        
        if match:
            stars_count = int(match.group(1))
            idx = counters.get(stars_count, 0)
            counters[stars_count] = idx + 1
            
            emoji_list = gift_emoji_ids.get(stars_count, [("🎁", "")])
            emoji_char = emoji_list[idx % len(emoji_list)][0]
            button_text = f"{emoji_char} {stars_count} ⭐ — {price:,}"
        else:
            button_text = f"🎁 {name_uz if lang == 'uz' else name_ru} — {price:,}"
        
        buttons.append(InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}"))
    
    # Группируем по 2 в ряд
    keyboard_buttons = []
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard_buttons.append(row)
    
    # Добавляем кнопку назад
    from translations import get_text_simple
    keyboard_buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Удаляем старое сообщение и отправляем новое
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def show_boost_menu(callback: types.CallbackQuery, products, lang):
    """Показать специальное меню для Boost"""
    # Отвечаем на callback сразу, чтобы избежать таймаута
    await callback.answer()
    
    if lang == "uz":
        text = (
            "<tg-emoji emoji-id=\"6269267069372469947\">✅</tg-emoji> <b>Telegram Boost</b>\n\n"
            "<tg-emoji emoji-id=\"6269085886177087845\">💰</tg-emoji> <b>Kanalga boost qo'shish</b>\n\n"
            "<tg-emoji emoji-id=\"5440410042773824003\">🔗</tg-emoji> <b>Vaqt:</b> 1 kun = 1 000 UZS\n"
            "<tg-emoji emoji-id=\"5317023930236549785\">📌</tg-emoji> <b>Min:</b> 10 ta boost\n\n"
            "<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> Boost shu kanalga qo'llaniladi"
        )
    else:
        text = (
            "<tg-emoji emoji-id=\"6269267069372469947\">✅</tg-emoji> <b>Telegram Boost</b>\n\n"
            "<tg-emoji emoji-id=\"6269085886177087845\">💰</tg-emoji> <b>Буст для канала</b>\n\n"
            "<tg-emoji emoji-id=\"5440410042773824003\">🔗</tg-emoji> <b>Время:</b> 1 день = 1 000 UZS\n"
            "<tg-emoji emoji-id=\"5317023930236549785\">📌</tg-emoji> <b>Мин:</b> 10 бустов\n\n"
            "<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> Буст применится к каналу"
        )
    
    # Создаем клавиатуру с товарами (1 кнопка в ряд для мобильных)
    keyboard_buttons = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        name = name_uz if lang == "uz" else name_ru
        
        # Форматируем кнопку - убираем эмодзи из name так как там уже есть ⚡️
        clean_name = name.replace("⚡️", "").replace("⚡", "").strip()
        button_text = f"⚡️ {clean_name} — {price:,} UZS"
        
        # 1 кнопка в ряд для мобильных
        keyboard_buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}")])
    
    # Добавляем кнопку назад
    from translations import get_text_simple
    keyboard_buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Удаляем старое сообщение и отправляем новое
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def show_robux_menu(callback: types.CallbackQuery, products, lang):
    """Показать специальное меню для Robux"""
    await callback.answer()

    text = (
        "<tg-emoji emoji-id=\"5458649351540712147\">💵</tg-emoji> <b>Robux</b>\n\n"
        "<tg-emoji emoji-id=\"5460952046716860045\">🔜</tg-emoji> <b>Kerakli mahsulotni tanlang:</b>"
    )

    keyboard_buttons = []
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        name = name_uz if lang == "uz" else name_ru
        keyboard_buttons.append([InlineKeyboardButton(text=f"{name} — {price:,} UZS", callback_data=f"product_{product_id}")])

    from translations import get_text_simple
    keyboard_buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@dp.callback_query(F.data == "custom_stars")
async def custom_stars_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор покупки произвольного количества stars"""
    lang = database.get_user_language(callback.from_user.id)

    if lang == "uz":
        text = (
            "<tg-emoji emoji-id=\"4965219701572503640\">💰</tg-emoji> <b>Kerakli Stars miqdorini kiriting</b>\n"
            "<tg-emoji emoji-id=\"5458382591121964689\">✍️</tg-emoji> <b>Masalan: <code>100, 250, 1000</code></b>\n"
            "<tg-emoji emoji-id=\"5201873447554145566\">💵</tg-emoji> <b>1 <tg-emoji emoji-id=\"5897920748101571572\">🌟</tg-emoji> = 245 so'm</b>\n"
            "<tg-emoji emoji-id=\"5460991276948143687\">⚡️</tg-emoji> <b>Narx avtomatik hisoblanadi va sizga ko'rsatiladi</b>"
        )
    else:
        text = (
            "<tg-emoji emoji-id=\"4965219701572503640\">💰</tg-emoji> <b>Введите нужное количество Stars</b>\n"
            "<tg-emoji emoji-id=\"5458382591121964689\">✍️</tg-emoji> <b>Например: <code>100, 250, 1000</code></b>\n"
            "<tg-emoji emoji-id=\"5201873447554145566\">💵</tg-emoji> <b>1 <tg-emoji emoji-id=\"5897920748101571572\">🌟</tg-emoji> = 245 сум</b>\n"
            "<tg-emoji emoji-id=\"5460991276948143687\">⚡️</tg-emoji> <b>Цена будет автоматически рассчитана и показана вам</b>"
        )

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state(OrderStates.waiting_for_stars_count)
    await state.update_data(
        category="stars",
        service_name="🌟 Stars (произвольное количество)" if lang == "ru" else "🌟 Stars (boshqa miqdor)"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("product_"))
async def product_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор товара"""
    product_id = int(callback.data.replace("product_", ""))
    lang = database.get_user_language(callback.from_user.id)

    # Получаем информацию о товаре
    product = database.get_product(product_id)

    if not product:
        if lang == "uz":
            text = "❌ <b>Bu mahsulot topilmadi</b>"
        else:
            text = "❌ <b>Этот товар не найден</b>"

        await safe_edit_message(callback, text, reply_markup=keyboards.back_to_menu(lang))
        await callback.answer()
        return

    product_id, category, name_uz, name_ru, desc_uz, desc_ru, price, is_active = product

    # Проверяем активен ли товар
    if not is_active:
        if lang == "uz":
            text = "❌ <b>Bu mahsulot hozircha mavjud emas</b>"
        else:
            text = "❌ <b>Этот товар временно недоступен</b>"

        await safe_edit_message(callback, text, reply_markup=keyboards.back_to_menu(lang))
        await callback.answer()
        return

    # Выбираем название и описание на нужном языке
    name = name_uz if lang == "uz" else name_ru
    description = desc_uz if lang == "uz" else desc_ru

    # Для Stars - особый формат текста
    if category == "stars":
        # Определяем количество stars
        from config import STARS_PRICES
        stars_count = 0
        for qty, star_price in STARS_PRICES.items():
            if star_price == price:
                stars_count = qty
                break

        if stars_count == 0:
            import re
            match = re.search(r"(\d+)", name)
            if match:
                stars_count = int(match.group(1))

        # Формируем продающий текст для Stars
        if lang == "uz":
            text = (
                f"<tg-emoji emoji-id=\"5417924076503062111\">💰</tg-emoji> <b>1 star narxi: 245 so'm</b>\n"
                f"<tg-emoji emoji-id=\"5951810621887484519\">⭐️</tg-emoji> <b>{stars_count} stars = {price:,} so'm</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Qaysi profilga olasiz?</b>\n"
                f"Username yozing...\n"
                f"<tg-emoji emoji-id=\"5350427505805238170\">✍️</tg-emoji> <b>Format: @username</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Stars shu akkauntga yuboriladiadi</b>"
            )
        else:
            text = (
                f"<tg-emoji emoji-id=\"5417924076503062111\">💰</tg-emoji> <b>Цена 1 star: 245 сум</b>\n"
                f"<tg-emoji emoji-id=\"5951810621887484519\">⭐️</tg-emoji> <b>{stars_count} stars = {price:,} сум</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>На какой профиль?</b>\n"
                f"Напишите username...\n"
                f"<tg-emoji emoji-id=\"5350427505805238170\">✍️</tg-emoji> <b>Формат: @username</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Stars на этот аккаунт</b>"
            )

        # Удаляем старое сообщение и отправляем новое
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price,
            stars_count=stars_count
        )
        await callback.answer()
        return

    # Для остальных категорий - стандартный формат
    if lang == "uz":
        text = (
            f"✅ <b>{name}</b>\n"
            f"📝 <b>Tavsif:</b>\n"
            f"{description}\n\n"
            f"💰 <b>Narxi:</b> {price:,} UZS\n\n"
        )
    else:
        text = (
            f"✅ <b>{name}</b>\n"
            f"📝 <b>Описание:</b>\n"
            f"{description}\n\n"
            f"💰 <b>Цена:</b> {price:,} UZS\n\n"
        )

    # Для Premium - простой формат как у Stars
    if category == "premium":
        if lang == "uz":
            text = (
                f"<tg-emoji emoji-id=\"5368766152870742501\">💎</tg-emoji> <b>{name}</b> — {price:,} so'm\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Premium qaysi profilingizga olinadi?</b>\n\n"
                f"<tg-emoji emoji-id=\"5350427505805238170\">✍️</tg-emoji> <b>Usernameni @ bilan yozing</b>\n"
                f"<b>Masalan: @Admin</b>"
            )
        else:
            text = (
                f"<tg-emoji emoji-id=\"5368766152870742501\">💎</tg-emoji> <b>{name}</b> — {price:,} сум\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>На какой профиль?</b>\n\n"
                f"<tg-emoji emoji-id=\"5350427505805238170\">✍️</tg-emoji> <b>Напишите username с @</b>\n"
                f"<b>Например: @Admin</b>"
            )

        await safe_edit_message(callback, text)
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price
        )
        await callback.answer()
        return

    # Для Gifts - запрашиваем username
    elif category == "gifts":
        # Извлекаем количество stars
        import re
        stars_match = re.search(r'(\d+)\s*⭐', name)
        stars_count = stars_match.group(1) if stars_match else "?"

        # Определяем премиум эмодзи подарка по названию
        gift_emoji_map = {
            "💝": "5283228279988309088",
            "🧸": "5397915559037785261",
            "🎁": "5199749070830197566",
            "🌹": "5280947338821524402",
            "🎂": "5280659198055572187",
            "🚀": "5445284980978621387",
            "🍾": "5451905784734574339",
            "💐": "5280774333243873175",
            "💎": "5368343974765411150",
            "🏆": "5280769763398671636",
            "💍": "5402100905883488232",
        }
        # Ищем эмодзи в названии товара
        gift_emoji_char = "🎁"
        gift_emoji_id = "5199749070830197566"
        for emoji_char, emoji_id in gift_emoji_map.items():
            if emoji_char in name:
                gift_emoji_char = emoji_char
                gift_emoji_id = emoji_id
                break

        if lang == "uz":
            text = (
                f"<tg-emoji emoji-id=\"{gift_emoji_id}\">{gift_emoji_char}</tg-emoji> <b>{stars_count} <tg-emoji emoji-id=\"5469641199348363998\">⭐️</tg-emoji> – Hadya</b>\n"
                f"<tg-emoji emoji-id=\"5417924076503062111\">💰</tg-emoji> <b>{price:,} UZS</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Username: @username</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Sovgʻa shu akkauntga yuboriladi</b>"
            )
        else:
            text = (
                f"<tg-emoji emoji-id=\"{gift_emoji_id}\">{gift_emoji_char}</tg-emoji> <b>{stars_count} <tg-emoji emoji-id=\"5469641199348363998\">⭐️</tg-emoji> – Подарок</b>\n"
                f"<tg-emoji emoji-id=\"5417924076503062111\">💰</tg-emoji> <b>{price:,} UZS</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Username: @username</b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Подарок на этот аккаунт</b>"
            )

        await safe_edit_message(callback, text)
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price
        )

    # Для Robux - запрашиваем логин
    elif category == "robux":
        # Извлекаем количество robux из названия
        import re
        rbx_match = re.search(r'(\d[\d\s]*)\s*rbx', name, re.IGNORECASE)
        rbx_count = rbx_match.group(1).replace(" ", "") if rbx_match else "?"

        if lang == "uz":
            text = (
                f"<tg-emoji emoji-id=\"5199628545457923796\">✅</tg-emoji> <b>{name}</b>\n"
                f"<tg-emoji emoji-id=\"5334882760735598374\">📝</tg-emoji> <b>{rbx_count} Robux beriladi</b>\n"
                f"<tg-emoji emoji-id=\"5460991276948143687\">⚡️</tg-emoji> <b>Tez yetkaziladi</b>\n"
                f"<tg-emoji emoji-id=\"5350619413533958825\">🔐</tg-emoji> <b>Akkauntga kirib beriladi</b>\n\n"
                f"<tg-emoji emoji-id=\"5375296873982604963\">💰</tg-emoji> <b>Narx: {price:,} UZS</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Login yuboring (username yoki email)</b>\n\n"
                f"<tg-emoji emoji-id=\"5188463524568926712\">⚠️</tg-emoji> <b>Parol keyin so'raladi</b>"
            )
        else:
            text = (
                f"<tg-emoji emoji-id=\"5199628545457923796\">✅</tg-emoji> <b>{name}</b>\n"
                f"<tg-emoji emoji-id=\"5334882760735598374\">📝</tg-emoji> <b>Выдаётся {rbx_count} Robux</b>\n"
                f"<tg-emoji emoji-id=\"5460991276948143687\">⚡️</tg-emoji> <b>Быстрая доставка</b>\n"
                f"<tg-emoji emoji-id=\"5350619413533958825\">🔐</tg-emoji> <b>Выдаётся через вход в аккаунт</b>\n\n"
                f"<tg-emoji emoji-id=\"5375296873982604963\">💰</tg-emoji> <b>Цена: {price:,} UZS</b>\n\n"
                f"<tg-emoji emoji-id=\"5373012449597335010\">👤</tg-emoji> <b>Отправьте логин (username или email)</b>\n\n"
                f"<tg-emoji emoji-id=\"5188463524568926712\">⚠️</tg-emoji> <b>Пароль запросим позже</b>"
            )

        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_roblox_login)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price
        )

    # Для Boost - запрашиваем ссылку на канал
    elif category == "boost":
        if lang == "uz":
            text = (
                f"<tg-emoji emoji-id=\"5262880537416054812\">✅</tg-emoji> <b>Telegram Boost</b>\n"
                f"<tg-emoji emoji-id=\"5417924076503062111\">💰</tg-emoji> <b>Narxi: {price:,} UZS</b>\n\n"
                f"<tg-emoji emoji-id=\"5271974997521350631\">🔗</tg-emoji> <b>Kanal havolasini yuboring:</b>\n"
                f"<b>Format: <i><u>https:</u></i></b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Boost shu kanalga qo'llaniladi</b>"
            )
        else:
            text = (
                f"<tg-emoji emoji-id=\"5262880537416054812\">✅</tg-emoji> <b>Telegram Boost</b>\n"
                f"<tg-emoji emoji-id=\"5417924076503062111\">💰</tg-emoji> <b>Цена: {price:,} UZS</b>\n\n"
                f"<tg-emoji emoji-id=\"5271974997521350631\">🔗</tg-emoji> <b>Отправьте ссылку канала:</b>\n"
                f"<b>Формат: <i><u>https:</u></i></b>\n\n"
                f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Буст на этот канал</b>"
            )

        # Вместо редактирования, отправляем новое сообщение
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_channel_link)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price
        )

    # Для остальных категорий (virtual_numbers) - сразу к оплате
    else:
        text += f"\n👇 <b>To'lov usulini tanlang:</b>" if lang == "uz" else f"\n👇 <b>Выберите способ оплаты:</b>"

        # Вместо редактирования, отправляем новое сообщение
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(text, reply_markup=keyboards.payment_methods(), parse_mode="HTML")
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price
        )

    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    help_text = get_premium_help(lang)
    await safe_edit_message(callback, help_text, reply_markup=keyboards.back_to_menu(lang))
    await callback.answer()

@dp.callback_query(F.data == "my_orders")
async def my_orders_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    orders = database.get_user_orders(callback.from_user.id, limit=10)

    status_emoji = {
        "pending":  ("<tg-emoji emoji-id=\"5451732530048802485\">⏳</tg-emoji>", "Kutilmoqda",   "Ожидает"),
        "approved": ("<tg-emoji emoji-id=\"5208869687286316655\">✅</tg-emoji>", "Tasdiqlandi",  "Подтверждён"),
        "rejected": ("<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji>", "Rad etildi",  "Отклонён"),
    }

    if not orders:
        if lang == "uz":
            text = "<tg-emoji emoji-id=\"5334882760735598374\">📝</tg-emoji> <b>Hali buyurtmalar yo'q.</b>"
        else:
            text = "<tg-emoji emoji-id=\"5334882760735598374\">📝</tg-emoji> <b>Заказов пока нет.</b>"
        await safe_edit_message(callback, text, reply_markup=keyboards.back_to_menu(lang))
        await callback.answer()
        return

    if lang == "uz":
        text = "<tg-emoji emoji-id=\"5897920748101571572\">🌟</tg-emoji> <b>Oxirgi buyurtmalaringiz:</b>\n\n"
    else:
        text = "<tg-emoji emoji-id=\"5897920748101571572\">🌟</tg-emoji> <b>Ваши последние заказы:</b>\n\n"

    for order_id, service, amount, status, created_at in orders:
        emoji, status_uz, status_ru = status_emoji.get(status, ("❓", status, status))
        status_label = status_uz if lang == "uz" else status_ru
        date = created_at[:10] if created_at else "—"
        text += (
            f"{emoji} <code>#{order_id}</code> — <b>{service}</b>\n"
            f"<tg-emoji emoji-id=\"5375296873982604963\">💰</tg-emoji> {amount:,} UZS · {status_label} · {date}\n\n"
        )

    await safe_edit_message(callback, text, reply_markup=keyboards.back_to_menu(lang))
    await callback.answer()

@dp.callback_query(F.data == "referral")
async def referral_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    user_id = callback.from_user.id
    count, total, balance = database.get_referral_stats(user_id)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    if lang == "uz":
        text = (
            f"<tg-emoji emoji-id=\"6037131070640491842\">🎉</tg-emoji> <b>Referal tizimi</b>\n\n"
            f"<tg-emoji emoji-id=\"5372926953978341366\">👥</tg-emoji> Takliflaringiz: <b>{count} ta</b>\n"
            f"<tg-emoji emoji-id=\"5346309121794659890\">⭐️</tg-emoji> Jami daromad: <b>{total:.2f} ⭐️</b>\n"
            f"<tg-emoji emoji-id=\"5375296873982604963\">💰</tg-emoji> Balans: <b>{balance:.2f} ⭐️</b>\n\n"
            f"<tg-emoji emoji-id=\"5271974997521350631\">🔗</tg-emoji> <b>Havolangiz:</b>\n"
            f"<code>{ref_link}</code>\n\n"
            f"<tg-emoji emoji-id=\"5431449001532594346\">⚡️</tg-emoji> Har bir taklif uchun <b>+0.50 ⭐️</b>\n"
            f"(shart: foydalanuvchi kanalga obuna bo'lishi kerak)"
        )
    else:
        text = (
            f"<tg-emoji emoji-id=\"6037131070640491842\">🎉</tg-emoji> <b>Реферальная система</b>\n\n"
            f"<tg-emoji emoji-id=\"5372926953978341366\">👥</tg-emoji> Приглашено: <b>{count} чел.</b>\n"
            f"<tg-emoji emoji-id=\"5346309121794659890\">⭐️</tg-emoji> Всего заработано: <b>{total:.2f} ⭐️</b>\n"
            f"<tg-emoji emoji-id=\"5375296873982604963\">💰</tg-emoji> Баланс: <b>{balance:.2f} ⭐️</b>\n\n"
            f"<tg-emoji emoji-id=\"5271974997521350631\">🔗</tg-emoji> <b>Ваша ссылка:</b>\n"
            f"<code>{ref_link}</code>\n\n"
            f"<tg-emoji emoji-id=\"5431449001532594346\">⚡️</tg-emoji> За каждого приглашённого <b>+0.50 ⭐️</b>\n"
            f"(условие: пользователь должен подписаться на канал)"
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Havolani ulashish" if lang == "uz" else "🔗 Поделиться ссылкой",
                              url=f"https://t.me/share/url?url={ref_link}&text={'Do%27stlaringizni%20taklif%20qiling!' if lang == 'uz' else 'Присоединяйтесь!'}")],
        [InlineKeyboardButton(text="◀️ Orqaga" if lang == "uz" else "◀️ Назад", callback_data="back_to_menu")]
    ])
    await safe_edit_message(callback, text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def contact_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    
    admin_username = "StarPayUzAdmin"
    
    # Создаем inline кнопку для перехода в личку админа
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Adminga yozish" if lang == "uz" else "💬 Написать админу",
            url=f"https://t.me/{admin_username}"
        )],
        [InlineKeyboardButton(
            text=get_text_simple(lang, "back_menu"),
            callback_data="back_to_menu"
        )]
    ])
    
    if lang == "uz":
        text = (
            "📞 <b>Aloqa</b>\n\n"
            "Quyidagi tugmani bosing va adminga yozing:\n\n"
            f"👤 Admin: @{admin_username}\n"
            f"💬 Xabar: <code>Salom @StarPayUz_bot boyicha yozyapman</code>\n\n"
            "Xabarni nusxalash uchun ustiga bosing ☝️"
        )
    else:
        text = (
            "📞 <b>Связаться</b>\n\n"
            "Нажмите кнопку ниже и напишите админу:\n\n"
            f"👤 Админ: @{admin_username}\n"
            f"💬 Сообщение: <code>Salom @StarPayUz_bot boyicha yozyapman</code>\n\n"
            "Нажмите на сообщение чтобы скопировать ☝️"
        )
    
    await safe_edit_message(callback, text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "statistics")
async def statistics_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    user_count = database.get_user_count()
    stats_text = get_text(lang, "statistics", use_premium=True, count=user_count)
    await safe_edit_message(callback, stats_text, reply_markup=keyboards.back_to_menu(lang))
    await callback.answer()

@dp.message(Command("shop"))
async def cmd_shop(message: types.Message):
    """Команда для открытия магазина с premium emoji"""
    await message.answer(
        "🛍️ <b>Выберите что вы хотите купить:</b>",
        reply_markup=create_premium_keyboard(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📊 Статистика")
async def admin_stats(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    user_count = database.get_user_count()
    pending_orders = len(database.get_pending_orders())
    ref_count = database.get_referral_count()
    
    stats_text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"<tg-emoji emoji-id=\"5472308992514464048\">👥</tg-emoji> Всего пользователей: <b>{user_count}</b>\n"
        f"📝 Ожидающих заказов: <b>{pending_orders}</b>\n"
        f"<tg-emoji emoji-id=\"5368324170671202286\">⭐</tg-emoji> Всего рефералов: <b>{ref_count}</b>\n"
    )
    
    await message.answer(stats_text, parse_mode="HTML")

@dp.message(F.text == "📝 Заказы")
async def admin_orders(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    # Показываем все заказы (не только pending)
    orders = database.get_all_orders(limit=30)

    if not orders:
        await message.answer("📝 Заказов нет")
        return

    status_map = {
        "pending":  "⏳ Kutilmoqda",
        "approved": "✅ Tasdiqlandi",
        "rejected": "❌ Rad etildi",
    }

    for order in orders:
        order_id, user_id, username, first_name, service, amount, status, created_at = order
        user_tag = f"@{username}" if username else first_name
        status_label = status_map.get(status, status)

        order_text = (
            f"📝 <b>Заказ #{order_id}</b>\n\n"
            f"👤 Пользователь: {user_tag}\n"
            f"🛍️ Услуга: {service}\n"
            f"💰 Сумма: {amount:,} UZS\n"
            f"📊 Статус: {status_label}\n"
            f"📅 Дата: {created_at}"
        )

        # Для pending показываем approve/reject, для остальных только удаление
        if status == "pending":
            kb = keyboards.order_actions(order_id)
        else:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del_order_{order_id}")]
            ])

        await message.answer(order_text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("del_order_"))
async def del_single_order(callback: types.CallbackQuery):
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    order_id = int(callback.data.replace("del_order_", ""))
    database.delete_order(order_id)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer(f"🗑 Заказ #{order_id} удалён")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_order(callback: types.CallbackQuery):
    """Подтверждение заказа"""
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    
    order_id = int(callback.data.replace("approve_", ""))
    
    # Получаем информацию о заказе
    order_info = database.get_order_info(order_id)
    if order_info:
        user_id = order_info[0]
        database.update_order_status(order_id, "approved")
        
        # Уведомляем пользователя
        try:
            lang = database.get_user_language(user_id)
            if lang == "uz":
                notify_text = (
                    f"<tg-emoji emoji-id=\"5208869687286316655\">✅</tg-emoji> <b>Buyurtma #{order_id} tasdiqlandi!</b>\n\n"
                    f"<tg-emoji emoji-id=\"5460991276948143687\">⚡️</tg-emoji> Xizmat tez orada bajariladi.\n"
                    f"<tg-emoji emoji-id=\"5201990176175299013\">📞</tg-emoji> Savollar: @StarPayUzAdmin"
                )
            else:
                notify_text = (
                    f"<tg-emoji emoji-id=\"5208869687286316655\">✅</tg-emoji> <b>Заказ #{order_id} подтверждён!</b>\n\n"
                    f"<tg-emoji emoji-id=\"5460991276948143687\">⚡️</tg-emoji> Услуга будет выполнена в ближайшее время.\n"
                    f"<tg-emoji emoji-id=\"5201990176175299013\">📞</tg-emoji> Вопросы: @StarPayUzAdmin"
                )
            await bot.send_message(user_id, notify_text, parse_mode="HTML")
        except:
            pass
    
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ <b>ПОДТВЕРЖДЕН</b>",
            parse_mode="HTML"
        )
    except:
        # Используем safe_edit_message для работы с любым типом сообщения
        new_text = callback.message.caption if callback.message.caption else callback.message.text
        await safe_edit_message(callback, new_text + "\n\n✅ <b>ПОДТВЕРЖДЕН</b>")
    
    await callback.answer("✅ Заказ подтвержден!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_order(callback: types.CallbackQuery):
    """Отклонение заказа"""
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    
    order_id = int(callback.data.replace("reject_", ""))
    
    # Получаем информацию о заказе
    order_info = database.get_order_info(order_id)
    if order_info:
        user_id = order_info[0]
        database.update_order_status(order_id, "rejected")
        
        # Уведомляем пользователя
        try:
            lang = database.get_user_language(user_id)
            if lang == "uz":
                notify_text = (
                    f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Buyurtma #{order_id} rad etildi.</b>\n\n"
                    f"<tg-emoji emoji-id=\"5201990176175299013\">📞</tg-emoji> Muammo bo'lsa: @StarPayUzAdmin || @kamron235"
                )
            else:
                notify_text = (
                    f"<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Заказ #{order_id} отклонён.</b>\n\n"
                    f"<tg-emoji emoji-id=\"5201990176175299013\">📞</tg-emoji> По вопросам: @StarPayUzAdmin || @kamron235"
                )
            await bot.send_message(user_id, notify_text, parse_mode="HTML")
        except:
            pass
    
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ <b>ОТКЛОНЕН</b>",
            parse_mode="HTML"
        )
    except:
        # Используем safe_edit_message для работы с любым типом сообщения
        new_text = callback.message.caption if callback.message.caption else callback.message.text
        await safe_edit_message(callback, new_text + "\n\n❌ <b>ОТКЛОНЕН</b>")
    
    await callback.answer("❌ Заказ отклонен!")

@dp.message(F.text == "🗑 Удалить заказы")
async def admin_delete_orders(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Все заказы удалить", callback_data="admin_delete_all_orders")],
        [InlineKeyboardButton(text="🗑 Удалить по ID", callback_data="admin_delete_by_id")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_delete")]
    ])
    await message.answer(
        "🗑 <b>Управление заказами</b>\n\nВыберите действие:",
        reply_markup=keyboard, parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_delete_all_orders")
async def admin_confirm_delete_all(callback: types.CallbackQuery):
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить всё", callback_data="admin_confirm_delete_all")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_delete")]
    ])
    await callback.message.edit_text(
        "⚠️ <b>Вы уверены?</b>\n\nВсе заказы будут удалены безвозвратно!",
        reply_markup=keyboard, parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_confirm_delete_all")
async def admin_do_delete_all(callback: types.CallbackQuery):
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    database.delete_all_orders()
    await callback.message.edit_text("✅ <b>Все заказы удалены!</b>", parse_mode="HTML")
    await callback.answer("✅ Готово!")

@dp.callback_query(F.data == "admin_delete_by_id")
async def admin_delete_by_id_prompt(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🗑 Введите ID заказа для удаления:\n\n/cancel для отмены",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_delete_order_id)
    await callback.answer()

@dp.message(OrderStates.waiting_for_delete_order_id)
async def admin_do_delete_by_id(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    try:
        order_id = int(message.text.strip())
        database.delete_order(order_id)
        await message.answer(f"✅ Заказ <b>#{order_id}</b> удалён!", parse_mode="HTML",
                             reply_markup=keyboards.admin_menu())
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)")
        return
    await state.clear()

@dp.callback_query(F.data == "admin_cancel_delete")
async def admin_cancel_delete(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("Отменено")

@dp.message(F.text == "📣 Опубликовать заказ")
async def admin_publish_order(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    orders = database.get_all_orders(limit=20)
    if not orders:
        await message.answer("📝 Нет заказов для публикации")
        return

    buttons = []
    for order in orders:
        order_id, user_id, username, first_name, service, amount, status, created_at = order
        label = f"#{order_id} — {service[:20]} — {amount:,} UZS"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"pub_order_{order_id}")])

    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_delete")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        "📣 <b>Выберите заказ для публикации:</b>",
        reply_markup=keyboard, parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("pub_order_"))
async def admin_do_publish_order(callback: types.CallbackQuery):
    if callback.from_user.id not in config.ADMIN_IDS:
        return
    order_id = int(callback.data.replace("pub_order_", ""))

    conn = __import__('sqlite3').connect(config.DATABASE_FILE)
    cur = conn.cursor()
    cur.execute('''
        SELECT o.order_id, o.user_id, u.username, u.first_name, o.service, o.amount, o.status, o.created_at
        FROM orders o JOIN users u ON o.user_id = u.user_id
        WHERE o.order_id = ?
    ''', (order_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return

    oid, uid, username, first_name, service, amount, status, created_at = row
    user_tag = f"@{username}" if username else first_name

    pub_text = (
        f"<tg-emoji emoji-id=\"5368324170671202286\">🛍</tg-emoji> <b>Yangi buyurtma!</b>\n\n"
        f"<tg-emoji emoji-id=\"5472308992514464048\">👤</tg-emoji> Xaridor: <b>{user_tag}</b>\n"
        f"<tg-emoji emoji-id=\"5897920748101571572\">🌟</tg-emoji> Mahsulot: <b>{service}</b>\n"
        f"<tg-emoji emoji-id=\"5375296873982604963\">💰</tg-emoji> Summa: <b>{amount:,} UZS</b>\n\n"
        f"<tg-emoji emoji-id=\"5208869687286316655\">✅</tg-emoji> <b>Star_payuz</b> orqali sotib olindi!"
    )

    try:
        await bot.send_message(config.CHANNEL_ID, pub_text, parse_mode="HTML")
        await callback.message.edit_text(
            f"✅ <b>Заказ #{order_id} опубликован в канал!</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка публикации: {e}",
            parse_mode="HTML"
        )
    await callback.answer()

@dp.message(F.text == "📢 Рассылка")
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    await message.answer(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Отправьте сообщение, которое хотите разослать всем пользователям.\n\n"
        "Для отмены отправьте /cancel",
        parse_mode="HTML"
    )
    
    await state.set_state(BroadcastStates.waiting_for_message)

@dp.message(BroadcastStates.waiting_for_message)
async def process_broadcast(message: types.Message, state: FSMContext):
    """Обработка рассылки"""
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    users = database.get_all_users()
    success = 0
    failed = 0
    
    status_msg = await message.answer(f"📤 Рассылка начата...\n\n✅ Отправлено: 0\n❌ Ошибок: 0")
    
    for user_id in users:
        try:
            await message.copy_to(user_id)
            success += 1
        except:
            failed += 1
        
        # Обновляем статус каждые 10 пользователей
        if (success + failed) % 10 == 0:
            try:
                await status_msg.edit_text(
                    f"📤 Рассылка в процессе...\n\n"
                    f"✅ Отправлено: {success}\n"
                    f"❌ Ошибок: {failed}"
                )
            except:
                pass
    
    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"✅ Отправлено: {success}\n"
        f"❌ Ошибок: {failed}",
        parse_mode="HTML"
    )
    
    await state.clear()

@dp.message(F.text == "◀️ Выход")
async def exit_admin(message: types.Message, state: FSMContext):
    """Выход из админ панели"""
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    # Сбрасываем авторизацию
    await state.clear()
    
    lang = database.get_user_language(message.from_user.id)
    await message.answer(
        "👋 Вы вышли из админ панели",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    
    # Возвращаем обычное меню
    user_mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    welcome_text = get_premium_welcome(user_mention, lang)
    
    try:
        if hasattr(config, 'BANNER_FILE'):
            import os
            banner_path = config.BANNER_FILE
            if os.path.exists(banner_path):
                photo = types.FSInputFile(banner_path)
                await mФessage.answer_photo(photo=photo, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
            else:
                await message.answer(welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
        else:
            await message.answer(welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
    except Exception as e:
        logging.error(f"Banner error: {e}")
        await message.answer(welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")

@dp.message(Command("qoida"))
async def cmd_rules(message: types.Message):
    """Правила бота"""
    lang = database.get_user_language(message.from_user.id)
    
    if lang == "uz":
        rules_text = (
            "<tg-emoji emoji-id=\"5969686726745002775\">☑️</tg-emoji> <b>Bot qoidalari:</b>\n\n"
            "<tg-emoji emoji-id=\"5440752772574122868\">1️⃣</tg-emoji> <b>Faqat to'g'ri ma'lumotlar kiriting</b>\n"
            "<tg-emoji emoji-id=\"5440582563020181969\">2️⃣</tg-emoji> <b>To'lov chekini aniq yuboring — to'lov faqat chek yuborilgandan keyin tasdiqlanadi</b>\n"
            "<tg-emoji emoji-id=\"5438151976602869299\">3️⃣</tg-emoji> <b>Spam qilmang</b>\n"
            "<tg-emoji emoji-id=\"5440593167294436069\">4️⃣</tg-emoji> <b>Administrator javobini kuting</b>\n"
            "<tg-emoji emoji-id=\"5438369529581311681\">5️⃣</tg-emoji> <b>Qayta to'lov qilmang</b>\n\n"
            "<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Qoidalarni buzgan foydalanuvchilar bloklangan bo'ladi!</b>"
        )
    else:
        rules_text = (
            "<tg-emoji emoji-id=\"5969686726745002775\">☑️</tg-emoji> <b>Правила бота:</b>\n\n"
            "<tg-emoji emoji-id=\"5440752772574122868\">1️⃣</tg-emoji> <b>Вводите только правильные данные</b>\n"
            "<tg-emoji emoji-id=\"5440582563020181969\">2️⃣</tg-emoji> <b>Отправляйте четкий чек оплаты — оплата подтверждается только после отправки чека</b>\n"
            "<tg-emoji emoji-id=\"5438151976602869299\">3️⃣</tg-emoji> <b>Не спамьте</b>\n"
            "<tg-emoji emoji-id=\"5440593167294436069\">4️⃣</tg-emoji> <b>Ждите ответа администратора</b>\n"
            "<tg-emoji emoji-id=\"5438369529581311681\">5️⃣</tg-emoji> <b>Не делайте повторную оплату</b>\n\n"
            "<tg-emoji emoji-id=\"5461137215641895106\">⚠️</tg-emoji> <b>Пользователи, нарушившие правила, будут заблокированы!</b>"
        )
    
    await message.answer(rules_text, parse_mode="HTML", reply_markup=keyboards.back_to_menu(lang))

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    print(f"[DEBUG] /admin command from user {message.from_user.id}, ADMIN_IDS: {config.ADMIN_IDS}")
    
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ панели!")
        print(f"[DEBUG] Access denied for user {message.from_user.id}")
        return
    
    # Проверяем авторизацию
    data = await state.get_data()
    print(f"[DEBUG] State data for user {message.from_user.id}: {data}")
    
    if data.get('admin_authorized'):
        # Уже авторизован
        print(f"[DEBUG] User {message.from_user.id} already authorized")
        await message.answer(
            "🔐 <b>Админ панель Star_payuz</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboards.admin_menu(),
            parse_mode="HTML"
        )
    else:
        # Запрашиваем логин
        print(f"[DEBUG] Requesting login from user {message.from_user.id}")
        await message.answer(
            "🔐 <b>Вход в админ панель</b>\n\n"
            "Введите логин:",
            parse_mode="HTML"
        )
        await state.set_state(AdminAuthStates.waiting_for_login)
        print(f"[DEBUG] State set to waiting_for_login for user {message.from_user.id}")

@dp.message(AdminAuthStates.waiting_for_login)
async def admin_login_received(message: types.Message, state: FSMContext):
    """Получение логина"""
    login = message.text.strip()
    
    print(f"[DEBUG] Admin login attempt: {login} from user {message.from_user.id}")
    
    if login == config.ADMIN_LOGIN:
        await state.update_data(admin_login=login)
        await message.answer(
            "✅ <b>Логин принят</b>\n\n"
            "Введите пароль:",
            parse_mode="HTML"
        )
        # Явно устанавливаем состояние
        await state.set_state(AdminAuthStates.waiting_for_password)
        print(f"[DEBUG] State set to waiting_for_password for user {message.from_user.id}")
    else:
        await message.answer(
            "❌ <b>Неверный логин!</b>\n\n"
            "Попробуйте еще раз или /cancel для отмены",
            parse_mode="HTML"
        )
        print(f"[DEBUG] Wrong login: {login}")

@dp.message(AdminAuthStates.waiting_for_password)
async def admin_password_received(message: types.Message, state: FSMContext):
    """Получение пароля"""
    password = message.text.strip()
    
    print(f"[DEBUG] Admin password attempt from user {message.from_user.id}")
    
    # Удаляем сообщение с паролем для безопасности
    try:
        await message.delete()
    except:
        pass
    
    if password == config.ADMIN_PASSWORD:
        await state.update_data(admin_authorized=True)
        await state.set_state(None)
        
        print(f"[DEBUG] Admin authorized successfully for user {message.from_user.id}")
        
        await bot.send_message(
            message.from_user.id,
            "✅ <b>Успешная авторизация!</b>\n\n"
            "🔐 <b>Админ панель Star_payuz</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboards.admin_menu(),
            parse_mode="HTML"
        )
    else:
        print(f"[DEBUG] Wrong password from user {message.from_user.id}")
        await bot.send_message(
            message.from_user.id,
            "❌ <b>Неверный пароль!</b>\n\n"
            "Попробуйте еще раз: /admin",
            parse_mode="HTML"
        )
        await state.clear()

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    await message.answer("❌ Действие отменено", reply_markup=types.ReplyKeyboardRemove())

# Отладочный обработчик удален для исправления авторизации админа

async def set_bot_commands():
    """Установка команд бота"""
    # Команды для обычных пользователей (без /admin)
    commands_uz = [
        types.BotCommand(command="start", description="Botni ishga tushirish"),
        types.BotCommand(command="qoida", description="Qoidalar"),
    ]
    commands_ru = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="qoida", description="Правила"),
    ]
    # Команды для админов (с /admin)
    admin_commands = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="qoida", description="Правила"),
        types.BotCommand(command="admin", description="Админ панель"),
    ]

    await bot.set_my_commands(commands_uz, language_code="uz")
    await bot.set_my_commands(commands_ru, language_code="ru")
    await bot.set_my_commands(commands_uz)

    # Устанавливаем расширенные команды для каждого админа
    from aiogram.types import BotCommandScopeChat
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception as e:
            logging.error(f"Failed to set admin commands for {admin_id}: {e}")

async def main():
    database.init_db()
    await set_bot_commands()
    print("🚀 Бот Star_payuz zapущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())