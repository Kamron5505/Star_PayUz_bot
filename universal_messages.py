#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальные функции с обычными эмодзи для всех пользователей
"""

def get_universal_welcome(name, lang="ru"):
    """Приветствие с обычными эмодзи для всех пользователей"""
    if lang == "uz":
        return f'''👋 <b>Xush kelibsiz, {name}!</b>

⭐️ <b>Bizda siz Telegram Stars va Telegram Premium'ni o'z akkauntingiz uchun so'm orqali xarid qilishingiz mumkin</b> 💳🔥

<b>Shuningdek, boshqa mashhur xizmatlarni ham arzon narxlarda sotib olish imkoniyati mavjud.</b>🛍️

<b>Yaxshi xaridlar tilaymiz!</b>

👇 <b>Kerakli xizmatni tanlang va buyurtma bering!</b>'''
    else:
        return f'''👋 <b>Добро пожаловать, {name}!</b>

⭐️ <b>У нас вы можете купить Telegram Stars и Telegram Premium для своего аккаунта за сумы</b> 💳🔥

<b>Также есть возможность приобрести другие популярные услуги по выгодным ценам.</b>🛍️

<b>Желаем удачных покупок!</b>

👇 <b>Выберите услугу и оформите заказ!</b>'''

def get_universal_service_selected(service, price, lang="ru"):
    """Выбор услуги с обычными эмодзи"""
    if lang == "uz":
        return f'''✅ Siz tanladingiz: {service}

💰 Narxi: {price:,} UZS

👇 To'lov usulini tanlang:'''
    else:
        return f'''✅ Вы выбрали: {service}

💰 Цена: {price:,} UZS

👇 Выберите способ оплаты:'''

def get_universal_payment_info(service, price, method, lang="ru"):
    """Информация об оплате с обычными эмодзи"""
    if lang == "uz":
        return f'''💳 To'lov ma'lumotlari ({method}):

🛍️ Xizmat: {service}
💰 Summa: {price:,} UZS

📱 Karta raqami: 8600 1234 5678 9012
👤 Qabul qiluvchi: Star_payuz

📸 To'lovdan keyin chek rasmini shu chatga yuboring.

⚠️ Muhim: Rasmda summa va vaqt ko'rinishi kerak!'''
    else:
        return f'''💳 Реквизиты для оплаты ({method}):

🛍️ Услуга: {service}
💰 Сумма: {price:,} UZS

📱 Номер карты: 8600 1234 5678 9012
👤 Получатель: Star_payuz

📸 После оплаты отправьте скриншот чека в этот чат.

⚠️ Важно: На скриншоте должна быть видна сумма и время платежа!'''

def get_universal_order_accepted(order_id, lang="ru"):
    """Подтверждение заказа с обычными эмодзи"""
    if lang == "uz":
        return f'''✅ Buyurtmangiz #{order_id} qabul qilindi!

⏳ Administrator tekshiruvini kuting
Odatda bu 5-30 daqiqa davom etadi

📬 Buyurtma tayyor bo'lgach sizga xabar beramiz'''
    else:
        return f'''✅ Ваш заказ #{order_id} принят!

⏳ Ожидайте проверки администратором
Обычно это занимает 5-30 минут

📬 Мы уведомим вас, когда заказ будет обработан'''

def get_universal_help(lang="ru"):
    """Помощь с обычными эмодзи"""
    if lang == "uz":
        return f'''ℹ️ Star_payuz - Premium & Stars Xizmati

📌 Mavjud buyruqlar:

/start - Asosiy menyu
/help - Yordam
/qoida - Qoidalar
/admin - Admin panel

💡 Nima qila oladi bu bot?

⭐ <b>Star_payuz Bot</b> — Premium & Stars Xizmati
🚀 Telegram Premium sotib olish
💎 Stars to'ldirish
⚡ Tezkor • Ishonchli • Qulay
🔒 Xavfsiz to'lovlar

📞 Yordam: @kamron235

⚡ Buyurtmalar 5-30 daqiqada bajariladi'''
    else:
        return f'''ℹ️ Star_payuz - Premium & Stars Service

📌 Доступные команды:

/start - Главное меню
/help - Помощь
/qoida - Правила
/admin - Админ панель

💡 Что может делать этот бот?

⭐ <b>Star_payuz Bot</b> — Premium & Stars Service
🚀 Telegram Premium покупка
💎 Stars пополнение
⚡ Быстро • Надежно • Удобно
🔒 Безопасные платежи

📞 Поддержка: @kamron235

⚡ Обработка заказов: 5-30 минут'''

# Функции для категорий
def get_universal_category_name(category, lang="ru"):
    """Названия категорий с обычными эмодзи"""
    categories = {
        "premium": {
            "uz": f'💎 Premium',
            "ru": f'💎 Premium'
        },
        "stars": {
            "uz": f'🌟 Stars',
            "ru": f'🌟 Stars'
        },
        "boost": {
            "uz": f'⚡ Boost',
            "ru": f'⚡ Boost'
        },
        "gifts": {
            "uz": f'🎁 Gifts',
            "ru": f'🎁 Gifts'
        },
        "virtual_numbers": {
            "uz": f'📱 Virtual numbers',
            "ru": f'📱 Virtual numbers'
        },
        "robux": {
            "uz": f'🎮 Robux',
            "ru": f'🎮 Robux'
        }
    }
    
    return categories.get(category, {}).get(lang, category)