from Navy.helpers import CMD
from Navy.database import dB
from Navy import bot
from html import escape
from .antigcast import is_user_admin
from pyrogram import filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ParseMode
import asyncio
import json

__MODULES__ = "sᴀɴɢᴍᴀᴛᴀ ʙᴏᴛ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>sᴀɴɢᴍᴀᴛᴀ ʙᴏᴛ</b></u>

<blockquote>
❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>sᴀɴɢᴍᴀᴛᴀ</b>

➢ `{0}sangmata` on/off
➢ `{0}sg` @user / reply
</blockquote>

<b>{1}</b>
"""


USER_CACHE = {}

async def import_from_sangmata(bot, user_id):

    sg_bot = "@SangMata_BOT"

    try:
        msg = await bot.send_message(sg_bot, user_id)

        await asyncio.sleep(2)

        names = []
        usernames = []

        async for m in bot.get_chat_history(sg_bot, limit=5):

            if not m.text:
                continue

            for line in m.text.split("\n"):

                if line.startswith("•"):
                    value = line.replace("•", "").strip()

                    if value.startswith("@"):
                        usernames.append(value)
                    else:
                        names.append(value)

        if names:
            await dB.set_var(
                user_id,
                f"USER_SG_HISTORY_name_{user_id}",
                json.dumps(names)
            )

        if usernames:
            await dB.set_var(
                user_id,
                f"USER_SG_HISTORY_username_{user_id}",
                json.dumps(usernames)
            )

        await msg.delete()

    except:
        pass

@CMD.BOT("sangmata")
async def sangmata_handler(bot, message):

    chat_id = message.chat.id
    args = message.text.split()

    bot_is_admin = await is_user_admin(bot, chat_id, bot.me.id)

    if not bot_is_admin:
        reply = await message.reply(
            "<b>⚠️ Berikan Bot Akses Admin Untuk Group Ini!</b>",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        return await reply.delete()

    if not message.from_user:
        return

    is_admin = await is_user_admin(bot, chat_id, message.from_user.id)

    if not is_admin:
        reply = await message.reply(
            "<b>⚠️ Kamu Bukan Admin Group Ini.</b>",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        return await reply.delete()

    if len(args) < 2:
        reply = await message.reply(
            "<b>Gunakan :</b> /sangmata on atau /sangmata off",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        return await reply.delete()

    action = args[1].lower()

    if action not in ("on", "off"):
        reply = await message.reply(
            "<b>Command Valid:</b> on / off",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        return await reply.delete()

    current_status = await dB.get_var(chat_id, "STATUS_SG") or "OFF"

    if action == "on":

        if current_status == "ON":
            reply = await message.reply(
                "<b>⚠️ SangMata sudah aktif di group ini.</b>",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(2)
            return await reply.delete()

        await dB.set_var(chat_id, "STATUS_SG", "ON")

        reply = await message.reply(
            "<b>✅ SangMata berhasil diaktifkan.</b>",
            parse_mode=ParseMode.HTML
        )

    else:

        if current_status == "OFF":
            reply = await message.reply(
                "<b>⚠️ SangMata belum aktif di group ini.</b>",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(2)
            return await reply.delete()

        await dB.set_var(chat_id, "STATUS_SG", "OFF")

        reply = await message.reply(
            "<b>❌ SangMata berhasil dimatikan.</b>",
            parse_mode=ParseMode.HTML
        )

    await asyncio.sleep(2)
    await reply.delete()


async def append_history(user_id, field, value):

    if not value:
        return

    key = f"USER_SG_HISTORY_{field}_{user_id}"

    old_data = await dB.get_var(user_id, key) or "[]"

    try:
        history = json.loads(old_data)
    except:
        history = []

    if value not in history:
        history.append(value)

    history = history[-50:]

    await dB.set_var(user_id, key, json.dumps(history))

async def check_user_update(chat_id, user, message=None):

    if not user or user.is_bot:
        return

    status = await dB.get_var(chat_id, "STATUS_SG") or "OFF"

    if status != "ON":
        return

    name = f"{user.first_name} {user.last_name or ''}".strip() or None
    username = f"@{user.username}" if user.username else None

    # CACHE CHECK
    cache_key = str(user.id)
    current_data = f"{name}{username}"

    if USER_CACHE.get(cache_key) == current_data:
        return

    USER_CACHE[cache_key] = current_data

    key_name = f"USER_SG_NAME_{user.id}"
    key_username = f"USER_SG_USERNAME_{user.id}"

    old_name = await dB.get_var(user.id, key_name)
    old_username = await dB.get_var(user.id, key_username)

    if old_name == name and old_username == username:
        return

    if old_name is None:
        await dB.set_var(user.id, key_name, name)

    if old_username is None:
        await dB.set_var(user.id, key_username, username)

    mention = f'<a href="tg://user?id={user.id}">{escape(name or "User")}</a>'

    text_parts = [
        f"👀 {bot.me.mention} <b>SangMata Bot</b>\n"
        f"<b>👤 Pengguna :</b> {mention} [{user.id}]"
    ]

    if old_name != name:

        text_parts.append(
            f"<b>♻️ Mengubah Nama</b>\n"
            f"<b>🔄 Dari :</b> <code>{old_name or 'None'}</code>\n"
            f"<b>🆕 Menjadi :</b> <code>{name or 'None'}</code>"
        )

        await dB.set_var(user.id, key_name, name)
        await append_history(user.id, "name", name)

    if old_username != username:

        text_parts.append(
            f"<b>♻️ Mengubah Username</b>\n"
            f"<b>🔄 Dari :</b> {old_username or 'None'}\n"
            f"<b>🆕 Menjadi :</b> {username or 'None'}"
        )

        await dB.set_var(user.id, key_username, username)
        await append_history(user.id, "username", username)

    text = "\n".join(text_parts)

    try:

        if message:
            msg = await message.reply_text(text, parse_mode=ParseMode.HTML)
        else:
            msg = await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

        await asyncio.sleep(90)
        await msg.delete()

    except:
        pass


@CMD.BOT("sg")
async def sg_history(bot, message):

    args = message.text.split()

    if message.reply_to_message:
        user = message.reply_to_message.from_user

    elif len(args) > 1:

        try:
            user = await bot.get_users(args[1])
        except:
            return await message.reply(
                "<b>❌ User tidak ditemukan.</b>",
                parse_mode=ParseMode.HTML
            )

    else:
        return await message.reply(
            "<b>Gunakan :</b> /sg @user atau reply pesan",
            parse_mode=ParseMode.HTML
        )

    user_id = user.id
    name = f"{user.first_name} {user.last_name or ''}".strip()

    mention = f'<a href="tg://user?id={user_id}">{escape(name)}</a>'

    name_key = f"USER_SG_HISTORY_name_{user_id}"
    username_key = f"USER_SG_HISTORY_username_{user_id}"

    name_history = await dB.get_var(user_id, name_key) or "[]"
    username_history = await dB.get_var(user_id, username_key) or "[]"

    try:
        name_history = json.loads(name_history)
    except:
        name_history = []

    try:
        username_history = json.loads(username_history)
    except:
        username_history = []

    # AUTO IMPORT JIKA DATABASE KOSONG
    if not name_history and not username_history:

        await import_from_sangmata(bot, user_id)

        name_history = await dB.get_var(user_id, name_key) or "[]"
        username_history = await dB.get_var(user_id, username_key) or "[]"

        try:
            name_history = json.loads(name_history)
        except:
            name_history = []

        try:
            username_history = json.loads(username_history)
        except:
            username_history = []

    text = [
        f"👀 <b>SangMata History</b>",
        f"<b>👤 User :</b> {mention}",
        f"<b>🆔 ID :</b> <code>{user_id}</code>"
    ]

    if name_history:
        text.append("\n<b>📛 History Nama :</b>")
        for n in reversed(name_history[-10:]):
            text.append(f"• <code>{escape(n)}</code>")
    else:
        text.append("\n<b>📛 History Nama :</b> Tidak ada")

    if username_history:
        text.append("\n<b>🔗 History Username :</b>")
        for u in reversed(username_history[-10:]):
            text.append(f"• {u}")
    else:
        text.append("\n<b>🔗 History Username :</b> Tidak ada")

    await message.reply(
        "\n".join(text),
        parse_mode=ParseMode.HTML
    )

@bot.on_message(filters.group & filters.incoming & ~filters.service)
async def sangmata_message_trigger(client, message):

    if message.from_user:
        await check_user_update(
            message.chat.id,
            message.from_user,
            message
        )

@bot.on_chat_member_updated(filters.group)
async def sangmata_member_update(client, chat_member_update: ChatMemberUpdated):

    await check_user_update(
        chat_member_update.chat.id,
        chat_member_update.new_chat_member.user
    )