#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Функции с Telegram Premium эмодзи для бота Star_payuz
Используем премиум эмодзи через теги <tg-emoji>
"""

def get_premium_welcome(name, lang="ru"):
    """Приветствие с Premium эмодзи"""
    if lang == "uz":
        return f'''<tg-emoji emoji-id="4976940882071651344">👋</tg-emoji> <b>Xush kelibsiz, {name}!</b>

<tg-emoji emoji-id="5936259309812846957">🌟</tg-emoji> <b>Bizda siz Telegram Stars va Telegram Premium'ni o'z akkauntingiz uchun so'm orqali xarid qilishingiz mumkin</b><tg-emoji emoji-id="5460991276948143687">🔥</tg-emoji>

<b>Shuningdek, boshqa mashhur xizmatlarni ham arzon narxlarda sotib olish imkoniyati mavjud.</b><tg-emoji emoji-id="5458488840022933066">🛍️</tg-emoji>

<b>Yaxshi xaridlar tilaymiz!</b>

<tg-emoji emoji-id="5406745015365943482">👇</tg-emoji> <b>Kerakli xizmatni tanlang va buyurtma bering!</b>'''
    else:
        return f'''<tg-emoji emoji-id="4976940882071651344">👋</tg-emoji> <b>Добро пожаловать, {name}!</b>

<tg-emoji emoji-id="5936259309812846957">🌟</tg-emoji> <b>У нас вы можете купить Telegram Stars и Telegram Premium для своего аккаунта за сумы</b><tg-emoji emoji-id="5460991276948143687">🔥</tg-emoji>

<b>Также есть возможность приобрести другие популярные услуги по выгодным ценам.</b><tg-emoji emoji-id="5458488840022933066">🛍️</tg-emoji>

<b>Желаем удачных покупок!</b>

<tg-emoji emoji-id="5406745015365943482">👇</tg-emoji> <b>Выберите услугу и оформите заказ!</b>'''


def get_premium_service_selected(service, price, lang="ru"):
    """Выбор услуги с Premium эмодзи"""
    if lang == "uz":
        return f'''<tg-emoji emoji-id="5456390099958773299">✅</tg-emoji> Siz tanladingiz: <b>{service}</b>

<tg-emoji emoji-id="5456390099958773299">💰</tg-emoji> Narxi: <b>{price:,} UZS</b>

<tg-emoji emoji-id="5456390099958773299">👇</tg-emoji> To'lov usulini tanlang:'''
    else:
        return f'''<tg-emoji emoji-id="5456390099958773299">✅</tg-emoji> Вы выбрали: <b>{service}</b>

<tg-emoji emoji-id="5456390099958773299">💰</tg-emoji> Цена: <b>{price:,} UZS</b>

<tg-emoji emoji-id="5456390099958773299">👇</tg-emoji> Выберите способ оплаты:'''


def get_premium_payment_info(service, price, method, lang="ru"):
    """Информация об оплате с Premium эмодзи"""
    if lang == "uz":
        return f'''<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> <b>To'lov ma'lumotlari ({method})</b>

<tg-emoji emoji-id="5458488840022933066">🛍️</tg-emoji> Xizmat: <b>{service}</b>
<tg-emoji emoji-id="5456390099958773299">💰</tg-emoji> Summa: <b>{price:,} UZS</b>

<tg-emoji emoji-id="5456390099958773299">📱</tg-emoji> Karta raqami:
<code>8600 1234 5678 9012</code>

<tg-emoji emoji-id="5456390099958773299">👤</tg-emoji> Qabul qiluvchi: <b>Star_payuz</b>

<tg-emoji emoji-id="5456390099958773299">📸</tg-emoji> To'lovdan keyin chek rasmini shu chatga yuboring.

<tg-emoji emoji-id="5461137215641895106">⚠️</tg-emoji> <b>Muhim:</b> Rasmda summa va vaqt ko'rinishi kerak!'''
    else:
        return f'''<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> <b>Реквизиты для оплаты ({method})</b>

<tg-emoji emoji-id="5458488840022933066">🛍️</tg-emoji> Услуга: <b>{service}</b>
<tg-emoji emoji-id="5456390099958773299">💰</tg-emoji> Сумма: <b>{price:,} UZS</b>

<tg-emoji emoji-id="5456390099958773299">📱</tg-emoji> Номер карты:
<code>8600 1234 5678 9012</code>

<tg-emoji emoji-id="5456390099958773299">👤</tg-emoji> Получатель: <b>Star_payuz</b>

<tg-emoji emoji-id="5456390099958773299">📸</tg-emoji> После оплаты отправьте скриншот чека в этот чат.

<tg-emoji emoji-id="5461137215641895106">⚠️</tg-emoji> <b>Важно:</b> На скриншоте должна быть видна сумма и время платежа!'''


def get_premium_order_accepted(order_id, lang="ru"):
    """Подтверждение заказа с Premium эмодзи"""
    if lang == "uz":
        return (
            f"<tg-emoji emoji-id=\"5208869687286316655\">✅</tg-emoji> <b>Buyurtmangiz #{order_id} qabul qilindi!</b>\n\n"
            f"<tg-emoji emoji-id=\"5451732530048802485\">⏳</tg-emoji> Administrator tekshiruvini kuting.\n"
            f"Odatda bu 5–30 daqiqa davom etadi.\n\n"
            f"<tg-emoji emoji-id=\"5350421256627838238\">📬</tg-emoji> Buyurtma tayyor bo'lgach sizga xabar beramiz."
        )
    else:
        return (
            f"<tg-emoji emoji-id=\"5208869687286316655\">✅</tg-emoji> <b>Ваш заказ #{order_id} принят!</b>\n\n"
            f"<tg-emoji emoji-id=\"5451732530048802485\">⏳</tg-emoji> Ожидайте проверки администратором.\n"
            f"Обычно это занимает 5–30 минут.\n\n"
            f"<tg-emoji emoji-id=\"5350421256627838238\">📬</tg-emoji> Мы уведомим вас, когда заказ будет обработан."
        )


def get_premium_help(lang="ru"):
    """Помощь с Premium эмодзи"""
    if lang == "uz":
        return (
            "<tg-emoji emoji-id=\"5461098956073222348\">🎙</tg-emoji> <b>Star_payuz — Premium & Stars xizmati</b>\n\n"
            "<tg-emoji emoji-id=\"5317023930236549785\">📌</tg-emoji> <b>Buyruqlar:</b>\n"
            "/start — Asosiy menyu\n"
            "/help — Yordam\n"
            "/qoida — Qoidalar\n\n"
            "<tg-emoji emoji-id=\"5262844652964303985\">💡</tg-emoji> <b>Bot imkoniyatlari:</b>\n"
            "<tg-emoji emoji-id=\"6154661321687176046\">🌟</tg-emoji> Telegram Stars to'ldirish\n"
            "<tg-emoji emoji-id=\"5370784581341422520\">⭐️</tg-emoji> Telegram Premium sotib olish\n"
            "<tg-emoji emoji-id=\"5199785165735367039\">⚡️</tg-emoji> Tez va qulay xizmat\n"
            "<tg-emoji emoji-id=\"6039457435381402923\">🔒</tg-emoji> Xavfsiz to'lov\n\n"
            "<tg-emoji emoji-id=\"5201990176175299013\">📞</tg-emoji> Yordam: @StarPayUzAdmin || @kamron235\n\n"
            "<tg-emoji emoji-id=\"5382194935057372936\">⏱️</tg-emoji> Buyurtmalar 5–30 daqiqada bajariladi"
        )
    else:
        return (
            "<tg-emoji emoji-id=\"5461098956073222348\">🎙</tg-emoji> <b>Star_payuz — Premium & Stars сервис</b>\n\n"
            "<tg-emoji emoji-id=\"5317023930236549785\">📌</tg-emoji> <b>Команды:</b>\n"
            "/start — Главное меню\n"
            "/help — Помощь\n"
            "/qoida — Правила\n\n"
            "<tg-emoji emoji-id=\"5262844652964303985\">💡</tg-emoji> <b>Возможности бота:</b>\n"
            "<tg-emoji emoji-id=\"6154661321687176046\">🌟</tg-emoji> Пополнение Telegram Stars\n"
            "<tg-emoji emoji-id=\"5370784581341422520\">⭐️</tg-emoji> Покупка Telegram Premium\n"
            "<tg-emoji emoji-id=\"5199785165735367039\">⚡️</tg-emoji> Быстрый и удобный сервис\n"
            "<tg-emoji emoji-id=\"6039457435381402923\">🔒</tg-emoji> Безопасная оплата\n\n"
            "<tg-emoji emoji-id=\"5201990176175299013\">📞</tg-emoji> Поддержка: @StarPayUzAdmin || @kamron235\n\n"
            "<tg-emoji emoji-id=\"5382194935057372936\">⏱️</tg-emoji> Заказы выполняются за 5–30 минут"
        )


def get_premium_category_name(category, lang="ru"):
    """Названия категорий с Premium эмодзи"""
    categories = {
        "premium": {
            "uz": f'<tg-emoji emoji-id="5348489165589724843">💎</tg-emoji> Premium',
            "ru": f'<tg-emoji emoji-id="5348489165589724843">💎</tg-emoji> Premium'
        },
        "stars": {
            "uz": f'<tg-emoji emoji-id="5936259309812846957">🌟</tg-emoji> Stars',
            "ru": f'<tg-emoji emoji-id="5936259309812846957">🌟</tg-emoji> Stars'
        },
        "boost": {
            "uz": f'<tg-emoji emoji-id="5460991276948143687">⚡</tg-emoji> Boost',
            "ru": f'<tg-emoji emoji-id="5460991276948143687">⚡</tg-emoji> Boost'
        },
        "gifts": {
            "uz": f'<tg-emoji emoji-id="5458488840022933066">🎁</tg-emoji> Gifts',
            "ru": f'<tg-emoji emoji-id="5458488840022933066">🎁</tg-emoji> Gifts'
        },
        "robux": {
            "uz": f'<tg-emoji emoji-id="5458649351540712147">🎮</tg-emoji> Robux',
            "ru": f'<tg-emoji emoji-id="5458649351540712147">🎮</tg-emoji> Robux'
        }
    }
    
    return categories.get(category, {}).get(lang, category)