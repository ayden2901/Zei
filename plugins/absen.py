import os
from datetime import datetime
import aiocron
import traceback
import html
import pytz
from pyrogram import filters, Client, types
from pyrogram.types import Message 
from pyrogram.enums import ParseMode, ChatMemberStatus
from Navy import bot, navy
from Navy.helpers import CMD,Emoji, animate_proses, Tools
from Navy.logger import logger
from pyrogram.utils import unpack_inline_message_id
from assistant.inline import inline_absen
from assistant.callback import absen_callback
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InlineQueryResultAnimation,
                            InlineQueryResultArticle,
                            InlineQueryResultCachedAnimation,
                            InlineQueryResultCachedAudio,
                            InlineQueryResultCachedDocument,
                            InlineQueryResultCachedPhoto,
                            InlineQueryResultCachedSticker,
                            InlineQueryResultCachedVideo,
                            InlineQueryResultCachedVoice,
                            InlineQueryResultPhoto, InlineQueryResultVideo,
                            InputTextMessageContent, InlineQuery, CallbackQuery)
from bot.cache import (
    absen_data,
    inline_mapping,
    inline_msg_cache,
    active_absen_inline_ids,
    active_absen_messages,
    absen_owners
)
from bot.cache import (
    save_inline_mapping_file,
    load_inline_mapping_file,
    get_today,
    get_absen_file_by_inline,
    load_absen_file,
    save_absen_file,
    save_inline_mapping,
    get_inline_mapping,
    save_inline_meta_file,
    load_inline_meta_file
)


__MODULES__ = "ᴀʙsᴇɴ"
__HELP__ = """<blockquote expandable><u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **ᴀʙsᴇɴ**</u>
lagi gua edit isinya!!!</blockquote>
"""


@CMD.BOT("absen")
async def absen_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"[DEBUG] Handler aktif dari: {chat_id} oleh: {user_id}")

    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("🚫 Hanya admin yang menggunakan perintah. Anda bukan Bagian admin grup.")

        user = message.from_user
        absen_key = f"{chat_id}_{message.id}"
        absen_owners[absen_key] = user.id  # ✅ Letakkan di sini setelah user terdefinisi

        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        hari = now.strftime("%A")
        tanggal = now.strftime("%d-%m-%Y")

        fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        mention = f'<a href="tg://user?id={user.id}">{fullname}</a>'

        teks = (
            f"<blockquote>"
            f"📋 <b><u>DAFTAR ABSENSI HARIAN</u></b>\n\n"
            f"Hari : {hari}\n"
            f"Tanggal : {tanggal}\n\n"
            f"Di Absensi oleh : {mention}"
            f"</blockquote>\n"
            f"<b>Belum Ada Yang Absen Hari Ini</b>"
        )

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Absen Sekarang", callback_data="absen_tap")],
            [InlineKeyboardButton("❌ Tutup", callback_data="absen_close")]
        ])

        await message.reply(teks, reply_markup=markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        import logging
        logging.exception("Gagal menjalankan perintah /absen")
        await message.reply("⚠️ Terjadi kesalahan saat menjalankan perintah.")

@CMD.BOT("getabsen")
@CMD.UBOT("getabsen")
async def get_absen_result(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply ke pesan absen!")

    teks = message.reply_to_message.text
    if not teks or "DAFTAR ABSENSI HARIAN" not in teks:
        return await message.reply("❌ Bukan pesan absen.")

    filename = f"data/absensi/absen_{message.chat.id}_{get_today()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(teks)

    await message.reply_document(filename, caption="📂 Absen disimpan.")

@CMD.BOT("absen_close")
@CMD.UBOT("close")
async def close_absen_handler(client, message):
    if not message.reply_to_message:
        return await message.edit("❌ Harus membalas pesan daftar absen!")

    reply_msg = message.reply_to_message

    # Cek apakah ada tombol "absen_close"
    if not reply_msg.reply_markup:
        return await message.edit("❌ Tidak ada tombol untuk ditutup!")

    # Cari callback_data "absen_close"
    found = False
    for row in reply_msg.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == "absen_close":
                found = True
                break

    if not found:
        return await message.edit("❌ Tidak ditemukan tombol `Tutup Absen`!")

    try:
        # Tekan tombol callback "absen_close"
        await client.request_callback_answer(
            chat_id=message.chat.id,
            message_id=reply_msg.id,
            callback_data="absen_close"
        )
        await message.edit("✅ Absen berhasil ditutup.")
    except Exception as e:
        await message.edit(f"❌ Gagal menutup absen:\n{e}")


@CMD.UBOT("absen")
async def absen_inline(client, message):
    query = "absen"
    try:
        results = await client.get_inline_bot_results("StarXCodeBot", query)
        await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id
        )

        # ✅ Simpan inline_message_id aktif (gunakan cache global)
        from bot.cache import active_absen_inline_ids
        active_absen_inline_ids[message.chat.id] = results.results[0].id

        await message.delete()
    except Exception as e:
        await message.reply(f"Gagal: {e}")