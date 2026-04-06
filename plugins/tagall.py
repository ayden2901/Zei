import asyncio
from Navy import *
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses
from .admins import admin_check



# Menyimpan task aktif berdasarkan chat_id
_active_task_ids = {}

# TAGALL
@CMD.UBOT("tagall")
@CMD.DEV_CMD("tagall")
@CMD.FAKEDEV("tagall")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await animate_proses(message, em.proses) 

    if not proses:
        return

    botol = await admin_check(message, client.me.id)
    if not botol:
        return await proses.edit(f"{em.gagal}**You are not an admin in this group!**")

    replied = message.reply_to_message
    prefix = client.get_prefix(client.me.id)
    if len(message.command) < 2 and not replied:
        return await proses.edit(f"{em.gagal}**Please reply to text or give text!**")

    chat_id = message.chat.id
    task_id = task.start_task()
    _active_task_ids[chat_id] = task_id

    await proses.edit(
        f"{em.proses}<i>Proses mention berjalan. Ketik <code>{prefix[0]}stoptag</code> untuk membatalkan.</i>"
    )

    async def tag_members():
        try:
            usernum = 0
            usertxt = ""
            ids = f"{em.pin}ᴄʀᴇᴀᴛᴇᴅ ʙʏ : @StarBotDevs"
            text = replied.text if replied else message.text.split(maxsplit=1)[1]

            async for m in client.get_chat_members(chat_id):
                if m.user.is_bot or m.user.is_deleted:
                    continue
                if not task.is_active(task_id):
                    return await proses.edit(f"{em.gagal}**Proses dibatalkan.**")

                usernum += 1
                usertxt += f"{em.ket} [{m.user.first_name}](tg://user?id={m.user.id})\n"

                if usernum == 4:
                    content = f"<blockquote>{text}</blockquote>\n<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>"
                    if replied:
                        await replied.reply_text(f"<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>")
                    else:
                        await client.send_message(chat_id, content)
                    await asyncio.sleep(5)
                    usernum = 0
                    usertxt = ""

            if usernum > 0:
                content = f"<blockquote>{text}</blockquote>\n<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>"
                if replied:
                    await replied.reply_text(f"<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>")
                else:
                    await client.send_message(chat_id, content)

        except FloodWait as e:
            await asyncio.sleep(e.value)
        finally:
            task.end_task(task_id)
            _active_task_ids.pop(chat_id, None)

    try:
        await asyncio.wait_for(tag_members(), timeout=3600)
    except asyncio.TimeoutError:
        task.end_task(task_id)
        _active_task_ids.pop(chat_id, None)
        await proses.edit(f"{em.gagal}**Proses mention timeout setelah 30 menit!**")
        return

    return await proses.delete()


# @ADMINS
@CMD.UBOT_REGEX(r"^(@admins)")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await animate_proses(message, em.proses) 

    if not proses:
        return

    chat_id = message.chat.id
    task_id = task.start_task()
    _active_task_ids[message.chat.id] = task_id
    replied = message.reply_to_message
    prefix = client.get_prefix(client.me.id)

    if not replied and len(message.text.split()) == 1:
        return await proses.edit(f"{em.gagal}**Please reply to text or give text!**")

    await proses.edit(
        f"{em.proses}<i>Memanggil admin... Ketik <code>{prefix[0]}stoptag</code> untuk membatalkan.</i>"
    )

    async def mention_admins():
        try:
            usernum = 0
            ids = f"{em.pin}ᴄʀᴇᴀᴛᴇᴅ ʙʏ : @StarBotDevs"
            usertxt = ""
            text = replied.text if replied else message.text.split(maxsplit=1)[1]
            async for m in client.get_chat_members(
                message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
            ):
                if not task.is_active(task_id):
                    return await proses.edit(f"{em.gagal}**Proses dibatalkan.**")
                if m.user.is_deleted or m.user.is_bot:
                    continue
                usernum += 1
                usertxt += f"{em.ket} [{m.user.first_name}](tg://user?id={m.user.id})\n"
                if usernum == 5:
                    content = f"<blockquote>{text}</blockquote>\n<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>"
                    if replied:
                        await replied.reply_text(f"<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>")
                    else:
                        await client.send_message(chat_id, content)
                    await asyncio.sleep(2)
                    usernum = 0
                    usertxt = ""
            if usernum > 0:
                content = f"<blockquote>{text}</blockquote>\n<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>"
                if replied:
                    await replied.reply_text(f"<blockquote>{usertxt}</blockquote><blockquote>{ids}</blockquote>")
                else:
                    await client.send_message(chat_id, content)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        finally:
            task.end_task(task_id)
            _active_task_ids.pop(chat_id, None)

    await mention_admins()
    return await proses.delete()


# CANCEL
@CMD.UBOT("stoptag")
@CMD.DEV_CMD("stoptag")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    chat_id = message.chat.id
    if chat_id not in _active_task_ids:
        return await message.reply(f"{em.gagal}Tidak ada proses tag yang sedang berjalan di chat ini.")

    task_id = _active_task_ids[chat_id]
    task.end_task(task_id)
    del _active_task_ids[chat_id]

    return await message.reply(f"{em.sukses}Proses tag `#{task_id}` telah dibatalkan.")

__MODULES__ = "ᴛᴀɢᴀʟʟ"
__HELP__ = """<blockquote>Command Help **Tagall**</blockquote>

<blockquote>**Mention members**</blockquote>
    **Tag member from chat**
        `{0}tagall` (text/reply text)

<blockquote>**Mention admins**</blockquote>
    **Tag only admins from chat**
        `@admins` (text/reply text)

<blockquote>**Stop mention**</blockquote>
    **Stop task tag**
        `{0}stoptag`

<b>   {1}</b>
"""
