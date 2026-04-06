import asyncio
import base64
import io
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyrogram.helpers import ikb, kb
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            ReplyKeyboardRemove, WebAppInfo)

from pytz import timezone
from Navy import bot

from config import (AKSES_DEPLOY, LOG_SELLER, SAWERIA_EMAIL, SAWERIA_USERID, SAWERIA_NAME, OWNER_ID)
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, Message, Tools
from Navy.helpers.Saweria import Saweria
from Navy.logger import logger

last_generated_time = {}
transactions = {}

waktu_jkt = timezone("Asia/Jakarta")

async def add_transaction(user_id, month):
    expired = await dB.get_expired_date(user_id)
    if not expired:
        now = datetime.now(waktu_jkt)
        expired = now + relativedelta(months=month)
        await dB.set_expired_date(user_id, expired)

@CMD.CALLBACK("^go_payment")
async def user_aggre(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    del_ = await client.send_message(
        user_id, "<b>Please wait...</b>", reply_markup=ReplyKeyboardRemove()
    )
    await del_.delete()
    await callback_query.message.delete()
    buttons = ButtonUtils.plus_minus(0, user_id)
    return await client.send_message(
        user_id,
        Message.TEXT_PAYMENT(0, 0, 0),
        disable_web_page_preview=True,
        reply_markup=buttons,
    )


@CMD.CALLBACK("^batal_payment")
async def _(client, callback):
    return await cancel_payment(client, callback)

@CMD.CALLBACK("^(kurang|tambah)")
async def _(client, callback_query):
    await callback_query.answer()

    data = callback_query.data.split()
    QUERY = data[0]
    BULAN = int(data[1])

    HARGA = 17000

    try:
        if QUERY == "kurang" and BULAN > 1:
            BULAN -= 1
        elif QUERY == "tambah" and BULAN < 12:
            BULAN += 1

        TOTAL_HARGA = HARGA * BULAN

        # 🔘 Tombol + / -
        buttons = [
            [
                InlineKeyboardButton("➖", callback_data=f"kurang {BULAN}"),
                InlineKeyboardButton("➕", callback_data=f"tambah {BULAN}")
            ]
        ]

        # ✅ Confirm hanya muncul jika valid
        if BULAN > 0 and TOTAL_HARGA >= 1000:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "✅ Confirm",
                        callback_data=f"confirm {BULAN} {TOTAL_HARGA}"
                    )
                ]
            )

        await callback_query.edit_message_text(
            Message.TEXT_PAYMENT(HARGA, TOTAL_HARGA, BULAN),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(e)


@CMD.CALLBACK("^confirm")
async def _(client, callback_query):
    await callback_query.answer()
    data = callback_query.data.split()
    month = int(data[1])
    amount = int(data[2])
    user_id = callback_query.from_user.id
    full = f"{callback_query.from_user.first_name}"
    await callback_query.message.delete()

    if amount <15000:
        return await client.send_message(user_id, "<b>The price cannot be 15000.</b>")
    if month == 0:
        return await client.send_message(user_id, "<b>The mont cannot be 0.</b>")

    try:
        if user_id in transactions:
            return await callback_query.message.reply(
                "**__📑 You still have a pending transaction.__**",
                reply_markup=ikb([[("❌ Cancel", "batal_payment")]]),
            )

        loading = await callback_query.message.reply(
            "<b><i>⏳ Generating QR Code...</i></b>"
        )
        item_name = f"Sewa Userbot {month} Months"
        output_path = f"/storage/cache/{user_id}.png"
        qrstring, hasil_idpayment, qris_path = await Saweria.create_payment_qr(
            SAWERIA_USERID, SAWERIA_NAME, amount, SAWERIA_EMAIL, output_path
        )
        now = datetime.now(waktu_jkt)
        hasil_amount = Saweria.get_amount(qrstring)
        hasil_expired = datetime.now() + timedelta(minutes=3)
        sent_msg = await client.send_photo(
            user_id,
            qris_path,
            caption=f"""
<b>📃「 Waiting Payment 」</b>

<blockquote expandable><b><i>📦 TRANSACTION DONE**
💵 Price: `{Message.format_rupiah(amount)}`
💰 Total Payment: `{Message.format_rupiah(hasil_amount)}`
⏰ Expires At: `{hasil_expired}`
🛒 Item: `{item_name}` 

Please scan the QRIS above to make your payment.
If you have issues, contact <a href='tg://user?id={OWNER_ID}'>ADMIN</a>.
Click the ❌ Cancel button below to cancel the transaction.</i></b></blockquote>

<blockquote>© Auto Payment @{client.me.username}</blockquote>
""",
            reply_markup=ikb([[("❌ Cancel", "batal_payment")]]),
        )
        await loading.delete()
        if os.path.exists(qris_path):
            os.remove(qris_path)

        transactions[user_id] = {
            "qris_path": qris_path,
            "expire_time": hasil_expired,
            "message_id": sent_msg.id,
            "done": False,
        }

        while True:
            await asyncio.sleep(1)
            trans = transactions.get(user_id)
            if not trans or trans["done"]:
                break
            if datetime.now() > trans["expire_time"]:
                if not trans["done"]:
                    await client.send_message(
                        user_id, "<b><i>Payment canceled due to timeout.</i></b>"
                    )
                    await client.delete_messages(
                        chat_id=callback_query.message.chat.id,
                        message_ids=trans["message_id"],
                    )
                    del transactions[user_id]
                break
            try:
                is_paid = await Saweria.check_paid_status(hasil_idpayment)
                if is_paid and not trans["done"]:
                    trans["done"] = True
                    await callback_query.message.reply(
                        "<b><i>Payment received, processing your order...</i></b>"
                    )
                    await client.send_message(
                        LOG_SELLER,
                        f"""
<b>📝「 Payment Successfully 」</b>

<blockquote expandable><b><i>👤 User Name: `{callback_query.from_user.first_name}`
🆔 User ID: `{callback_query.from_user.id}`
📦 Item: `{item_name}`
💵 Price: `{Message.format_rupiah(amount)}`
📅 Date: `{now.strftime('%d-%m-%Y')}`
⏰ Time: `{now.strftime('%H:%M')}`</i></b></blockquote>

<blockquote>© Auto Payment @{client.me.username}</blockquote>
""",
                    )
                    await client.delete_messages(
                        chat_id=callback_query.message.chat.id,
                        message_ids=transactions[user_id]["message_id"],
                    )
                    del transactions[user_id]

                    await add_transaction(user_id, month)
                    if user_id not in AKSES_DEPLOY:
                        AKSES_DEPLOY.append(user_id)
                    await client.send_message(
                        user_id,
                        "<b><i>✅ Payment successful.\nClick the button below to create your Userbot.</i></b>",
                        reply_markup=kb(
                            [["✨ Mulai Buat Userbot"]],
                            resize_keyboard=True,
                            one_time_keyboard=True,
                        ),
                    )
                    break

            except Exception as e:
                print(f"Error checking payment: {e}")

    except Exception:
        logger.error(f"ERROR: {traceback.format_exc()}")
        return await client.send_message(
            user_id, "<b>An error occurred, please try again.</b>"
        )

async def cancel_payment(client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.answer()

    if user_id in transactions:
        qris_path = transactions[user_id]["qris_path"]

        if os.path.exists(qris_path):
            os.remove(qris_path)

        try:
            await client.delete_messages(
                chat_id=callback_query.message.chat.id,
                message_ids=transactions[user_id]["message_id"],
            )
        except Exception:
            pass

        del transactions[user_id]

        await callback_query.message.reply(
            "**__📑 Transaksi Berhasil Dibatalkan.__**",
            reply_markup=ButtonUtils.start_menu(is_admin=False),
        )
    else:
        await callback_query.message.reply("**__❌ Tidak Ada Transaksi Yang Aktif__**")

async def qris_cmd(client, message):
    em = Emoji(client)
    await em.get()

    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return await message.reply(
            f"{em.gagal}**Sorry, this feature is only for the Owner.**"
        )

    if user_id in transactions:
        return await message.reply(
            f"""
<b><i>{em.gagal}You still have an ongoing transaction.
{em.warn}You can cancel it using <code>.cancelpay</code>.</i></b>
"""
        )

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply(
                f"{em.gagal}**Incorrect format. Use:** <code>.pay amount, description</code>"
            )
        try:
            amount_str, description = args[1].split(",", maxsplit=1)
            amount = int(amount_str.strip())
            description = description.strip()
        except ValueError:
            return await message.reply(
                f"{em.gagal}**Incorrect format. Use:** <code>.pay amount, description</code>"
            )

        loading = await message.reply(f"{em.proses}**Prosesing..**")
        output_path = f"/storage/cache/{user_id}.png"
        qrstring, hasil_idpayment, qris_path = await Saweria.create_payment_qr(
            SAWERIA_USERID, SAWERIA_NAME, amount, SAWERIA_EMAIL, output_path
        )
        hasil_amount = Saweria.get_amount(qrstring)
        hasil_expired = datetime.now() + timedelta(minutes=3)
        sent_message = await message.reply_photo(
            qris_path,
            caption=(
                f"""
<b>📃「 Waiting Payment 」</b>

<blockquote expandable><b><i>{em.profil}Item: `{description}`
{em.net}Price: `{Message.format_rupiah(amount)}`
{em.speed}Total Payment: `{Message.format_rupiah(hasil_amount)}`
{em.warn}Expiration Time: `{hasil_expired}`

Please scan the QRIS above to complete the payment.
If you encounter any issues, contact <a href='tg://user?id={OWNER_ID}'>ADMIN</a>
Type `.cancelpay` to cancel the transaction.</i></b></blockquote>

<blockquote>© Auto Payment @{bot.me.username}</blockquote>
"""
            ),
        )
        await loading.delete()

        if os.path.exists(qris_path):
            os.remove(qris_path)

        transactions[user_id] = {
            "qris_path": qris_path,
            "expire_time": hasil_expired,
            "message_id": sent_message.id,
            "done": False,
        }

        while True:
            await asyncio.sleep(1)
            trans = transactions.get(user_id)
            if not trans or trans["done"]:
                break
            if datetime.now() > trans["expire_time"]:
                if not trans["done"]:
                    await client.send_message(
                        user_id, "<b><i>Payment canceled due to timeout.</i></b>"
                    )
                    await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=trans["message_id"],
                    )
                    del transactions[user_id]
                break
            try:
                is_paid = await Saweria.check_paid_status(hasil_idpayment)
                if is_paid and not trans["done"]:
                    trans["done"] = True
                    await message.reply(
                        f"""
<blockquote><b><i>{em.sukses}Payment received successfully!

{em.profil}Item: `{description}`
{em.net}Price: `{Message.format_rupiah(amount)}`
{em.speed}Total Paid: `{Message.format_rupiah(hasil_amount)}`</i></b></blockquote>
"""
                    )
                    await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=transactions[user_id]["message_id"],
                    )
                    del transactions[user_id]
                    return

            except Exception as e:
                print(f"Error while checking payment: {e}")

    except ValueError:
        return await message.reply(
            f"{em.gagal}**Invalid amount. Make sure it is a number.**"
        )


async def cancelpay_cmd(client, message):
    em = Emoji(client)
    await em.get()

    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return await message.reply(
            f"{em.gagal}**Sorry, this feature is only for the Owner.**"
        )

    if user_id in transactions:
        await client.delete_messages(
            chat_id=message.chat.id, message_ids=transactions[user_id]["message_id"]
        )
        del transactions[user_id]

        return await message.reply(
            f"{em.sukses}**Transaction has been successfully canceled.**"
        )
    else:
        return await message.reply(
            f"{em.warn}**There is no active transaction to cancel.**"
        )