"""
Хендлер пополнения баланса через SMS мониторинг.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import api_client
import database

router = Router()
UZ_TZ = timezone(timedelta(hours=5))


class TopupStates(StatesGroup):
    waiting_for_amount  = State()
    waiting_for_payment = State()


def _cancel_kb(payment_id: str, lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔄 Tekshirish" if lang == "uz" else "🔄 Проверить",
            callback_data=f"check_pay_{payment_id}")],
        [InlineKeyboardButton(
            text="❌ Bekor qilish" if lang == "uz" else "❌ Отменить",
            callback_data=f"cancel_pay_{payment_id}")],
    ])


# ── Открыть раздел пополнения ─────────────────────────────────────────────────

@router.callback_query(F.data == "topup_balance")
async def topup_start(callback: CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)

    if lang == "uz":
        text = (
            "💳 <b>Balansni to'ldirish</b>\n\n"
            "Quyidagi miqdorni kiriting:\n\n"
            "🔻 Minimal: <b>1 000 so'm</b>\n"
            "🔺 Maksimal: <b>2 500 000 so'm</b>"
        )
    else:
        text = (
            "💳 <b>Пополнение баланса</b>\n\n"
            "Введите сумму:\n\n"
            "🔻 Минимум: <b>1 000 сум</b>\n"
            "🔺 Максимум: <b>2 500 000 сум</b>"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="◀️ Orqaga" if lang == "uz" else "◀️ Назад",
            callback_data="back_to_menu")
    ]])

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")

    await state.set_state(TopupStates.waiting_for_amount)
    await callback.answer()


# ── Получить сумму ────────────────────────────────────────────────────────────

@router.message(TopupStates.waiting_for_amount)
async def topup_amount(message: Message, state: FSMContext):
    lang = database.get_user_language(message.from_user.id)

    try:
        # Убираем всё кроме цифр
        clean = ''.join(filter(str.isdigit, message.text.strip()))
        amount = int(clean)
    except (ValueError, TypeError):
        err = "❌ Faqat raqam kiriting!" if lang == "uz" else "❌ Введите только число!"
        await message.answer(err)
        return

    if amount < 1000:
        await message.answer("❌ Minimal 1 000 so'm!" if lang == "uz" else "❌ Минимум 1 000 сум!")
        return
    if amount > 2500000:
        await message.answer("❌ Maksimal 2 500 000 so'm!" if lang == "uz" else "❌ Максимум 2 500 000 сум!")
        return

    result = await api_client.create_payment(message.from_user.id, amount)

    if not result.get("success"):
        await message.answer("❌ Xatolik. Qayta urinib ko'ring." if lang == "uz" else "❌ Ошибка. Попробуйте снова.")
        await state.clear()
        return

    data      = result["data"]
    payment_id = data["payment_id"]
    card      = data["card_number"]
    owner     = data["card_owner"]

    now    = datetime.now(UZ_TZ)
    expire = now + timedelta(seconds=300)

    if lang == "uz":
        text = (
            f"✅ <b>To'lov so'rovi yaratildi!</b>\n\n"
            f"📦 Buyurtma: <code>{payment_id[-10:]}</code>\n"
            f"💳 Miqdori: <b>{amount:,} so'm</b>\n\n"
            f"💳 To'lov uchun karta:\n"
            f"<code>{card}</code>\n"
            f"👤 {owner}\n\n"
            f"⏰ To'lov amalga oshirilgach, bot avtomatik aniqlaydi.\n\n"
            f"⚠️ Muddat: {now.strftime('%H:%M:%S')} — {expire.strftime('%H:%M:%S')} (Toshkent)\n"
            f"Aniq <b>5 daqiqa</b>. Undan keyin <b>avtomatik bekor qilinadi!</b>"
        )
    else:
        text = (
            f"✅ <b>Заявка создана!</b>\n\n"
            f"📦 Заказ: <code>{payment_id[-10:]}</code>\n"
            f"💳 Сумма: <b>{amount:,} сум</b>\n\n"
            f"💳 Карта для оплаты:\n"
            f"<code>{card}</code>\n"
            f"👤 {owner}\n\n"
            f"⏰ После оплаты бот автоматически определит.\n\n"
            f"⚠️ Срок: {now.strftime('%H:%M:%S')} — {expire.strftime('%H:%M:%S')} (Ташкент)\n"
            f"Ровно <b>5 минут</b>. Потом <b>автоматически отменится!</b>"
        )

    await message.answer(text, reply_markup=_cancel_kb(payment_id, lang), parse_mode="HTML")
    await state.update_data(payment_id=payment_id, amount=amount)
    await state.set_state(TopupStates.waiting_for_payment)

    asyncio.create_task(_poll(message.bot, message.from_user.id, payment_id, amount, lang, state))


# ── Polling ───────────────────────────────────────────────────────────────────

async def _poll(bot: Bot, user_id: int, payment_id: str, amount: int, lang: str, state: FSMContext):
    for _ in range(30):
        await asyncio.sleep(10)

        result = await api_client.check_payment(payment_id)
        status = result.get("data", {}).get("status")

        if status == "success":
            bal = await api_client.get_bot_user_balance(user_id)
            balance = bal.get("data", {}).get("balance_uzs", 0)

            if lang == "uz":
                text = (f"✅ <b>To'lov qabul qilindi!</b>\n\n"
                        f"💰 {amount:,} so'm\n💳 Balans: <b>{balance:,} so'm</b>")
            else:
                text = (f"✅ <b>Оплата получена!</b>\n\n"
                        f"💰 {amount:,} сум\n💳 Баланс: <b>{balance:,} сум</b>")

            try:
                await bot.send_message(user_id, text, parse_mode="HTML")
            except Exception as e:
                logging.error(f"[TOPUP] notify: {e}")

            await state.clear()
            return

        if status in ("failed", "cancelled"):
            break

    cur = await state.get_state()
    if cur == TopupStates.waiting_for_payment.state:
        msg = "❌ To'lov vaqti tugadi." if lang == "uz" else "❌ Время оплаты истекло."
        try:
            await bot.send_message(user_id, msg, parse_mode="HTML")
        except:
            pass
        await state.clear()


# ── Ручная проверка ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("check_pay_"))
async def manual_check(callback: CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)
    payment_id = callback.data.replace("check_pay_", "")

    result = await api_client.check_payment(payment_id)
    status = result.get("data", {}).get("status")

    if status == "success":
        data    = await state.get_data()
        amount  = data.get("amount", 0)
        bal     = await api_client.get_bot_user_balance(callback.from_user.id)
        balance = bal.get("data", {}).get("balance_uzs", 0)

        if lang == "uz":
            text = f"✅ <b>To'lov tasdiqlandi!</b>\n\n💰 {amount:,} so'm\n💳 Balans: <b>{balance:,} so'm</b>"
        else:
            text = f"✅ <b>Оплата подтверждена!</b>\n\n💰 {amount:,} сум\n💳 Баланс: <b>{balance:,} сум</b>"

        await callback.message.edit_text(text, parse_mode="HTML")
        await state.clear()
    else:
        msg = "⏳ Hali to'lov kelmadi." if lang == "uz" else "⏳ Оплата ещё не поступила."
        await callback.answer(msg, show_alert=True)


@router.callback_query(F.data.startswith("cancel_pay_"))
async def cancel_pay(callback: CallbackQuery, state: FSMContext):
    lang = database.get_user_language(callback.from_user.id)
    await state.clear()
    msg = "❌ Bekor qilindi." if lang == "uz" else "❌ Отменено."
    await callback.message.edit_text(msg, parse_mode="HTML")
    await callback.answer()


def register_topup_handlers(dp):
    dp.include_router(router)
