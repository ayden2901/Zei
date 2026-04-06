import uuid
from pyrogram.helpers import kb
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import SUDO_OWNERS
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, no_commands
from Navy import bot
from Navy.logger import logger


# ===================================
# USER BUAT TICKET
# ===================================

async def pengguna_nanya(client, message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    logs = await dB.get_var(client.me.id, "FORWARD_LOG")
    if not logs:
        return await message.reply("Log belum diset oleh admin.")

    # pastikan logs selalu list
    if not isinstance(logs, list):
        logs = [logs]

    # 🔒 Cek ticket aktif
    active_ticket = state.get(user_id, "ACTIVE_TICKET")
    if active_ticket and state.get(active_ticket, "TICKET_STATUS") == "OPEN":
        return await message.reply(
            f"❗ Kamu masih punya ticket aktif.\n"
            f"🎫 TICKET: {active_ticket}\n"
            f"Tunggu sampai admin menjawab."
        )

    try:
        button = kb([["❌ Batalkan"]], resize_keyboard=True, one_time_keyboard=True)
        pesan = await client.ask(
            user_id,
            "<b>✍️ Tulis pertanyaan kamu:</b>",
            reply_markup=button,
        )

        if not pesan.text or pesan.text in no_commands:
            await pesan.delete()
            return await client.send_message(
                user_id,
                "<b>❌ Proses dibatalkan.</b>",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )

    except Exception as e:
        logger.error(f"ASK ERROR: {e}")
        return

    # 🎫 Buat Ticket ID
    ticket_id = str(uuid.uuid4())[:8].upper()
    state.set(ticket_id, "TICKET_USER", user_id)
    state.set(ticket_id, "TICKET_STATUS", "OPEN")
    state.set(user_id, "ACTIVE_TICKET", ticket_id)

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Akun", callback_data=f"akun_{ticket_id}"),
            InlineKeyboardButton("💬 Jawab", callback_data=f"jawab_{ticket_id}")
        ],
        [
            InlineKeyboardButton("🔒 Tutup Case", callback_data=f"close_{ticket_id}")
        ]
    ])

    ticket_header = (
        f"<blockquote expandable>"
        f"ㅤㅤ<b>QUESTION SUPPORT</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"<b>🎫 TICKET :</b> #{ticket_id}\n"
        f"<b>👤 Dari :</b> {full_name}\n"
        f"<b>🆔 User ID :</b> <code>{user_id}</code>\n"
        f"━━━━━━━━━━━━━\n"
        f"</blockquote>"
        f"<blockquote>"
        f"<b>💬 Pesan:</b>\n"
        f"</blockquote>"
    )

    # Forward ke semua log
    for log_id in logs:
        try:
            if pesan.text:
                await client.send_message(
                    log_id,
                    ticket_header + pesan.text,
                    reply_markup=buttons,
                    parse_mode=ParseMode.HTML
                )
            else:
                await pesan.copy(
                    log_id,
                    caption=ticket_header + (pesan.caption or ""),
                    reply_markup=buttons,
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"FORWARD ERROR ke {log_id}: {e}")

    return await client.send_message(
        user_id,
        f"<b>✅ Ticket berhasil dibuat!</b>\n🎫 ID: <code>{ticket_id}</code>",
        reply_markup=ButtonUtils.start_menu(is_admin=False),
    )


# ===================================
# CLOSE TICKET MANUAL
# ===================================
@CMD.CALLBACK("^close_")
async def close_ticket(client, callback_query):
    if not callback_query.from_user:
        return

    admin_id = callback_query.from_user.id
    if admin_id not in SUDO_OWNERS:
        return await callback_query.answer("Akses ditolak.", True)

    ticket_id = callback_query.data.split("_")[1]
    if state.get(ticket_id, "TICKET_STATUS") != "OPEN":
        return await callback_query.answer("Ticket sudah ditutup.", True)

    user_id = state.get(ticket_id, "TICKET_USER")
    state.set(ticket_id, "TICKET_STATUS", "CLOSED")
    state.set(user_id, "ACTIVE_TICKET", None)

    try:
        await client.send_message(user_id, f"🔒 Ticket #{ticket_id} telah ditutup.")
    except:
        pass

    await callback_query.answer("Ticket ditutup.")
    await callback_query.message.reply(f"✅ Ticket #{ticket_id} ditutup.")


# ===================================
# MODE BALAS ADMIN
# ===================================
@CMD.CALLBACK("^jawab_")
async def jawab_pesan(client, callback_query):
    if not callback_query.from_user:
        return

    admin_id = callback_query.from_user.id
    if admin_id not in SUDO_OWNERS:
        return await callback_query.answer("Akses ditolak.", True)

    if state.get(admin_id, "REPLY_MODE"):
        return await callback_query.answer("Masih dalam mode balas!", True)

    ticket_id = callback_query.data.split("_")[1]
    if state.get(ticket_id, "TICKET_STATUS") != "OPEN":
        return await callback_query.answer("Ticket sudah ditutup.", True)

    state.set(admin_id, "REPLY_MODE", ticket_id)
    state.set(admin_id, "REPLY_ACTIVE", True)

    await callback_query.answer("Mode balas aktif.")
    await callback_query.message.reply(f"✍️ Balas sekarang untuk Ticket #{ticket_id}")


# ===================================
# LIHAT AKUN
# ===================================
@CMD.CALLBACK("^akun_")
async def lihat_akun(client, callback_query):
    if not callback_query.from_user:
        return

    admin_id = callback_query.from_user.id
    if admin_id not in SUDO_OWNERS:
        return await callback_query.answer("Akses ditolak.", True)

    ticket_id = callback_query.data.split("_")[1]
    user_id = state.get(ticket_id, "TICKET_USER")
    if not user_id:
        return await callback_query.answer("Ticket tidak ditemukan.", True)

    await callback_query.answer()
    await callback_query.message.reply(
        f"👤 User ID: <code>{user_id}</code>",
        parse_mode=ParseMode.HTML
    )


# ===================================
# SET LOG MULTIPLE
# ===================================
@CMD.BOT("setlog")
async def setlog_handler(client, message):
    if not message.from_user:
        return
    if message.from_user.id not in SUDO_OWNERS:
        return

    if len(message.command) < 2:
        return await message.reply(
            "Gunakan format:\n/setlog <chat_id atau user_id> [user_id2 ...]"
        )

    target_ids = []
    for arg in message.command[1:]:
        try:
            target_ids.append(int(arg))
        except ValueError:
            return await message.reply(f"⚠️ ID harus angka: {arg}")

    # simpan sebagai list
    await dB.set_var(client.me.id, "FORWARD_LOG", target_ids)

    await message.reply(
        f"✅ Log forward diatur ke ID: `{', '.join(map(str, target_ids))}`"
    )


# ===================================
# KIRIM BALASAN ADMIN
# ===================================
@CMD.NO_CMD("ANSWER", bot)
async def kirim_balasan(client, message):
    if not message.from_user:
        return

    admin_id = message.from_user.id
    if admin_id not in SUDO_OWNERS:
        return

    ticket_id = state.get(admin_id, "REPLY_MODE")
    if not ticket_id:
        return

    if state.get(ticket_id, "TICKET_STATUS") != "OPEN":
        state.set(admin_id, "REPLY_MODE", None)
        state.set(admin_id, "REPLY_ACTIVE", None)
        return await message.reply("Ticket sudah ditutup.")

    user_id = state.get(ticket_id, "TICKET_USER")
    if not user_id:
        return

    if not (message.text or message.caption or message.media):
        return await message.reply("Tidak bisa mengirim pesan kosong.")

    try:
        await client.copy_message(
            chat_id=int(user_id),
            from_chat_id=message.chat.id,
            message_id=message.id
        )
        await message.reply("✅ Balasan terkirim & ticket ditutup.")
    except Exception as e:
        logger.error(f"REPLY ERROR: {e}")
        await message.reply("❌ Gagal mengirim balasan.")

    # 🔒 Auto Close Setelah Balas
    state.set(ticket_id, "TICKET_STATUS", "CLOSED")
    state.set(user_id, "ACTIVE_TICKET", None)
    state.set(admin_id, "REPLY_MODE", None)
    state.set(admin_id, "REPLY_ACTIVE", None)


# ===================================
# FORWARD PESAN UMUM KE LOG
# ===================================
async def forward_general(client, message):
    if message.text in no_commands:
        return

    user_id = message.from_user.id
    logs = await dB.get_var(client.me.id, "FORWARD_LOG")
    if not logs:
        logs = [OWNER_ID]
    elif not isinstance(logs, list):
        logs = [logs]

    try:
        for log_id in logs:
            forward = await client.forward_messages(
                chat_id=log_id,
                from_chat_id=message.chat.id,
                message_ids=message.id
            )
            state.set(forward.id, f"FORWARD_{forward.id}", user_id)
    except Exception as e:
        logger.error(f"GENERAL FORWARD ERROR: {e}")

"""
@CMD.NO_CMD("QUESTION", bot)
async def _(client, message):
    if message.text in no_commands:
        return
    user_id = message.from_user.id
    logs = await dB.get_var(client.me.id, "FORWARD_LOG")
    log = int(logs) if logs else OWNER_ID
    forward = await client.forward_messages(
        chat_id=log, from_chat_id=message.chat.id, message_ids=message.id
    )
    state.set(forward.id, f"FORWARD_{forward.id}", user_id)
"""