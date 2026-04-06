import asyncio
import os
from datetime import datetime
from io import BytesIO
import time
from pyrogram.errors import FloodWait, RPCError

from pyrogram import enums
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import (ChannelPrivate, FloodWait, PeerIdInvalid,
                             UsernameOccupied, UserNotParticipant)
from pyrogram.raw import functions

from Navy.helpers import CMD, Emoji, animate_proses, Tools

__MODULES__ = "ᴘʀᴏғɪʟᴇ"
__HELP__ = """<blockquote>Command Help **Profile** </blockquote>
<blockquote expandable>**Set delete username**
    **You can set new username to your account**
        `{0}setuname` (text/reply text)
    **You delete the username from your account**
        `{0}remuname`

**Set profile bio**
    **You can change bio from your account**
        `{0}setbio` (text/reply text)

**Set profile name**
    **You can set new name to your account**
        `{0}setname` (text/reply text)

**Set profile photo**
    **You can set new profile photo to your account**
        `{0}setpp` (reply media)

**Block unblock user**
    **You can block the user if you want**
        `{0}block` (username/reply user)
    **Unblock the user**
        `{0}unblock` (username/reply user)

**Set Your Online**
    **You can change online from your account**
        `{0}setonline on` or off

**You get profile photo user**
    **You can get profile photo user if you want**
        `{0}getpp` (username/reply user/id)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("setonline")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await message.reply(
            f"{emo.gagal}<b>Use the command like this:</b>\n<code>{x}setonline</code> on/off."
        )
    pros = await animate_proses(message, emo.proses)
    handle = message.text.split(None, 1)[1]
    try:
        if handle.lower() == "off":
            await client.invoke(functions.account.UpdateStatus(offline=False))
            return await pros.edit(
                f"{emo.sukses}<b>Successfully changed online status to: <code>{handle}</code></b>"
            )
        elif handle.lower() == "on":
            await client.invoke(functions.account.UpdateStatus(offline=True))
            return await pros.edit(
                f"{emo.sukses}<b>Successfully changed online status to: <code>{handle}</code></b>"
            )
        else:
            return await pros.edit(
                f"{emo.gagal}<b>Use the command like this:</b>\n<code>{x}setonline</code> on/off."
            )
    except Exception as e:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{e}</code>")


@CMD.UBOT("unblock")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    user_id = await client.extract_user(message)
    if not user_id:
        return await message.reply(
            f"{emo.gagal}<b>Provide username/user_id/reply to user's message.</b>"
        )
    pros = await animate_proses(message, emo.proses)
    try:
        user = await client.get_users(user_id)
    except PeerIdInvalid:
        return await pros.edit(
            f"{emo.gagal}<b>I have never interacted with <code>{user_id}</code></b>"
        )
    except Exception as e:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{str(e)}</code>")
    if user.id == client.me.id:
        return await pros.edit(f"{emo.sukses}<b>Ok!</b>")
    await client.unblock_user(user.id)
    return await pros.edit(f"{emo.sukses}<b>Successfully unblocked {user.mention}.</b>")


@CMD.UBOT("block")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    user_id = await client.extract_user(message)
    if not user_id:
        return await message.reply(
            f"{emo.gagal}<b>Provide username/user_id or reply to user's message.</b>"
        )
    pros = await animate_proses(message, emo.proses)
    try:
        user = await client.get_users(user_id)
    except PeerIdInvalid:
        return await pros.edit(
            f"{emo.gagal}<b>I have never interacted with <code>{user_id}</code></b>"
        )
    except Exception as e:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{str(e)}</code>")
    if user.id == client.me.id:
        return await pros.edit(f"{emo.sukses}<b>Ok!</b>")
    await client.block_user(user_id)
    return await pros.edit(f"{emo.sukses}<b>Successfully blocked {user.mention}.</b>")


@CMD.UBOT("setname")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await animate_proses(message, emo.proses)
    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await pros.edit(
            f"{emo.gagal}<b>Provide text or reply to a message to set as your name.</b>"
        )
    elif len(message.command) > 1:
        nama = message.text.split(None, 2)
        name = nama[1]
        namee = nama[2] if len(nama) > 2 else ""

        try:
            await client.update_profile(first_name=name)
            await client.update_profile(last_name=namee)
            return await pros.edit(
                f"{emo.sukses}<b>Successfully changed name to: <code>{name} {namee}</code></b>"
            )
        except Exception as e:
            return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{e}</code>")


@CMD.UBOT("setuname")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await message.reply(
            f"{emo.gagal}<b>Provide text or reply to a message to set as your username.</b>"
        )
    pros = await animate_proses(message, emo.proses)
    if rep:
        uname = rep.text or rep.caption
    elif len(message.command) > 1:
        nama = message.text.split(None, 1)
        uname = nama[1]
    else:
        return await pros.edit(
            f"{emo.gagal}<b>Provide text or reply to a message to set as your username.</b>"
        )

    try:
        await client.set_username(username=uname)
        return await pros.edit(
            f"{emo.sukses}<b>Successfully changed username to: <code>{uname}</code></b>"
        )
    except FloodWait as e:
        wait = int(e.value)
        await asyncio.sleep(wait)
        await client.set_username(username=uname)
        return await pros.edit(
            f"{emo.sukses}<b>Successfully changed username to: <code>{uname}</code></b>"
        )
    except UsernameOccupied:
        return await pros.edit(
            f"{emo.gagal}<b><code>{uname}</code> is already taken by another user.</b>"
        )
    except Exception as e:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{e}</code>")


@CMD.UBOT("remuname")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await animate_proses(message, emo.proses)

    try:
        await client.set_username(username="")
        return await pros.edit(f"{emo.sukses}<b>Username successfully removed.</b>")
    except Exception as e:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{e}</code>")


@CMD.UBOT("setbio")
@CMD.FAKEDEV("setbio")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await animate_proses(message, emo.proses)
    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await pros.edit(f"{emo.gagal}<b>Provide text or reply to a message.</b>")
    if rep:
        bio = rep.text or rep.caption
    elif len(message.command) > 1:
        bio = message.text.split(None, 1)[1]
    try:
        await client.update_profile(bio=bio)
        return await pros.edit(
            f"{emo.sukses}<b>Successfully changed bio to: <code>{bio}</b>"
        )
    except Exception as e:
        return await pros.edit(f"{emo.gagal}<b>Error:</b> <code>{e}</code>")


@CMD.UBOT("setpp")
@CMD.FAKEDEV("setpp")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    po = "storage/TM_BLACK.png"
    replied = message.reply_to_message
    pros = await animate_proses(message, emo.proses
    )
    if (
        replied
        and replied.media
        and (
            replied.photo
            or (replied.document and "image" in replied.document.mime_type)
        )
    ):
        prop = await client.download_media(message=replied, file_name=po)
        await client.set_profile_photo(photo=prop)
        await client.send_photo(
            message.chat.id,
            prop,
            caption=f"{emo.sukses}<b>Successfully changed your profile picture.</b>",
        )
        if os.path.exists(prop):
            os.remove(prop)
        return await pros.delete()
    else:
        return await pros.edit(
            f"{emo.gagal}<b>Reply to a photo/image, or a document that is a photo/image to set as your profile picture.</b>"
        )


@CMD.UBOT("getpp")
@CMD.FAKEDEV("getpp")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    pros = await animate_proses(message, emo.proses)

    try:
        chat = None
        args = message.text.split(maxsplit=1)

        # 1) Reply (user / channel / anonymous)
        if message.reply_to_message:
            if message.reply_to_message.from_user:
                chat = await client.get_chat(message.reply_to_message.from_user.id)
            elif message.reply_to_message.sender_chat:
                chat = await client.get_chat(message.reply_to_message.sender_chat.id)

        # 2) Username / ID / Link
        elif len(args) > 1:
            target = args[1].strip()
            try:
                chat = await client.get_chat(target)
            except Exception:
                return await pros.edit(
                    f"{emo.gagal}<b>Target tidak ditemukan.</b>"
                )

        # 3) Default: diri sendiri
        else:
            chat = await client.get_chat("me")

        chat_id = chat.id
        title = chat.first_name or chat.title or "Unknown"

        # Ambil foto profil
        photos = []
        async for p in client.get_chat_photos(chat_id, limit=1):
            photos.append(p)

        if not photos:
            return await pros.edit(
                f"{emo.gagal}<b>{title} tidak memiliki foto profil.</b>"
            )

        media = photos[0]

        # Deteksi tipe media
        if getattr(media, "video", None):
            ext = ".mp4"
            send_type = "video"
        elif getattr(media, "animation", None):
            ext = ".gif"
            send_type = "animation"
        else:
            ext = ".jpg"
            send_type = "photo"

        file_path = f"storage/getpp_{chat_id}_{int(time.time())}{ext}"
        file = await client.download_media(media.file_id, file_name=file_path)

        caption = f"{emo.sukses}<b>Profile picture dari {title}.</b>"

        if send_type == "video":
            await client.send_video(message.chat.id, file, caption=caption)
        elif send_type == "animation":
            await client.send_animation(message.chat.id, file, caption=caption)
        else:
            await client.send_photo(message.chat.id, file, caption=caption)

        if os.path.exists(file):
            os.remove(file)

        return await pros.delete()

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await pros.edit(
            f"{emo.gagal}<b>FloodWait: coba lagi dalam {e.value} detik.</b>"
        )

    except RPCError as e:
        return await pros.edit(f"{emo.gagal}<b>Error: {e}</b>")