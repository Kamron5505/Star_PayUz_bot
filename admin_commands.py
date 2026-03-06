# -*- coding: utf-8 -*-
"""
Админ-команды для бота
"""

import asyncio
from aiogram import Bot
from database import get_pending_orders, update_order_status, get_all_users, get_user_count, get_all_products
from cache import cache, CACHE_KEYS
from translations_markdown import get_text_markdown
import config

async def notify_admin(bot, message: str, admin_id: int = None):
    """Отправить уведомление админу"""
    try:
        if admin_id:
            await bot.send_message(admin_id, message, parse_mode="MarkdownV2")
        else:
            # Отправляем всем админам из конфига
            for admin_id in config.ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, message, parse_mode="MarkdownV2")
                except:
                    pass
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")

async def send_broadcast(bot, message: str, user_ids: list):
    """Отправить рассылку пользователям"""
    success = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message, parse_mode="MarkdownV2")
            success += 1
            await asyncio.sleep(0.1)  # Задержка чтобы не спамить
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            failed += 1
    
    return success, failed

async def check_new_orders(bot, admin_id: int):
    """Проверить новые заказы и уведомить админа"""
    try:
        from database import get_pending_orders
        
        orders = get_pending_orders()
        if orders:
            message = "📊 *Новые заказы ожидают обработки:*\n\n"
            for order in orders:
                order_id, user_id, username, service, amount, payment_method, created_at = order
                message += f"• Заказ #{order_id}: {service} - {amount} UZS\n"
                message += f"  👤 Пользователь: {username or f'ID: {user_id}'}\n"
                message += f"  💰 Сумма: {amount} UZS\n"
                message += f"  📅 Создан: {created_at}\n\n"
            
            await notify_admin(bot, message, admin_id)
    except Exception as e:
        print(f"Ошибка при проверке заказов: {e}")

async def send_daily_stats(bot, admin_id: int):
    """Отправить ежедневную статистику"""
    try:
        from database import get_user_count, get_today_orders, get_today_revenue
        
        user_count = get_user_count()
        today_orders = get_today_orders()
        today_revenue = get_today_revenue()
        
        message = f"📊 *Ежедневная статистика*\n\n"
        message += f"👥 Всего пользователей: *{user_count}*\n"
        message += f"📦 Заказов сегодня: *{today_orders}*\n"
        message += f"💰 Выручка сегодня: *{today_revenue} UZS*\n"
        message += f"📅 {datetime.now().strftime('%d.%m.%Y')}"
        
        await bot.send_message(admin_id, message, parse_mode="MarkdownV2")
        
    except Exception as e:
        print(f"Ошибка отправки статистики: {e}")

async def send_order_notification(bot, order_id: int, user_id: int, service: str, amount: int):
    """Уведомить админа о новом заказе"""
    try:
        from database import get_user_info
        
        user_info = get_user_info(user_id)
        username = user_info.get('username', f'ID: {user_id}')
        
        message = f"🆕 *Новый заказ!*\n\n"
        message += f"📦 *Заказ #{order_id}*\n"
        message += f"👤 Пользователь: {username}\n"
        message += f"📦 Услуга: {service}\n"
        message += f"💰 Сумма: *{amount} UZS*\n"
        message += f"⏰ Время: {datetime.now().strftime('%H:%M')}"
        
        # Отправляем всем админам
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(admin_id, message, parse_mode="MarkdownV2")
            except:
                pass
                
    except Exception as e:
        print(f"Ошибка уведомления о заказе: {e}")

async def send_low_stock_notification(bot, product_name: str, current_stock: int):
    """Уведомить о низком остатке товара"""
    message = f"⚠️ *Внимание! Низкий остаток*\n\n"
    message += f"Товар: {product_name}\n"
    message += f"Остаток: {current_stock} шт.\n"
    message += "Необходимо пополнить запасы!"
    
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, message, parse_mode="MarkdownV2")
        except:
            pass

async def send_system_alert(bot, message: str, level: str = "info"):
    """Отправить системное уведомление админам"""
    emoji = "ℹ️"
    if level == "warning":
        emoji = "⚠️"
    elif level == "error":
        emoji = "❌"
    elif level == "success":
        emoji = "✅"
    
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id, 
                f"{emoji} *Системное уведомление*\n\n{message}",
                parse_mode="MarkdownV2"
            )
        except:
            pass

async def send_user_notification(bot, user_id: int, message: str, parse_mode="MarkdownV2"):
    """Отправить уведомление пользователю"""
    try:
        await bot.send_message(user_id, message, parse_mode=parse_mode)
        return True
    except Exception as e:
        print(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        return False