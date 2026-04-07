import asyncio
import os
import random
import re
import json
import traceback
import html
from datetime import datetime
from io import BytesIO
from time import time
from pyrogram.errors import MessageIdInvalid, ChatSendStickersForbidden
from pyrogram import enums, raw
from pyrogram.enums import ChatType, ParseMode
from pyrogram.raw.functions import Ping

from Navy import dB
from Navy.helpers import (CMD, Emoji, Tools, get_time, start_time, Basic_Effect, Premium_Effect, animate_proses)

__MODULES__ = "sᴇᴛᴛɪɴɢs"
__HELP__ = """<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **sᴇᴛᴛɪɴɢs**</u>

<blockquote><b>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ sᴇᴛᴛɪɴɢs</b>
     ➢ `{0}set_text ping` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
     ➢ `{0}set_text uptime` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
     ➢ `{0}set_text owner` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
     ➢ `{0}set_text ubot` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
     ➢ `{0}set_text proses` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
     ➢ `{0}set_text help` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
     ➢ `{0}set_text sukses` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]</blockquote>
<blockquote>ɴᴏᴛᴇ : ᴜsᴇ ᴘɪɴɢ ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄʜᴀɴɢᴇs ᴀɴᴅ ʜᴇʟᴘ</blockquote>

<b>   {1}</b>
"""


async def set_pong_message(user_id, new_message):
    await dB.set_var(user_id, "text_ping", new_message)
    return


async def set_utime_message(user_id, new_message):
    await dB.set_var(user_id, "text_uptime", new_message)
    return


async def set_owner_message(user_id, new_message):
    await dB.set_var(user_id, "text_owner", new_message)
    return


async def set_ubot_message(user_id, new_message):
    await dB.set_var(user_id, "text_ubot", new_message)
    return


async def set_gcast_message(user_id, new_message):
    await dB.set_var(user_id, "text_gcast", new_message)
    return


async def set_sukses_message(user_id, new_message):
    await dB.set_var(user_id, "text_sukses", new_message)
    return


async def set_help_message(user_id, new_message):
    await dB.set_var(user_id, "text_help", new_message)
    return


costumtext_query = {
    "ping": set_pong_message,
    "uptime": set_utime_message,
    "owner": set_owner_message,
    "ubot": set_ubot_message,
    "proses": set_gcast_message,
    "sukses": set_sukses_message,
    "help": set_help_message,
}


@CMD.UBOT("set_text")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses}**{proses_}**")

    args = message.text.split(maxsplit=2)
    variable = args[1]
    # if len(args) >= 3:
    new_message = client.new_arg(message)
    if variable in costumtext_query:
        await costumtext_query[variable](client.me.id, new_message)
        return await pros.edit(
            f"{em.sukses}**Successfully updated custom text: <u>{variable}</u>**"
        )
    else:
        return await pros.edit(
            f"{em.gagal}**Please given text for this query: {variable}!**"
        )
    # else:
    # return await pros.edit(
    #    f"{em.gagal}**No query: <code>{variable}</code>. Please provide the correct query!**"
    # )


MAX_FILE_SIZE = 1_500_000

@CMD.UBOT("setsping")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    args = message.command
    reply = message.reply_to_message


    if len(args) > 1 and args[1].lower() == "none":
        try:
            await dB.remove_var(client.me.id, "ping_sticker")
            await dB.remove_var(client.me.id, "ping_media")
            return await message.reply_text(
                f"{em.sukses}**Ping stiker/media dinonaktifkan (mode teks).**"
            )
        except Exception as e:
            return await message.reply_text(f"{em.gagal}**Error: {str(e)}**")

    if not reply:
        return await message.reply_text(f"{em.gagal}**Reply ke stiker atau media!**")

    if reply.sticker:
        try:
            await dB.set_var(
                client.me.id,
                "ping_sticker",
                reply.sticker.file_id
            )
            return await message.reply_text(f"{em.sukses}**Berhasil set ping stiker!**")
        except Exception as e:
            return await message.reply_text(f"{em.gagal}**Error: {str(e)}**")

    media_mapping = {
        "photo": Tools.Types.PHOTO,
        "video": Tools.Types.VIDEO,
        "animation": Tools.Types.ANIMATION,
        "document": Tools.Types.DOCUMENT,
        "audio": Tools.Types.AUDIO,
        "voice": Tools.Types.VOICE,
        "video_note": Tools.Types.VIDEO_NOTE,
    }

    for key, val in media_mapping.items():
        media_attr = getattr(reply, key, None)
        if media_attr:
            size = getattr(media_attr, "file_size", None)
            if size and size > MAX_FILE_SIZE:
                return await message.reply_text(
                    f"{em.gagal}**File terlalu besar! Maksimal {Tools.humanbytes(MAX_FILE_SIZE)}.**"
                )
            try:

                data = {
                    "chat_id": reply.chat.id,
                    "message_id": reply.id
                }
                await dB.set_var(
                    client.me.id,
                    "ping_media",
                    json.dumps(data)
                )
                return await message.reply_text(
                    f"{em.sukses}**Berhasil set ping media: {key}!**"
                )
            except Exception as e:
                return await message.reply_text(f"{em.gagal}**Error: {str(e)}**")

    return await message.reply_text(f"{em.gagal}**Tipe media ini tidak didukung!**")


@CMD.UBOT("ping|p")
@CMD.DEV_CMD("ping")
@CMD.FAKEDEV("ping")
async def ping_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    sticker = await dB.get_var(client.me.id, "ping_sticker")
    media = await dB.get_var(client.me.id, "ping_media")

    pros = await animate_proses(message, em.proses)
    if not pros:
        return

    start = datetime.now()
    try:
        await client.invoke(Ping(ping_id=0))
    except:
        pass
    end = datetime.now()

    duration = round((end - start).microseconds / 100000, 2)
    upnya = await get_time(time() - start_time)

    ping_text = (
        f"<blockquote expandable>"
        f"<b>╭───⊳zei ubot⊲────</b>\n"
        f"<b>├{em.ping}{pong_} :</b> {duration}ms\n"
        f"<b>├{em.uptime}{uptime_} :</b> {upnya}\n"
        f"<b>├{em.owner}{owner_}</b>\n"
        f"<b>├{em.robot}ᴜsᴇʀʙᴏᴛ :</b> {ubot_}\n"
        f"<b>╰────⊳<a href='tg://user?id=5819562467'>sᴜᴘᴘᴏʀᴛ</a>⊲────</b>\n"
        f"</blockquote>"
    )

    effect_id = random.choice(
        Premium_Effect if message._client.me.is_premium else Basic_Effect
    )

    # 🔹 Sticker
    try:
        if sticker:
            st = await message.reply_sticker(sticker)
            await asyncio.sleep(2)
            await st.delete()
    except Exception as e:
        print("ERROR STICKER:", e)

    # 🔹 Ambil media
    async def get_media():
        try:
            data = media
            if isinstance(data, str):
                data = json.loads(data)

            if not isinstance(data, dict):
                return None

            chat_id = data.get("chat_id")
            msg_id = data.get("message_id")

            if not chat_id or not msg_id:
                return None

            return await client.get_messages(chat_id, msg_id)

        except Exception as e:
            print("ERROR GET MEDIA:", e)
            return None

    # 🔹 Kirim media
    async def send_media(msg, use_effect):
        try:
            kwargs = {
                "caption": ping_text,
                "parse_mode": ParseMode.HTML
            }

            if use_effect:
                kwargs["effect_id"] = effect_id

            if msg.photo:
                await client.send_photo(message.chat.id, msg.photo.file_id, **kwargs)

            elif msg.video:
                await client.send_video(message.chat.id, msg.video.file_id, **kwargs)

            elif msg.animation:
                await client.send_animation(message.chat.id, msg.animation.file_id, **kwargs)

            elif msg.document:
                await client.send_document(message.chat.id, msg.document.file_id, **kwargs)

            elif msg.audio:
                await client.send_audio(message.chat.id, msg.audio.file_id, **kwargs)

            elif msg.voice:
                await client.send_voice(message.chat.id, msg.voice.file_id, **kwargs)

            elif msg.video_note:
                await client.send_video_note(message.chat.id, msg.video_note.file_id)

            else:
                return False

            return True

        except Exception as e:
            print("ERROR SEND MEDIA:", e)
            return False

    # 🔥 EXECUTION
    msg = await get_media()

    if msg:
        ok = await send_media(msg, True)
        if ok:
            try:
                await pros.delete()
            except:
                pass
            return

        ok = await send_media(msg, False)
        if ok:
            try:
                await pros.delete()
            except:
                pass
            return

    # 🔥 FALLBACK (AMAN)
    try:
        return await pros.edit(
            ping_text,
            parse_mode=ParseMode.HTML
        )
    except:
        return await message.reply_text(
            ping_text,
            parse_mode=ParseMode.HTML
        )

"""
@CMD.UBOT("setsping")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    # 👉 tambahin ini
    if len(message.command) > 1 and message.command[1].lower() == "none":
        try:
            await dB.remove_var(client.me.id, "ping_sticker")
            return await message.reply_text(
                f"{em.sukses}**Ping sticker dinonaktifkan (mode teks).**"
            )
        except Exception as e:
            return await message.reply_text(
                f"{em.gagal}**error{str(e)}**"
            )

    # 👉 kode lama kamu (TIDAK diubah)
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text(f"{em.gagal}**Reply to sticker!**")

    try:
        await dB.set_var(client.me.id, "ping_sticker", reply.sticker.file_id)
        return await message.reply_text(f"{em.sukses}**Successfully set vars ping stickers!**")
    except Exception as e:
        return await message.reply_text(f"{em.gagal}**error{str(e)}**")

@CMD.UBOT("ping|p")
@CMD.DEV_CMD("ping")
@CMD.FAKEDEV("ping")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    data = await dB.get_var(client.me.id, "ping_sticker") or \
        "CAACAgUAAxkBAAIcC2h4wCjEnAySn5TzrIMF7ENOMmACAAL9DAADXDhU2U5g24fxElceBA"

    # ================= STICKER (OPSIONAL) =================
    sticker = None
    try:
        sticker = await message.reply_sticker(data)
    except ChatSendStickersForbidden:
        pass  # ⬅️ skip total, tidak buat pesan apa pun

    # ================= ANIMASI PROSES =================
    pros = await animate_proses(message, em.proses)
    if not pros:
        if sticker:
            await sticker.delete()
        return

    # ================= HITUNG PING =================
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    end = datetime.now()
    duration = round((end - start).microseconds / 100000, 2)

    upnya = await get_time(time() - start_time)

    _ping = (
        f"<blockquote expandable>"
        f"<b>╭───⊳zei ubot⊲────</b>\n"
        f"<b>├{em.ping}{pong_} :</b> {duration}ms\n"
        f"<b>├{em.uptime}{uptime_} :</b> {upnya}\n"
        f"<b>├{em.owner}{owner_}</b>\n"
        f"<b>├{em.robot}ᴜsᴇʀʙᴏᴛ :</b> {ubot_}\n"
        f"<b>╰────⊳<a href='tg://user?id=347422710'>sᴜᴘᴘᴏʀᴛ</a>⊲────</b>\n"
        f"</blockquote>"
    )

    await asyncio.sleep(2)

    # ================= CLEANUP =================
    if sticker:
        await sticker.delete()

    return await pros.edit(_ping, parse_mode=ParseMode.HTML)
"""