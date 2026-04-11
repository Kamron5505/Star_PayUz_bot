"""
StarPay API Client — подключение к Node.js API
"""
import aiohttp
import logging

API_URL = "https://web-production-72c54.up.railway.app"  # После деплоя: https://твой-проект.up.railway.app
API_KEY = "31d269e807984178959ba2133fdc82bd"
HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}


async def send_stars(telegram_user_id: int, amount: int) -> dict:
    """Отправить звёзды пользователю"""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API_URL}/api/send-stars", headers=HEADERS,
                              json={"telegram_user_id": str(telegram_user_id), "amount": amount}) as r:
                return await r.json()
    except Exception as e:
        logging.error(f"[API] send_stars: {e}")
        return {"success": False, "error": str(e)}


async def create_payment(telegram_id: int, amount_uzs: int) -> dict:
    """Создать заявку на пополнение баланса"""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API_URL}/api/sms/create-payment", headers=HEADERS,
                              json={"telegram_id": str(telegram_id), "amount_uzs": amount_uzs}) as r:
                return await r.json()
    except Exception as e:
        logging.error(f"[API] create_payment: {e}")
        return {"success": False, "error": str(e)}


async def check_payment(payment_id: str) -> dict:
    """Проверить статус платежа"""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API_URL}/api/sms/check-payment/{payment_id}", headers=HEADERS) as r:
                return await r.json()
    except Exception as e:
        logging.error(f"[API] check_payment: {e}")
        return {"success": False, "error": str(e)}


async def get_bot_user_balance(telegram_id: int) -> dict:
    """Баланс пользователя в сумах"""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API_URL}/api/bot/user/{telegram_id}/balance", headers=HEADERS) as r:
                return await r.json()
    except Exception as e:
        logging.error(f"[API] get_balance: {e}")
        return {"success": False, "error": str(e)}


async def buy_stars(telegram_id: int, stars: int) -> dict:
    """Купить звёзды — списывает сумы с баланса и отправляет звёзды"""
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{API_URL}/api/bot/buy-stars", headers=HEADERS,
                              json={"telegram_id": str(telegram_id), "stars": stars}) as r:
                return await r.json()
    except Exception as e:
        logging.error(f"[API] buy_stars: {e}")
        return {"success": False, "error": str(e)}
