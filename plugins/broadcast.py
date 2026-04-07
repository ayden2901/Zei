import asyncio
import os
import html
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import (ChannelPrivate,
                             ChatWriteForbidden, FloodWait, Forbidden,
                             PeerIdInvalid, SlowmodeWait, UserBannedInChannel,
                             MessageIdInvalid)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BLACKLIST_GCAST, DEVS, OWNER_ID, FAKE_DEVS
from Navy import bot
from assistant import callback, inline
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses



__MODULES__ = "ʙʀᴏᴀᴅᴄᴀsᴛ"
__HELP__ = """<blockquote expandable><u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **ʙʀᴏᴀᴅᴄᴀsᴛ**</u>

❖ <b>ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ **ʙʀᴏᴀᴅᴄᴀsᴛ**</b>
    ➢ `{0}bc` [ǫᴜᴇʀʏ] [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
    ➢ `{0}ɢᴄᴀsᴛ` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
    ➢ `{0}ucast` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
    ➢ `{0}send` [ᴛᴇxᴛ/ʀᴇᴘʟʏ ᴛᴇxᴛ]
    ➢ `{0}cancel` [ᴛᴀsᴋɪᴅ]
    ➢ `{0}addbl` [ᴄʜᴀᴛɪᴅ]
    ➢ `{0}delbl` [ᴄʜᴀᴛɪᴅ]
    ➢ `{0}add-bcdb` [ᴄʜᴀᴛɪᴅ]
    ➢ `{0}del-bcdb` [ᴄʜᴀᴛɪᴅ]
❖ <b>ʟɪʜᴀᴛ ᴅᴀғᴛᴀʀ **ʙʟᴀᴄᴋʟɪsᴛ**</b>
    ➢ `{0}listbl`
    ➢ `{0}list-bcdb`
<b>❖ **ʟɪsᴛ ǫᴜᴇʀʏ**</b>
    ➢ `db` : ᴜsᴇʀ
    ➢ `private` : ɢʀᴏᴜᴘ ᴘʀɪᴠᴀᴛᴇ
    ➢ `group` : ɢʀᴏᴜᴘ
    ➢ `all` : sᴇᴍᴜᴀɴʏᴀ</blockquote>

<b>    {1}</b>
"""

GCAST_OWNERS = {}

@CMD.UBOT("bc")
@CMD.DEV_CMD("bc")
@CMD.FAKEDEV("bc")
async def bc_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    async def safe_edit(msg_obj, text, **kwargs):
        try:
            return await msg_obj.edit(text, **kwargs)
        except MessageIdInvalid:
            return await message.reply(text, **kwargs)
    proses = await animate_proses(message, em.proses) 

    if not proses:
        return

    command, text = client.extract_type_and_msg(message)

    if command not in ["group", "private", "all", "db"] or not text:
        return await safe_edit(
            f"{em.gagal}<code>{message.text.split()[0]}</code> <b>[group, private, all atau db]</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    await safe_edit(
        proses,
        f"""<blockquote expandable>╭{em.proses}<b>{message.command[0]} {proses_}</b>
├{em.sukses}<b>sᴜᴄᴄᴇss :</b> <code>0 ɢʀᴏᴜᴘs</code>
├{em.gagal}<b>ғᴀɪʟᴇᴅ :</b> <code>0 ɢʀᴏᴜᴘs</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>""", parse_mode=ParseMode.HTML
    )
    chats = await client.get_chat_id(command)
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"{em.gagal}**Error failed broadcast:**\n"
    try:
        if command == "db":
            return await broadcast_db(
                client,
                message,
                em,
                prefix,
                done,
                failed,
                blacklist,
                task,
                task_id,
                proses,
            )
        for index, chat_id in enumerate(chats, 1):
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}Broadcast cancelled.")
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await (
                    text.copy(chat_id)
                    if message.reply_to_message
                    else client.send_message(chat_id, text)
                )
                done += 1
            except ChannelPrivate:
                error += f"ChannelPrivate or channel private {chat_id}\n"
                continue

            except SlowmodeWait:
                error += f"SlowmodeWait or gc di timer {chat_id}\n"
                failed += 1

            except ChatWriteForbidden:
                error += f"ChatWriteForbidden or lu dimute {chat_id}\n"
                failed += 1

            except Forbidden:
                error += f"Forbidden or antispam grup aktif {chat_id}\n"
                failed += 1

            except UserBannedInChannel:
                error += f"UserBannedInChannel or lu limit {chat_id}\n"
                failed += 1

            except PeerIdInvalid:
                error += f"PeerIdInvalid or lu bukan pengguna grup ini {chat_id}\n"
                continue

            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await (
                        text.copy(chat_id)
                        if message.reply_to_message
                        else client.send_message(chat_id, text)
                    )
                    done += 1
                except Exception:
                    failed += 1
                    error += f"FloodWait retry gagal {chat_id}\n"
                except SlowmodeWait:
                    failed += 1
                    error += f"Grup timer {chat_id}\n"

            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"

            if index % 5 == 0:
                try:
                    await safe_edit(
                        proses,
                        f"""
<blockquote expandable>╭{em.proses}<b>{message.command[0]} {proses_}</b>
├{em.sukses}<b>sᴜᴄᴄᴇss :</b> <code>{done} ɢʀᴏᴜᴘs</code>
├{em.gagal}<b>ғᴀɪʟᴇᴅ :</b> <code>{failed} ɢʀᴏᴜᴘs</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>
""", parse_mode=ParseMode.HTML
                    )
                except MessageIdInvalid:
                    pass

    finally:
        task.end_task(task_id)
        await proses.delete()

    if error:
        error_dir = "storage/cache"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await safe_edit(
            proses,
            f"""
<blockquote expandable><b>{em.warn}{sukses_}</b>
<b>{em.sukses}sᴜᴄᴄᴇss : {done} ɢʀᴏᴜᴘs</b>
<b>{em.gagal}ғᴀɪʟᴇᴅ : {failed} ɢʀᴏᴜᴘs</b>
<b>{em.msg}ᴛʏᴘᴇ : {command}</b>
<b>{em.robot}ᴛᴀsᴋ ɪᴅ :</b> <code>{task_id}</code>
<b>{em.profil}{owner_}</b>

<b>ᴛʏᴘᴇ <code>{prefix[0]}bc-error</code> ᴛᴏ ᴠɪᴇᴡ ғᴀɪʟᴇᴅ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ.</b></blockquote>""", parse_mode=ParseMode.HTML
        )
    else:
        return await safe_edit(
            proses,
            f"""
<blockquote expandable><b>{em.warn}{sukses_}</b>
<b>{em.sukses}sᴜᴄᴄᴇss : {done} ɢʀᴏᴜᴘs</b>
<b>{em.gagal}ғᴀɪʟᴇᴅ : {failed} ɢʀᴏᴜᴘs</b>
<b>{em.msg}ᴛʏᴘᴇ : {command}</b>
<b>{em.robot}ᴛᴀsᴋ ɪᴅ :</b> <code>{task_id}</code>
<b>{em.profil}{owner_}</b></blockquote>""", parse_mode=ParseMode.HTML
        )

@CMD.UBOT("cekdb")
async def cekdb(client, message):
    data = await dB.get_var(client.me.id, "BLACKLIST_GCAST")
    await message.reply(f"<code>{type(data)}</code>\n<code>{data}</code>")

@CMD.UBOT("gcast")
@CMD.DEV_CMD("gcast")
@CMD.FAKEDEV("gcast")
async def gcast_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    async def safe_edit(msg_obj, text, **kwargs):
        try:
            return await msg_obj.edit(text, **kwargs)
        except MessageIdInvalid:
            return await message.reply(text, **kwargs)
    proses = await animate_proses(message, em.proses) 

    if not proses:
        return

    text = client.get_message(message)

    if not text:
        return await safe_edit(
            proses,
            f"{em.gagal}<code>{message.text.split()[0]}</code> <b>text or give text</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    await safe_edit(
        proses,
        f"""<blockquote expandable>╭{em.proses}<b>{message.command[0]} {proses_}</b>
├{em.sukses}<b>sᴜᴄᴄᴇss :</b> <code>0 ɢʀᴏᴜᴘs</code>
├{em.gagal}<b>ғᴀɪʟᴇᴅ :</b> <code>0 ɢʀᴏᴜᴘs</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>""", parse_mode=ParseMode.HTML
    )
    chats = await client.get_chat_id("group")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"{em.gagal}**Error failed broadcast:**\n"
    try:
        for index, chat_id in enumerate(chats, 1):
            if not task.is_active(task_id):
                return await safe_edit(
                    proses,
                    f"{em.gagal}{message.command[0]} cancelled.")
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await (
                    text.copy(chat_id)
                    if message.reply_to_message
                    else client.send_message(chat_id, text)
                )
                done += 1
            except ChannelPrivate:
                error += f"ChannelPrivate or channel private {chat_id}\n"
                continue

            except SlowmodeWait:
                error += f"SlowmodeWait or gc di timer {chat_id}\n"
                failed += 1

            except ChatWriteForbidden:
                error += f"ChatWriteForbidden or lu dimute {chat_id}\n"
                failed += 1

            except Forbidden:
                error += f"Forbidden or antispam grup aktif {chat_id}\n"
                failed += 1

            except UserBannedInChannel:
                error += f"UserBannedInChannel or lu limit {chat_id}\n"
                failed += 1

            except PeerIdInvalid:
                error += f"PeerIdInvalid or lu bukan pengguna grup ini {chat_id}\n"
                continue

            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await (
                        text.copy(chat_id)
                        if message.reply_to_message
                        else client.send_message(chat_id, text)
                    )
                    done += 1
                except Exception:
                    failed += 1
                    error += f"FloodWait retry gagal {chat_id}\n"
                except SlowmodeWait:
                    failed += 1
                    error += f"Grup timer {chat_id}\n"

            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"

            if index % 5 == 0:
                try:
                    await safe_edit(
                        proses,
                        f"""
<blockquote expandable>╭{em.proses}<b>{message.command[0]} {proses_}</b>
├{em.sukses}<b>sᴜᴄᴄᴇss :</b> <code>{done} ɢʀᴏᴜᴘs</code>
├{em.gagal}<b>ғᴀɪʟᴇᴅ :</b> <code>{failed} ɢʀᴏᴜᴘs</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>""", parse_mode=ParseMode.HTML
                    )
                except MessageIdInvalid:
                    pass

    finally:
        task.end_task(task_id)
        await proses.delete()

    if error:
        error_dir = "storage/cache"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await safe_edit(
            proses,
            f"""
<blockquote expandable>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done} ɢʀᴏᴜᴘs</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed} ɢʀᴏᴜᴘs</b>
<b>├{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b>

<b>Type <code>{prefix[0]}bc-error</code> ᴛᴏ ᴠɪᴇᴡ ғᴀɪʟᴇᴅ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ.</b></blockquote>""", parse_mode=ParseMode.HTML
        )
    else:
        return await safe_edit(
            proses,
            f"""
<blockquote expandable>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done} ɢʀᴏᴜᴘs</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed} ɢʀᴏᴜᴘs</b>
<b>├{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b></blockquote>""", parse_mode=ParseMode.HTML
        )


@CMD.UBOT("ucast")
@CMD.DEV_CMD("ucast")
@CMD.FAKEDEV("ucast")
async def broadcast(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    async def safe_edit(msg_obj, text, **kwargs):
        try:
            return await msg_obj.edit(text, **kwargs)
        except MessageIdInvalid:
            return await message.reply(text, **kwargs)
    proses = await animate_proses(message, em.proses) 

    if not proses:
        return

    text = client.get_message(message)

    if not text:
        return await safe_edit(
            proses,
            f"{em.gagal}<code>{message.text.split()[0]}</code> <b>text or give text</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    await safe_edit(
        proses,
        f"""<blockquote expandable>╭{em.proses}<b>{message.command[0]} {proses_}</b>
├{em.sukses}<b>sᴜᴄᴄᴇss :</b> <code>0 ɢʀᴏᴜᴘs</code>
├{em.gagal}<b>ғᴀɪʟᴇᴅ :</b> <code>0 ɢʀᴏᴜᴘs</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>""", parse_mode=ParseMode.HTML
    )
    chats = await client.get_chat_id("private")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"{em.gagal}**Error failed broadcast:**\n"
    try:
        for index, chat_id in enumerate(chats, 1):
            if not task.is_active(task_id):
                return await safe_edit(
                    proses,
                    f"{em.gagal}{message.command[0]} cancelled.")
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await (
                    text.copy(chat_id)
                    if message.reply_to_message
                    else client.send_message(chat_id, text)
                )
                done += 1
            except ChannelPrivate:
                error += f"ChannelPrivate or channel private {chat_id}\n"
                continue

            except SlowmodeWait:
                error += f"SlowmodeWait or gc di timer {chat_id}\n"
                failed += 1

            except ChatWriteForbidden:
                error += f"ChatWriteForbidden or lu dimute {chat_id}\n"
                failed += 1

            except Forbidden:
                error += f"Forbidden or antispam grup aktif {chat_id}\n"
                failed += 1

            except UserBannedInChannel:
                error += f"UserBannedInChannel or lu limit {chat_id}\n"
                failed += 1

            except PeerIdInvalid:
                error += f"PeerIdInvalid or lu bukan pengguna grup ini {chat_id}\n"
                continue

            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await (
                        text.copy(chat_id)
                        if message.reply_to_message
                        else client.send_message(chat_id, text)
                    )
                    done += 1
                except Exception:
                    failed += 1
                    error += f"FloodWait retry gagal {chat_id}\n"
                except SlowmodeWait:
                    failed += 1
                    error += f"Grup timer {chat_id}\n"

            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"

            if index % 5 == 0:
                try:
                    await safe_edit(
                        proses,
                        f"""
<blockquote expandable>╭{em.proses}<b>{message.command[0]} {proses_}</b>
├{em.sukses}<b>sᴜᴄᴄᴇss :</b> <code>{done} ɢʀᴏᴜᴘs</code>
├{em.gagal}<b>ғᴀɪʟᴇᴅ :</b> <code>{failed} ɢʀᴏᴜᴘs</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>""", parse_mode=ParseMode.HTML
                    )
                except MessageIdInvalid:
                    pass

    finally:
        task.end_task(task_id)
        await proses.delete()

    if error:
        error_dir = "storage/cache"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await safe_edit(
            proses,
            f"""
<blockquote expandable>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done} ɢʀᴏᴜᴘs</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed} ɢʀᴏᴜᴘs</b>
<b>├{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b>

<b>Type <code>{prefix[0]}bc-error</code> ᴛᴏ ᴠɪᴇᴡ ғᴀɪʟᴇᴅ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ.</b></blockquote>""", parse_mode=ParseMode.HTML
        )
    else:
        return await safe_edit(
            proses,
            f"""
<blockquote expandable>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done} ɢʀᴏᴜᴘs</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed} ɢʀᴏᴜᴘs</b>
<b>├{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b></blockquote>""", parse_mode=ParseMode.HTML
        )


@CMD.UBOT("bc-error")
@CMD.DEV_CMD("bc-error")
@CMD.FAKEDEV("bc-error")
async def _(client, message):
    oy = await message.reply("<b>Reading error logs...</b>")
    try:
        error_file = f"storage/cache/{client.me.id}_errors.txt"
        try:
            with open(error_file, "r") as f:
                content = f.read().strip()

            if not content:
                await oy.edit("<b>No errors found in log file.</b>")
                return
            if len(content) > 4000:
                content = content[-4000:]
                content = f"... (truncated)\n\n{content}"

            message_text = f"<b>📋 Error Logs:</b>\n\n<code>{content}</code>"

            return await oy.edit(message_text)

        except FileNotFoundError:
            return await oy.edit("<b>Error log file not found!</b>")

    except Exception:
        try:
            error_file = f"storage/cache/{client.me.id}_error.txt"
            with open(error_file, "r") as f:
                content = f.read().strip()

            if not content:
                await oy.edit("<b>No errors found in fallback log file.</b>")
                return

            if len(content) > 4000:
                content = content[-4000:]
                content = f"... (truncated)\n\n{content}"

            message_text = (
                f"<b>📋 Error Logs (from fallback):</b>\n\n<code>{content}</code>"
            )

            await client.send_message("me", message_text)
            return await oy.edit("<b>Cek saved message</b>")

        except Exception as e:
            return await oy.edit(f"<b>Failed to read error logs: {str(e)}</b>")


async def broadcast_db(
    client, message, em, prefix, done, failed, blacklist, task, task_id, proses
):
    command, text = client.extract_type_and_msg(message)
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    chatsdb = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    if not chatsdb:
        return await proses.edit(
            f"{em.gagal}**You don't have broadcastdb !!Please type `{prefix[0]} add-bcdb 'in the group or user.**"
        )
    try:
        for chat_id in chatsdb:
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}**Broadcast cancelled.**")
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await (
                    text.copy(chat_id)
                    if message.reply_to_message
                    else client.send_message(chat_id, text)
                )
                done += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await (
                    text.copy(chat_id)
                    if message.reply_to_message
                    else client.send_message(chat_id, text)
                )
            except Exception:
                failed += 1
                continue
    finally:
        task.end_task(task_id)
        await proses.delete()

    return await message.reply(
        f"""
<blockquote>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done}</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed}</b>
<b>├{em.msg}ᴛʏᴘᴇ : {command}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b></blockquote>

<blockquote><b>{em.profil}{owner_}</b></blockquote>"""
    )


@CMD.UBOT("cancel")
@CMD.DEV_CMD("cancel")
@CMD.FAKEDEV("cancel")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    prefix = client.get_prefix(client.me.id)
    if len(message.command) != 2:
        return await message.reply(
            f"{em.gagal}**Please provide a task ID to cancel.\nType `{prefix[0]}task` to view list task running.**"
        )

    task_id = message.command[1]

    if not task.is_active(task_id):
        return await message.reply(
            f"{em.gagal}**No active task found with ID: #`{task_id}`**"
        )
    task.end_task(task_id)
    return await message.reply(f"{em.sukses}**Ended task: #`{task_id}`**")


@CMD.UBOT("addbl")
@CMD.DEV_CMD("addbl")
@CMD.FAKEDEV("addbl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pp = await animate_proses(message, em.proses) 
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await pp.edit(f"{em.gagal}**chat_id must be in the form of numbers!**")
    try:
        chat = await client.get_chat(chat_id)
    except Exception:
        return await pp.edit(f"{em.gagal} chat_id tidak ditemukan atau tidak dapat di akses")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        name = chat.title
    else: 
        name = (
        chat.title
        or f"{chat.first_name or ''} {chat.last_name or ''}".strip()
        or chat.username
        or str(chat.id)
    )

    if chat_id in blacklist:
        return await pp.edit(f"{em.gagal}**`{name}` already in the blacklist-Gcast!**")
    await dB.add_to_var(client.me.id, "BLACKLIST_GCAST", chat_id)
    return await pp.edit(
        f"<blockquote>{em.sukses}<b>sᴜᴋsᴇs ᴍᴇɴᴀᴍʙᴀʜᴋᴀɴ\n{em.msg}ɴᴀᴍᴀ : `{name}`\n{em.ket}{keterangan_} : `ʙᴇʙᴀs ᴅᴀʀɪ ɴᴇʀᴀᴋᴀ`</b></blockquote>"
    )

@CMD.UBOT("fixbl")
async def fix_blacklist(client, message):
    await dB.set_var(client.me.id, "BLACKLIST_GCAST", "")
    return await message.reply("✅ BLACKLIST_GCAST berhasil di reset!")

@CMD.UBOT("delbl")
@CMD.DEV_CMD("delbl")
@CMD.FAKEDEV("delbl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    pp = await animate_proses(message, em.proses)

    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST") or []

    # =========================
    # FIX 1: HANDLE ARGUMENT DULU
    # =========================
    if len(message.command) > 1:

        if message.command[1].lower() == "all":
            for A in blacklist:
                await dB.remove_from_var(client.me.id, "BLACKLIST_GCAST", A)

            return await pp.edit(
                f"{em.sukses}<b>Successfully delete all blacklist-gcast lists!</b>"
            )

        chat_id = message.command[1]

        try:
            chat_id = int(chat_id)
        except ValueError:
            return await pp.edit(
                f"{em.gagal}**chat_id must be in the form of numbers!**"
            )

    else:
        chat_id = message.chat.id

    # =========================
    # FIX 2: get_chat setelah chat_id valid
    # =========================
    try:
        chat = await client.get_chat(chat_id)
    except Exception:
        return await pp.edit(
            f"{em.gagal} chat_id tidak ditemukan atau tidak dapat di akses"
        )

    # FIX 3: gunakan chat.type, bukan message.chat.type
    chat_type = chat.type

    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        name = chat.title
    else:
        name = (
            chat.title
            or f"{chat.first_name or ''} {chat.last_name or ''}".strip()
            or chat.username
            or str(chat.id)
        )

    # =========================
    # LOGIC DELETE (TETAP SAMA)
    # =========================
    try:
        if chat_id not in blacklist:
            return await pp.edit(
                f"{em.gagal}**`{name}` is not in blacklists!**"
            )

        await dB.remove_from_var(client.me.id, "BLACKLIST_GCAST", chat_id)

        return await pp.edit(
            f"{em.sukses}**Successfully delete `{name}` from the blacklist-gcast list!**"
        )

    except Exception as er:
        return await pp.edit(f"{em.gagal}ERRORR: `{str(er)}`!!")


@CMD.UBOT("listbl")
@CMD.DEV_CMD("listbl")
@CMD.FAKEDEV("listbl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    pp = await animate_proses(message, em.proses)
    if blacklist == []:
        return await pp.edit(f"{em.gagal}**Your Blacklist-Gcast Data is still empty!**")
    msg = f"<blockquote>{em.msg}Total Blacklist-Gcast: {len(blacklist)}</blockquote>\n\n"
    for num, x in enumerate(blacklist, 1):
        try:
            chat = await client.get_chat(x)
            name = chat.title or f"{chat.first_name} {chat.last_name or ''}"
            msg += f"<blockquote>{num}. {name}|`{chat.id}`</blockquote>\n"
        except Exception:
            msg += f"<blockquote>{num}. `{x}`</blockquote>\n"
    if len(msg) > 4096:
        link = await Tools.paste(msg)
        await pp.edit(f"{em.proses}**Message is too long, uploading to pastebin...**")
        await asyncio.sleep(1)
        return await message.reply_text(
            f"{em.sukses}**<a href='{link}'>Click here </a> to see your blacklist-gcast list.**",
            disable_web_page_preview=True,
        )
    else:
        await pp.delete()
        return await message.reply_text(msg)


@CMD.UBOT("add-bcdb")
@CMD.DEV_CMD("add-bcdb")
@CMD.FAKEDEV("add_bcdb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pp = await animate_proses(message, em.proses) 
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    blacklist = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        name = message.chat.title
    elif chat_type == ChatType.PRIVATE:
        name = f"{message.chat.first_name}{message.chat.last_name or ''}"
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await pp.edit(f"{em.gagal}**Chat_id must be a number!**")

    if chat_id in blacklist:
        return await pp.edit(f"{em.gagal}`{name}` **Already on Broadcast-DB!**")
    await dB.add_to_var(client.me.id, "BROADCASTDB", chat_id)
    return await pp.edit(
        f"{em.sukses}**Successfully added `{name}` into broadcast-db**"
    )


@CMD.UBOT("del-bcdb")
@CMD.DEV_CMD("del_bcdb")
@CMD.FAKEDEV("del-bcdb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pp = await animate_proses(message, em.proses)
    blacklist = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        name = message.chat.title
    elif chat_type == ChatType.PRIVATE:
        name = f"{message.chat.first_name}{message.chat.last_name or ''}"
    try:
        if len(message.command) < 2:
            chat_id = message.chat.id

            if chat_id not in blacklist:
                return await pp.edit(f"{em.gagal}`{name}` **is not in broadcast-db!**")
            await dB.remove_from_var(client.me.id, "BROADCASTDB", chat_id)
            return await pp.edit(
                f"{em.sukses}**Successfully delete `{name} 'from the broadcast list-db!**"
            )
        else:
            if message.command[1] == "all":
                for A in blacklist:
                    await dB.remove_from_var(client.me.id, "BROADCASTDB", A)
                return await pp.edit(
                    f"{em.sukses}Successfully delete all broadcast lists-DB!"
                )
            else:
                chat_id = message.command[1]
                try:
                    chat_id = int(chat_id)
                except ValueError:
                    return await pp.edit(
                        f"{em.gagal}**Please give a valid chat_id.Error `{chat_id}`!**"
                    )

                if chat_id not in blacklist:
                    return await pp.edit(f"{em.gagal}`{name}` **not in broadcast-db!**")
                await dB.remove_from_var(client.me.id, "BROADCASTDB", chat_id)
                return await pp.edit(
                    f"{em.sukses}**Successfully delete `{name}` from the broadcast list-db!**"
                )
    except Exception as er:
        return await pp.edit(f"{em.gagal}ERRORR: `{str(er)}`!!")


@CMD.UBOT("list-bcdb")
@CMD.DEV_CMD("list-bcdb")
@CMD.FAKEDEV("list-bcdb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    blacklist = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    pp = await animate_proses(message, em.proses)
    if blacklist == []:
        return await pp.edit(f"{em.gagal}**Your broadcast-DB data is still empty!**")
    msg = f"{em.msg}**Total Broadcast-DB: {len(blacklist)}**\n\n"
    for num, x in enumerate(blacklist, 1):
        try:
            chat = await client.get_chat(x)
            name = chat.title or f"{chat.first_name} {chat.last_name or ''}"
            msg += f"**{num}. {name}|`{chat.id}`**\n"
        except Exception:
            msg += f"**{num}. `{x}`**\n"
    if len(msg) > 4096:
        link = await Tools.paste(msg)
        await pp.edit(f"{em.proses}**Message is too long, uploading to pastebin ...**")
        await asyncio.sleep(1)
        return await message.reply_text(
            f"{em.sukses}**<a href='{link}'>Click here </a> to see your broadcast list.**",
            disable_web_page_preview=True,
        )
    else:
        await pp.delete()
        return await message.reply_text(msg)


@CMD.UBOT("send")
@CMD.DEV_CMD("send")
@CMD.FAKEDEV("send")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if message.reply_to_message:
        chat_id = (
            message.chat.id if len(message.command) < 2 else message.text.split()[1]
        )
        try:
            if message.reply_to_message.reply_markup:
                state.set(client.me.id, "inline_send", id(message))
                query = f"inline_send {client.me.id}"
                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    chat_id,
                    bot.me.username,
                    query,
                )
                if inline:
                    return await message.delete()
        except Exception as er:
            return await message.reply(f"{em.gagal}ERROR: {str(er)}")
        else:
            try:
                await message.reply_to_message.copy(chat_id)
                await message.delete()
                return
            except Exception as er:
                return await message.reply(f"{em.gagal}ERROR: {str(er)}")
    else:
        if len(message.command) < 3:
            return
        chat_id, chat_text = message.text.split(None, 2)[1:]
        try:
            if "/" in chat_id:
                to_chat, msg_id = chat_id.split("/")
                await client.send_message(
                    to_chat, chat_text, reply_to_message_id=int(msg_id)
                )
                await message.delete()
                return
            else:
                await client.send_message(chat_id, chat_text)
                await message.delete()
                return
        except Exception as er:
            return await message.reply(f"{em.gagal}ERROR: {str(er)}")
