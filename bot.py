# -*- coding: utf-8 -*-
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import database
import keyboards
from translations import get_text, get_text_simple
from universal_messages import (
    get_universal_welcome,
    get_universal_service_selected,
    get_universal_payment_info,
    get_universal_order_accepted,
    get_universal_help,
    get_universal_category_name
)

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


def format_as_quote(text, lang="uz"):
    """Форматировать текст как цитату"""
    if lang == "uz":
        return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else:
        return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

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
        logging.error(f"Subscription check error: {e}")
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    database.add_user(user.id, user.username, user.first_name)
    lang = database.get_user_language(user.id)
    
    # Формируем упоминание пользователя
    user_mention = f"@{user.username}" if user.username else user.first_name
    
    # Если язык не выбран (первый запуск), показываем выбор языка
    if lang == "uz" and not database.user_exists(user.id):
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
        if lang == "uz":
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"⚠️ <b>Botdan foydalanish uchun kanalimizga obuna bo'ling!</b>"
            )
        else:
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"⚠️ <b>Для использования бота подпишитесь на наш канал!</b>"
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
    welcome_text = get_universal_welcome(user_mention, lang)
    
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
                f"⚠️ <b>Botdan foydalanish uchun kanalimizga obuna bo'ling!</b>"
            )
        else:
            sub_text = (
                f"👋 <b>{user_mention}!</b>\n\n"
                f"⚠️ <b>Для использования бота подпишитесь на наш канал!</b>"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna / Подписаться", url=config.CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish / Проверить", callback_data="check_subscription")]
        ])
        
        await callback.message.edit_caption(caption=sub_text, reply_markup=keyboard, parse_mode="HTML")
    else:
        # Показываем продающее приветствие
        await callback.answer(get_text_simple(lang, "language_changed"))
        welcome_text = get_premium_welcome(user_mention, lang)
        await callback.message.edit_caption(caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")

@dp.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    user_mention = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
    
    if await check_subscription(callback.from_user.id):
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
    await callback.message.edit_caption(caption=get_text_simple(lang, "choose_language"), reply_markup=keyboards.language_keyboard(), parse_mode="HTML")

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
                "⚠️ <b>Muhim:</b> Akkauntingizga kirishimiz kerak bo'ladi"
            )
        else:
            text = (
                "💎 <b>Telegram Premium</b>\n\n"
                "Какой вариант выбираете?\n\n"
                "📌 <b>1 месяц</b> - По номеру телефона (нужен вход)\n"
                "📌 <b>12 месяцев</b> - По номеру телефона (нужен вход)\n\n"
                "⚠️ <b>Важно:</b> Потребуется вход в ваш аккаунт"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 1 oy / месяц", callback_data="premium_1month")],
            [InlineKeyboardButton(text="📅 12 oy / месяцев", callback_data="premium_12month")],
            [InlineKeyboardButton(text="◀️ Orqaga / Назад", callback_data="back_to_menu")]
        ])
        
        await callback.message.edit_caption(caption=text, reply_markup=keyboard, parse_mode="HTML")
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
                f"⚠️ <b>Muhim:</b> Stars yoki sovg'a shu akkauntga yuboriladi"
            )
        else:
            text = (
                f"✅ Вы выбрали: <b>{service_name}</b>\n\n"
                f"💰 <b>Цена:</b> <b>{price:,} UZS</b>\n\n"
                f"👤 <b>Пожалуйста, отправьте username:</b>\n"
                f"Формат: @username или username\n\n"
                f"⚠️ <b>Важно:</b> Stars или подарок будет отправлен на этот аккаунт"
            )
        
        await callback.message.edit_caption(caption=text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(service=service, service_name=service_name, price=price)
    else:
        # Для остальных услуг - сразу к оплате
        text = get_premium_service_selected(service_name, price, lang)
        await callback.message.edit_caption(caption=text, reply_markup=keyboards.payment_methods(), parse_mode="HTML")
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
            f"⚠️ <b>Muhim:</b> Akkauntingizga kirish uchun kod yuboriladi"
        )
    else:
        text = (
            f"✅ Вы выбрали: <b>{service_name}</b>\n\n"
            f"💰 <b>Цена:</b> <b>{price:,} UZS</b>\n\n"
            f"📱 <b>Пожалуйста, отправьте номер телефона:</b>\n"
            f"Формат: +998901234567\n\n"
            f"⚠️ <b>Важно:</b> На номер придет код для входа в аккаунт"
        )
    
    await callback.message.edit_caption(caption=text, parse_mode="HTML")
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
                f"✅ <b>Username qabul qilindi!</b>\n\n"
                f"👤 <b>Username:</b> @{username}\n\n"
                f"💌 <b>Iltimos, xabar yuboring:</b>\n"
                f"Bu xabar sovg'a bilan birga yuboriladi\n\n"
                f"📝 Xabar uzunligi: 0-200 belgi"
            )
        else:
            text = (
                f"✅ <b>Username принят!</b>\n\n"
                f"👤 <b>Username:</b> @{username}\n\n"
                f"💌 <b>Пожалуйста, отправьте сообщение:</b>\n"
                f"Это сообщение будет отправлено вместе с подарком\n\n"
                f"📝 Длина сообщения: 0-200 символов"
            )
        
        await message.answer(text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_message)
    else:
        # Для Stars и других услуг - сразу к оплате
        data = await state.get_data()
        service_name = data.get('service_name')
        price = data.get('price')
        category = data.get('category', '')
        stars_count = data.get('stars_count', 0)
        
        if category == "stars" and stars_count > 0:
            # Для Stars показываем детальную информацию
            if lang == "uz":
                text = (
                    f"✅ <b>Username qabul qilindi!</b>\n\n"
                    f"👤 <b>Username:</b> @{username}\n"
                    f"⭐️ <b>Stars soni:</b> {stars_count} ta\n"
                    f"� <b>1 star narxi:</b> 320 so'm\n"
                    f"💰 <b>Jami summa:</b> <b>{price:,} so'm</b>\n\n"
                    f"👇 <b>To'lov usulini tanlang:</b>"
                )
            else:
                text = (
                    f"✅ <b>Username принят!</b>\n\n"
                    f"👤 <b>Username:</b> @{username}\n"
                    f"⭐️ <b>Количество stars:</b> {stars_count} шт\n"
                    f"💵 <b>Цена 1 star:</b> 320 сум\n"
                    f"💰 <b>Общая сумма:</b> <b>{price:,} сум</b>\n\n"
                    f"👇 <b>Выберите способ оплаты:</b>"
                )
        else:
            # Для других услуг
            if lang == "uz":
                text = (
                    f"✅ <b>Username qabul qilindi!</b>\n\n"
                    f"👤 <b>Username:</b> @{username}\n"
                    f"�🛍️ <b>Xizmat:</b> {service_name}\n"
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

@dp.message(OrderStates.waiting_for_message)
async def message_received(message: types.Message, state: FSMContext):
    """Получение сообщения для NFT подарка"""
    lang = database.get_user_language(message.from_user.id)
    gift_message = message.text.strip()
    
    # Проверяем длину сообщения
    if len(gift_message) > 200:
        if lang == "uz":
            await message.answer(
                "❌ <b>Xabar juda uzun!</b>\n\n"
                "Iltimos, 200 belgidan oshmasligi kerak",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ <b>Сообщение слишком длинное!</b>\n\n"
                "Пожалуйста, не более 200 символов",
                parse_mode="HTML"
            )
        return
    
    # Сохраняем сообщение
    await state.update_data(gift_message=gift_message)
    
    # Спрашиваем анонимность
    if lang == "uz":
        text = (
            f"✅ <b>Xabar qabul qilindi!</b>\n\n"
            f"💌 <b>Xabar:</b> {gift_message}\n\n"
            f"🤔 <b>Sovg'ani qanday yuborish kerak?</b>\n\n"
            f"🔒 <b>Anonim</b> - Kimdanligi ko'rinmaydi\n"
            f"👤 <b>Anonim emas</b> - Sizning akkauntingizdan"
        )
    else:
        text = (
            f"✅ <b>Сообщение принято!</b>\n\n"
            f"💌 <b>Сообщение:</b> {gift_message}\n\n"
            f"🤔 <b>Как отправить подарок?</b>\n\n"
            f"🔒 <b>Анонимно</b> - Не видно от кого\n"
            f"👤 <b>Не анонимно</b> - От вашего аккаунта"
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
    
    if lang == "uz":
        text = (
            f"✅ <b>Sozlamalar saqlandi!</b>\n\n"
            f"👤 <b>Username:</b> @{username}\n"
            f"💌 <b>Xabar:</b> {gift_message}\n"
            f"🔒 <b>Anonimlik:</b> {'Ha' if is_anonymous else 'Yoq'}\n"
            f"🛍️ <b>Xizmat:</b> {service_name}\n"
            f"💰 <b>Summa:</b> <b>{price:,} UZS</b>\n\n"
            f"👇 <b>To'lov usulini tanlang:</b>"
        )
    else:
        text = (
            f"✅ <b>Настройки сохранены!</b>\n\n"
            f"👤 <b>Username:</b> @{username}\n"
            f"💌 <b>Сообщение:</b> {gift_message}\n"
            f"🔒 <b>Анонимность:</b> {'Да' if is_anonymous else 'Нет'}\n"
            f"🛍️ <b>Услуга:</b> {service_name}\n"
            f"💰 <b>Сумма:</b> <b>{price:,} UZS</b>\n\n"
            f"👇 <b>Выберите способ оплаты:</b>"
        )
    
    await callback.message.edit_caption(caption=text, reply_markup=keyboards.payment_methods(), parse_mode="HTML")
    await state.set_state(None)
    await callback.answer()

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
            f"✅ <b>Login qabul qilindi!</b>\n\n"
            f"👤 <b>Login:</b> <code>{roblox_login}</code>\n\n"
            f"🔐 <b>Endi parolni yuboring:</b>\n"
            f"📌 <b>Misol:</b> MyPassword123 yoki Roblox@2024\n\n"
            f"⚠️ <b>Muhim:</b> Parol faqat administrator ko'radi va xavfsiz saqlanadi"
        )
    else:
        text = (
            f"✅ <b>Логин принят!</b>\n\n"
            f"👤 <b>Логин:</b> <code>{roblox_login}</code>\n\n"
            f"🔐 <b>Теперь отправьте пароль:</b>\n"
            f"📌 <b>Пример:</b> MyPassword123 или Roblox@2024\n\n"
            f"⚠️ <b>Важно:</b> Пароль видит только администратор и хранится безопасно"
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
    
    if lang == "uz":
        text = (
            f"✅ <b>Roblox ma'lumotlari saqlandi!</b>\n\n"
            f"👤 <b>Login:</b> <code>{roblox_login}</code>\n"
            f"🔐 <b>Parol:</b> <i>(xavfsiz saqlandi)</i>\n"
            f"🛍️ <b>Xizmat:</b> {service_name}\n"
            f"💰 <b>Summa:</b> <b>{price:,} UZS</b>\n\n"
            f"👇 <b>To'lov usulini tanlang:</b>"
        )
    else:
        text = (
            f"✅ <b>Данные Roblox сохранены!</b>\n\n"
            f"👤 <b>Логин:</b> <code>{roblox_login}</code>\n"
            f"🔐 <b>Пароль:</b> <i>(сохранен безопасно)</i>\n"
            f"🛍️ <b>Услуга:</b> {service_name}\n"
            f"💰 <b>Сумма:</b> <b>{price:,} UZS</b>\n\n"
            f"👇 <b>Выберите способ оплаты:</b>"
        )
    
    await bot.send_message(
        message.from_user.id,
        text,
        reply_markup=keyboards.payment_methods(),
        parse_mode="HTML"
    )
    await state.set_state(None)

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
    price_per_star = 320
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
            f"💵 <b>1 star narxi:</b> 320 so'm\n"
            f"⭐️ <b>{stars_count} stars</b> = <b>{total_price:,} so'm</b> bo'ladi\n\n"
            f"👤 <b>Qaysi profilga olasiz? Username yozing...</b> ✍️\n\n"
            f"Format: @username yoki username\n\n"
            f"⚠️ <b>Muhim:</b> Stars shu akkauntga yuboriladi"
        )
    else:
        text = (
            f"💵 <b>Цена 1 star:</b> 320 сум\n"
            f"⭐️ <b>{stars_count} stars</b> = <b>{total_price:,} сум</b>\n\n"
            f"👤 <b>На какой профиль покупаете? Напишите username...</b> ✍️\n\n"
            f"Формат: @username или username\n\n"
            f"⚠️ <b>Важно:</b> Stars будет отправлен на этот аккаунт"
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
            f"<tg-emoji emoji-id=\"5348489165589724843\">💎</tg-emoji> <b>TRASTBANK — To'lov va rekvizitlar</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇺🇿 ️ <b>To'lov shartlari:</b>\n\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">💳</tg-emoji> <b>Karta raqami:</b>\n"
            f"<code>{config.CARD_NUMBER}</code>\n\n"
            f"🟢 <b>Karta egasi:</b> {config.CARD_OWNER}\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">📞</tg-emoji> <b>Kartaga ulangan raqam:</b>\n"
            f"<code>{config.CARD_PHONE}</code>\n\n"
            f"<tg-emoji emoji-id=\"5458488840022933066\">🛍️</tg-emoji> <b>Xizmat:</b> {service_name}\n"
        )
        
        # Для Stars добавляем детальную информацию
        if category == "stars" and stars_count > 0:
            payment_info += (
                f"<tg-emoji emoji-id=\"5936259309812846957\">🌟</tg-emoji> <b>Stars soni:</b> {stars_count} ta\n"
                f"<tg-emoji emoji-id=\"5456390099958773299\">💰</tg-emoji> <b>1 star narxi:</b> 320 so'm\n"
                f"<tg-emoji emoji-id=\"5456390099958773299\">💰</tg-emoji> <b>Jami summa:</b> <b>{price:,} so'm</b>\n"
            )
        else:
            payment_info += f"<tg-emoji emoji-id=\"5456390099958773299\">💰</tg-emoji> <b>To'lov summasi:</b> <b>{price:,} UZS</b>\n"
        
        if phone_number:
            payment_info += f"<tg-emoji emoji-id=\"5456390099958773299\">📱</tg-emoji> <b>Sizning raqamingiz:</b> <code>{phone_number}</code>\n"
        
        payment_info += (
            f"\n<tg-emoji emoji-id=\"5456390099958773299\">🧾</tg-emoji> <b>To'lov limiti:</b> 0 so'm\n\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">⚠️</tg-emoji> <b>Muhim!</b>\n"
            f"• To'lov qilayotganda bank komissiyasiga albatta e'tibor bering — summa to'liq tushishi shart.\n"
            f"❗ To'lovdan so'ng 12 soat ichida chek adminga yuborilmasa, mablag' qaytarilmaydi.\n\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">📸</tg-emoji> <b>To'lov chekini shu chatga yuboring!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">📌</tg-emoji> <b>Aloqa:</b> @Star_payuz_admin\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">🤖</tg-emoji> <b>Karta bot:</b> {config.CARD_BOT}"
        )
    else:
        payment_info = (
            f"<tg-emoji emoji-id=\"5348489165589724843\">💎</tg-emoji> <b>TRASTBANK — Оплата и реквизиты</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇺🇿 ️<b>Условия оплаты:</b>\n\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">💳</tg-emoji> <b>Номер карты:</b>\n"
            f"<code>{config.CARD_NUMBER}</code>\n\n"
            f"🟢 <b>Владелец карты:</b> {config.CARD_OWNER}\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">📞</tg-emoji> <b>Номер привязанный к карте:</b>\n"
            f"<code>{config.CARD_PHONE}</code>\n\n"
            f"<tg-emoji emoji-id=\"5458488840022933066\">🛍️</tg-emoji> <b>Услуга:</b> {service_name}\n"
        )
        
        # Для Stars добавляем детальную информацию
        if category == "stars" and stars_count > 0:
            payment_info += (
                f"<tg-emoji emoji-id=\"5936259309812846957\">🌟</tg-emoji> <b>Количество stars:</b> {stars_count} шт\n"
                f"<tg-emoji emoji-id=\"5456390099958773299\">�</tg-emoji> <b>Цена 1 star:</b> 320 сум\n"
                f"<tg-emoji emoji-id=\"5456390099958773299\">💰</tg-emoji> <b>Общая сумма:</b> <b>{price:,} сум</b>\n"
            )
        else:
            payment_info += f"<tg-emoji emoji-id=\"5456390099958773299\">💰</tg-emoji> <b>Сумма к оплате:</b> <b>{price:,} UZS</b>\n"
        
        if phone_number:
            payment_info += f"<tg-emoji emoji-id=\"5456390099958773299\">📱</tg-emoji> <b>Ваш номер:</b> <code>{phone_number}</code>\n"
        
        payment_info += (
            f"\n<tg-emoji emoji-id=\"5456390099958773299\">🧾</tg-emoji> <b>Лимит оплаты:</b> 0 сум\n\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">⚠️</tg-emoji> <b>Важно!</b>\n"
            f"• При оплате обязательно учитывайте комиссию банка — сумма должна поступить полностью.\n"
            f"❗ Если чек не будет отправлен админу в течение 12 часов после оплаты, средства не возвращаются.\n\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">📸</tg-emoji> <b>Отправьте чек оплаты в этот чат!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">📌</tg-emoji> <b>Связь:</b> @Star_payuz_admin\n"
            f"<tg-emoji emoji-id=\"5456390099958773299\">🤖</tg-emoji> <b>Карта бот:</b> {config.CARD_BOT}"
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
                await callback.message.edit_caption(caption=payment_info, parse_mode="HTML")
            except Exception:
                await callback.message.answer(payment_info, parse_mode="HTML")
    except Exception as e:
        # если произошла любая ошибка с отправкой фото – логируем и шлём текст отдельным сообщением
        logging.error(f"Card image error: {e}")
        await bot.send_message(callback.from_user.id, payment_info, parse_mode="HTML")
    
    await state.set_state(OrderStates.waiting_for_payment_proof)
    await state.update_data(payment_method=payment_method)
    await callback.answer()

@dp.message(F.photo, OrderStates.waiting_for_payment_proof)
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
    
    # Получаем название товара для заказа
    product_name = database.get_product_name(product_id, lang)
    
    order_id = database.create_order(message.from_user.id, f"product_{product_id}", price, payment_method)
    await message.answer(get_premium_order_accepted(order_id, lang), reply_markup=keyboards.back_to_menu(lang))
    
    # Уведомление админам
    for admin_id in config.ADMIN_IDS:
        try:
            admin_caption = (
                f"🔔 <b>Yangi buyurtma #{order_id}</b>\n\n"
                f"👤 @{message.from_user.username or 'username yoq'} (ID: {message.from_user.id})\n"
                f"🛍️ {service_name}\n"
            )
            
            # Для Stars добавляем информацию о количестве
            if category == "stars" and stars_count > 0:
                admin_caption += f"⭐️ <b>Stars soni:</b> {stars_count} ta\n"
                admin_caption += f"💵 <b>1 star narxi:</b> 320 so'm\n"
                admin_caption += f"💰 <b>Jami summa:</b> {price:,} so'm\n"
            else:
                admin_caption += f"💰 {price:,} UZS\n"
            
            admin_caption += f"💳 {config.PAYMENT_METHODS[payment_method]}\n"
            
            # Если есть номер телефона (для Premium)
            if phone_number:
                admin_caption += f"📱 <b>Telefon:</b> <code>{phone_number}</code>\n"
            
            # Если есть username (для Stars или NFT)
            if username:
                admin_caption += f"👤 <b>Username:</b> @{username}\n"
            
            # Если есть сообщение (для NFT подарков)
            if gift_message:
                admin_caption += f"💌 <b>Xabar:</b> {gift_message}\n"
            
            # Если есть выбор анонимности (для Gifts подарков)
            if category == "gifts":
                admin_caption += f"🔒 <b>Anonim:</b> {'Ha' if is_anonymous else 'Yoq'}\n"
            
            admin_caption += f"📅 {message.date.strftime('%Y-%m-%d %H:%M:%S')}"
            
            await bot.send_photo(
                admin_id,
                photo=message.photo[-1].file_id,
                caption=admin_caption,
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
        await callback.message.edit_caption(caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
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
            text = "<b>❌ Bu kategoriyada hozircha mahsulotlar mavjud emas</b>"
        else:
            text = "<b>❌ В этой категории пока нет товаров</b>"
        
        await callback.message.edit_caption(caption=text, reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")
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
    if lang == "uz":
        text = "<b>💎 Telegram premium tariflari</b>\n\n"
        text += "<b>1 oylik va 1 yillik profilga kirib olinadi</b>\n"
        text += "<b>3 va 6 12 oylik gift qilib jonatiladi profilga kirilmaydi</b>\n\n"
        text += "<b>Kerali tarifni tanlang 👉</b>"
    else:
        text = "<b>💎 Тарифы Telegram premium</b>\n\n"
        text += "<b>1 месяц и 1 год - вход в профиль</b>\n"
        text += "<b>3, 6 и 12 месяцев - отправляется как подарок, без входа в профиль</b>\n\n"
        text += "<b>Выберите нужный тариф 👉</b>"
    
    # Создаем клавиатуру с товарами
    keyboard_buttons = []
    row = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        name = name_uz if lang == "uz" else name_ru
        
        # Сокращаем название для кнопки и добавляем цену
        if "1 oylik" in name_uz or "1 месяц" in name_ru:
            display_name = "1 oy" if lang == "uz" else "1 месяц"
            button_text = f"⭐️ {display_name} - {price:,} UZS"
        elif "1 yillik" in name_uz or "1 год" in name_ru:
            display_name = "1 yil" if lang == "uz" else "1 год"
            button_text = f"⭐️ {display_name} - {price:,} UZS"
        elif "3 oylik" in name_uz or "3 месяца" in name_ru:
            display_name = "3 oy" if lang == "uz" else "3 месяца"
            button_text = f"🎁 {display_name} - {price:,} UZS"
        elif "6 oylik" in name_uz or "6 месяцев" in name_ru:
            display_name = "6 oy" if lang == "uz" else "6 месяцев"
            button_text = f"🎁 {display_name} - {price:,} UZS"
        elif "12 oylik" in name_uz or "12 месяцев" in name_ru:
            display_name = "12 oy" if lang == "uz" else "12 месяцев"
            button_text = f"🎁 {display_name} - {price:,} UZS"
        else:
            # Убираем скобки с типом для кнопки
            clean_name = name.replace("(Akkaunt orqali)", "").replace("(Через аккаунт)", "").replace("(Akkauntsiz)", "").replace("(Без аккаунта)", "").strip()
            button_text = f"{clean_name} - {price:,} UZS"
        
        row.append(InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}"))
        
        # Добавляем по 2 кнопки в ряд
        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []
    
    # Добавляем последний ряд если он не пустой
    if row:
        keyboard_buttons.append(row)
    
    # Добавляем кнопку назад
    keyboard_buttons.append([InlineKeyboardButton(text=get_text_simple(lang, "back_menu"), callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    # Пробуем отправить видео premium.mp4 если файл существует
    try:
        import os
        if hasattr(config, 'PREMIUM_VIDEO') and os.path.exists(config.PREMIUM_VIDEO):
            # Удаляем старое сообщение
            await callback.message.delete()
            
            # Отправляем видео с подписью
            video = types.FSInputFile(config.PREMIUM_VIDEO)
            await bot.send_video(
                callback.from_user.id,
                video=video,
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Если видео нет, отправляем новое сообщение
            try:
                await callback.message.delete()
            except:
                pass
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Premium video error: {e}")
        # Если ошибка, отправляем новое сообщение
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
    await callback.answer()

async def show_stars_menu(callback: types.CallbackQuery, products, lang):
    """Показать специальное меню для Stars"""
    if lang == "uz":
        text = (
            "🌟 <b>Telegram Stars</b>\n\n"
            "<code>1 star = 320 so'm</code>\n"
            "<code>Minimal: 50 stars</code>\n"
            "<code>Maksimal: 1 000 000 stars</code>\n\n"
            "👇 <b>Tanlang:</b>"
        )
    else:
        text = (
            "🌟 <b>Telegram Stars</b>\n\n"
            "<code>1 star = 320 сум</code>\n"
            "<code>Минимально: 50 stars</code>\n"
            "<code>Максимально: 1 000 000 stars</code>\n\n"
            "👇 <b>Выберите:</b>"
        )
    
    # Создаем клавиатуру с товарами
    keyboard_buttons = []
    row = []
    
    for product in products:
        product_id, name_uz, name_ru, desc_uz, desc_ru, price = product
        name = name_uz if lang == "uz" else name_ru
        
        # Сокращаем название для кнопки и добавляем цену
        if "100 Stars" in name_uz or "100 Stars" in name_ru:
            display_name = "100 Stars"
            button_text = f"🌟 {display_name} - {price:,} UZS"
        elif "500 Stars" in name_uz or "500 Stars" in name_ru:
            display_name = "500 Stars"
            button_text = f"🌟 {display_name} - {price:,} UZS"
        elif "1000 Stars" in name_uz or "1000 Stars" in name_ru:
            display_name = "1000 Stars"
            button_text = f"🌟 {display_name} - {price:,} UZS"
        else:
            # Убираем скобки с типом для кнопки
            clean_name = name.replace("(sotib olish)", "").replace("(покупка)", "").replace("(sotish)", "").replace("(продажа)", "").strip()
            button_text = f"{clean_name} - {price:,} UZS"
        
        row.append(InlineKeyboardButton(text=button_text, callback_data=f"product_{product_id}"))
        
        # Добавляем по 2 кнопки в ряд
        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []
    
    # Добавляем последний ряд если он не пустой
    if row:
        keyboard_buttons.append(row)
    
    # Добавляем специальную кнопку для покупки произвольного количества
    if lang == "uz":
        custom_button_text = "⭐️ Boshqa miqdor (50-1 000 000)"
    else:
        custom_button_text = "⭐️ Другое количество (50-1 000 000)"
    
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
    
    await callback.answer()

@dp.callback_query(F.data == "custom_stars")
async def custom_stars_selected(callback: types.CallbackQuery, state: FSMContext):
    """Выбор покупки произвольного количества stars"""
    lang = database.get_user_language(callback.from_user.id)
    
    if lang == "uz":
        text = (
            "⭐️ <b>Boshqa miqdor stars sotib olish</b>\n\n"
            "💵 <b>1 star narxi:</b> <code>320 so'm</code>\n"
            "📊 <b>Minimal:</b> <code>50 stars</code>\n"
            "📊 <b>Maksimal:</b> <code>1 000 000 stars</code>\n\n"
            "📝 <b>Nechta stars sotib olmoqchisiz?</b>\n"
            "Iltimos, sonni yuboring:"
        )
    else:
        text = (
            "⭐️ <b>Покупка другого количества stars</b>\n\n"
            "💵 <b>Цена 1 star:</b> <code>320 сум</code>\n"
            "📊 <b>Минимально:</b> <code>50 stars</code>\n"
            "📊 <b>Максимально:</b> <code>1 000 000 stars</code>\n\n"
            "📝 <b>Сколько stars хотите купить?</b>\n"
            "Пожалуйста, отправьте число:"
        )
    
    # Вместо редактирования, отправляем новое сообщение
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
        
        await callback.message.edit_caption(caption=text, reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")
        await callback.answer()
        return
    
    product_id, category, name_uz, name_ru, desc_uz, desc_ru, price, is_active = product
    
    # Проверяем активен ли товар
    if not is_active:
        if lang == "uz":
            text = "❌ <b>Bu mahsulot hozircha mavjud emas</b>"
        else:
            text = "❌ <b>Этот товар временно недоступен</b>"
        
        await callback.message.edit_caption(caption=text, reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")
        await callback.answer()
        return
    
    # Выбираем название и описание на нужном языке
    name = name_uz if lang == "uz" else name_ru
    description = desc_uz if lang == "uz" else desc_ru
    
    # Формируем текст в формате цитаты
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
    
    # Для Premium - проверяем тип (с аккаунтом или без)
    if category == "premium":
        # Проверяем нужен ли вход в аккаунт
        needs_account = "Akkaunt" in name_uz or "аккаунт" in name_ru
        
        if needs_account:
            # Для вариантов с аккаунтом - запрашиваем номер телефона
            if lang == "uz":
                text += (
                    f"\n📱 <b>Iltimos, telefon raqamingizni yuboring:</b>\n"
                    f"Format: +998901234567\n\n"
                    f"⚠️ <b>Muhim:</b> Akkauntingizga kirish uchun kod yuboriladi"
                )
            else:
                text += (
                    f"\n📱 <b>Пожалуйста, отправьте номер телефона:</b>\n"
                    f"Формат: +998901234567\n\n"
                    f"⚠️ <b>Важно:</b> На номер придет код для входа в аккаунт"
                )
            
            await callback.message.edit_caption(caption=text, parse_mode="HTML")
            await state.set_state(OrderStates.waiting_for_phone_number)
            await state.update_data(
                product_id=product_id,
                category=category,
                service_name=name,
                price=price,
                needs_account=True
            )
        else:
            # Для вариантов без входа в аккаунт (3, 6, 12 месяцев) - запрашиваем username
            if lang == "uz":
                text += (
                    f"\n👤 <b>Iltimos, username yuboring:</b>\n"
                    f"Format: @username yoki username\n\n"
                    f"⚠️ <b>Muhim:</b> Premium shu akkauntga yuboriladi"
                )
            else:
                text += (
                    f"\n👤 <b>Пожалуйста, отправьте username:</b>\n"
                    f"Формат: @username или username\n\n"
                    f"⚠️ <b>Важно:</b> Premium будет отправлен на этот аккаунт"
                )
            
            await callback.message.edit_caption(caption=text, parse_mode="HTML")
            await state.set_state(OrderStates.waiting_for_username)
            await state.update_data(
                product_id=product_id,
                category=category,
                service_name=name,
                price=price,
                needs_account=False
            )
    
    # Для Stars - не спрашиваем количество повторно, а используем фиксированный пакет
    elif category == "stars":
        # Пытаемся определить количество stars по цене из словаря цен
        from config import STARS_PRICES

        stars_count = 0
        for qty, star_price in STARS_PRICES.items():
            if star_price == price:
                stars_count = qty
                break

        # Если не нашли по цене, пробуем вытащить число из названия товара (например, "100 Stars ...")
        if stars_count == 0:
            import re
            match = re.search(r"(\d+)", name)
            if match:
                stars_count = int(match.group(1))

        # Формируем текст сразу с итоговой суммой и запросом username
        if lang == "uz":
            text += (
                f"⭐️ <b>Stars soni:</b> {stars_count} ta\n"
                f"💵 <b>1 star narxi:</b> 320 so'm\n"
                f"💰 <b>Jami summa:</b> <b>{price:,} so'm</b>\n\n"
                f"👤 <b>Iltimos, username yuboring:</b>\n"
                f"Format: @username yoki username\n\n"
                f"⚠️ <b>Muhim:</b> Stars shu akkauntga yuboriladi"
            )
        else:
            text += (
                f"⭐️ <b>Количество stars:</b> {stars_count} шт\n"
                f"💵 <b>Цена 1 star:</b> 320 сум\n"
                f"💰 <b>Общая сумма:</b> <b>{price:,} сум</b>\n\n"
                f"👤 <b>Пожалуйста, отправьте username:</b>\n"
                f"Формат: @username или username\n\n"
                f"⚠️ <b>Важно:</b> Stars будет отправлен на этот аккаунт"
            )

        await callback.message.edit_caption(caption=text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price,
            stars_count=stars_count
        )
    
    # Для Gifts - запрашиваем username
    elif category == "gifts":
        if lang == "uz":
            text += (
                f"\n👤 <b>Iltimos, username yuboring:</b>\n"
                f"Format: @username yoki username\n\n"
                f"⚠️ <b>Muhim:</b> Sovg'a shu akkauntga yuboriladi"
            )
        else:
            text += (
                f"\n👤 <b>Пожалуйста, отправьте username:</b>\n"
                f"Формат: @username или username\n\n"
                f"⚠️ <b>Важно:</b> Подарок будет отправлен на этот аккаунт"
            )
        
        await callback.message.edit_caption(caption=text, parse_mode="HTML")
        await state.set_state(OrderStates.waiting_for_username)
        await state.update_data(
            product_id=product_id,
            category=category,
            service_name=name,
            price=price
        )
    
    # Для Robux - запрашиваем логин
    elif category == "robux":
        # Создаем новый текст в формате цитаты как просит пользователь
        if lang == "uz":
            text = (
                f"✅ <b>{name}</b>\n"
                f"📝 <b>Tavsif:</b>\n"
                f"Roblox Robux 120 dona\n"
                f"✅ Akkauntingizga kirib olib beriladi\n"
                f"✅ Tezkor yetkazib berish\n"
                f"✅ Ishonchli xizmat\n\n"
                f"💰 <b>Narxi:</b> {price:,} UZS\n\n"
                f"🔐 <b>Roblox akkauntingizga kirish uchun ma'lumotlar kerak:</b>\n"
                f"👤 <b>Iltimos, login yuboring:</b>\n"
                f"Format: username yoki email\n"
                f"📌 <b>Misol:</b> player123 yoki player@email.com\n\n"
                f"⚠️ <b>Muhim:</b> Faqat login yuboring, parol keyin so'raymiz"
            )
        else:
            text = (
                f"✅ <b>{name}</b>\n"
                f"📝 <b>Описание:</b>\n"
                f"Roblox Robux 120 штук\n"
                f"✅ Вход в ваш аккаунт\n"
                f"✅ Быстрая доставка\n"
                f"✅ Надежный сервис\n\n"
                f"💰 <b>Цена:</b> {price:,} UZS\n\n"
                f"🔐 <b>Для входа в ваш аккаунт Roblox нужны данные:</b>\n"
                f"👤 <b>Пожалуйста, отправьте логин:</b>\n"
                f"Формат: username или email\n"
                f"📌 <b>Пример:</b> player123 или player@email.com\n\n"
                f"⚠️ <b>Важно:</b> Отправьте только логин, пароль запросим позже"
            )
        
        await callback.message.edit_caption(caption=text, parse_mode="HTML")
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
            text += (
                f"\n🔗 <b>Iltimos, kanal yoki post havolasini yuboring:</b>\n"
                f"Format: https://t.me/kanal_nomi yoki @kanal_nomi\n\n"
                f"📌 <b>Misol:</b> https://t.me/Star_payuz yoki @Star_payuz\n\n"
                f"⚠️ <b>Muhim:</b> Boost shu kanalga qo'llaniladi"
            )
        else:
            text += (
                f"\n🔗 <b>Пожалуйста, отправьте ссылку на канал или пост:</b>\n"
                f"Формат: https://t.me/название_канала или @название_канала\n\n"
                f"📌 <b>Пример:</b> https://t.me/Star_payuz или @Star_payuz\n\n"
                f"⚠️ <b>Важно:</b> Boost будет применен к этому каналу"
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
    await callback.message.edit_caption(caption=help_text, reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def contact_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    contact_text = get_premium_help(lang)  # Используем ту же функцию помощи
    await callback.message.edit_caption(caption=contact_text, reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "statistics")
async def statistics_callback(callback: types.CallbackQuery):
    lang = database.get_user_language(callback.from_user.id)
    user_count = database.get_user_count()
    stats_text = get_text(lang, "statistics", use_premium=True, count=user_count)
    await callback.message.edit_caption(caption=stats_text, reply_markup=keyboards.back_to_menu(lang), parse_mode="HTML")
    await callback.answer()

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    lang = database.get_user_language(message.from_user.id)
    help_text = get_premium_help(lang)
    await message.answer(help_text, parse_mode="HTML", reply_markup=keyboards.back_to_menu(lang))

@dp.message(F.text == "📊 Статистика")
async def admin_stats(message: types.Message, state: FSMContext):
    """Статистика бота"""
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    # Проверяем авторизацию
    data = await state.get_data()
    if not data.get('admin_authorized'):
        await message.answer("❌ Сначала авторизуйтесь: /admin")
        return
    
    user_count = database.get_user_count()
    pending_orders = len(database.get_pending_orders())
    
    stats_text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{user_count}</b>\n"
        f"📝 Ожидающих заказов: <b>{pending_orders}</b>\n"
    )
    
    await message.answer(stats_text, parse_mode="HTML")

@dp.message(F.text == "📝 Заказы")
async def admin_orders(message: types.Message, state: FSMContext):
    """Список заказов"""
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    # Проверяем авторизацию
    data = await state.get_data()
    if not data.get('admin_authorized'):
        await message.answer("❌ Сначала авторизуйтесь: /admin")
        return
    
    orders = database.get_pending_orders()
    
    if not orders:
        await message.answer("📝 Нет ожидающих заказов")
        return
    
    for order in orders:
        order_id, user_id, username, service, amount, payment_method, created_at = order
        
        order_text = (
            f"📝 <b>Заказ #{order_id}</b>\n\n"
            f"👤 Пользователь: @{username or 'без username'}\n"
            f"🛍️ Услуга: {service}\n"
            f"💰 Сумма: {amount:,} UZS\n"
            f"💳 Способ оплаты: {payment_method}\n"
            f"📅 Дата: {created_at}"
        )
        
        await message.answer(
            order_text,
            reply_markup=keyboards.order_actions(order_id),
            parse_mode="HTML"
        )

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
            await bot.send_message(
                user_id,
                f"✅ <b>Ваш заказ #{order_id} подтвержден!</b>\n\n"
                f"Спасибо за покупку! 🎉",
                parse_mode="HTML"
            )
        except:
            pass
    
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ <b>ПОДТВЕРЖДЕН</b>",
            parse_mode="HTML"
        )
    except:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ <b>ПОДТВЕРЖДЕН</b>",
            parse_mode="HTML"
        )
    
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
            await bot.send_message(
                user_id,
                f"❌ <b>Ваш заказ #{order_id} отклонен</b>\n\n"
                f"Свяжитесь с поддержкой для уточнения: @Star_payuz_admin",
                parse_mode="HTML"
            )
        except:
            pass
    
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ <b>ОТКЛОНЕН</b>",
            parse_mode="HTML"
        )
    except:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n❌ <b>ОТКЛОНЕН</b>",
            parse_mode="HTML"
        )
    
    await callback.answer("❌ Заказ отклонен!")

@dp.message(F.text == "📢 Рассылка")
async def start_broadcast(message: types.Message, state: FSMContext):
    """Начать рассылку"""
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    # Проверяем авторизацию
    data = await state.get_data()
    if not data.get('admin_authorized'):
        await message.answer("❌ Сначала авторизуйтесь: /admin")
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
                await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=keyboards.main_menu(lang), parse_mode="HTML")
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
            "📋 <b>Bot qoidalari</b>\n\n"
            "1️⃣ Faqat to'g'ri ma'lumotlar kiriting\n"
            "2️⃣ To'lov chekini aniq yuboring\n"
            "3️⃣ Spam qilmang\n"
            "4️⃣ Administrator javobini kuting\n"
            "5️⃣ Qayta to'lov qilmang\n\n"
            "⚠️ Qoidalarni buzgan foydalanuvchilar bloklangan bo'ladi!"
        )
    else:
        rules_text = (
            "📋 <b>Правила бота</b>\n\n"
            "1️⃣ Вводите только правильные данные\n"
            "2️⃣ Отправляйте четкий чек оплаты\n"
            "3️⃣ Не спамьте\n"
            "4️⃣ Ждите ответа администратора\n"
            "5️⃣ Не делайте повторную оплату\n\n"
            "⚠️ Пользователи, нарушившие правила, будут заблокированы!"
        )
    
    await message.answer(rules_text, parse_mode="HTML", reply_markup=keyboards.back_to_menu(lang))

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ панели!")
        return
    
    # Проверяем авторизацию
    data = await state.get_data()
    if data.get('admin_authorized'):
        # Уже авторизован
        await message.answer(
            "🔐 <b>Админ панель Star_payuz</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboards.admin_menu(),
            parse_mode="HTML"
        )
    else:
        # Запрашиваем логин
        await message.answer(
            "🔐 <b>Вход в админ панель</b>\n\n"
            "Введите логин:",
            parse_mode="HTML"
        )
        await state.set_state(AdminAuthStates.waiting_for_login)

@dp.message(AdminAuthStates.waiting_for_login)
async def admin_login_received(message: types.Message, state: FSMContext):
    """Получение логина"""
    login = message.text.strip()
    
    if login == config.ADMIN_LOGIN:
        await state.update_data(admin_login=login)
        await message.answer(
            "✅ <b>Логин принят</b>\n\n"
            "Введите пароль:",
            parse_mode="HTML"
        )
        await state.set_state(AdminAuthStates.waiting_for_password)
    else:
        await message.answer(
            "❌ <b>Неверный логин!</b>\n\n"
            "Попробуйте еще раз или /cancel для отмены",
            parse_mode="HTML"
        )

@dp.message(AdminAuthStates.waiting_for_password)
async def admin_password_received(message: types.Message, state: FSMContext):
    """Получение пароля"""
    password = message.text.strip()
    
    # Удаляем сообщение с паролем для безопасности
    try:
        await message.delete()
    except:
        pass
    
    if password == config.ADMIN_PASSWORD:
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

async def set_bot_commands():
    """Установка команд бота"""
    commands_uz = [
        types.BotCommand(command="start", description="Botni ishga tushirish"),
        types.BotCommand(command="help", description="Yordam"),
        types.BotCommand(command="qoida", description="Qoidalar"),
        types.BotCommand(command="admin", description="Admin panel")
    ]
    commands_ru = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Помощь"),
        types.BotCommand(command="qoida", description="Правила"),
        types.BotCommand(command="admin", description="Админ панель")
    ]
    await bot.set_my_commands(commands_uz, language_code="uz")
    await bot.set_my_commands(commands_ru, language_code="ru")
    await bot.set_my_commands(commands_uz)

async def main():
    database.init_db()
    await set_bot_commands()
    print("🚀 Бот Star_payuz запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


print("Hello world")
if __name__ == '__main__':
    asyncio.run(main())