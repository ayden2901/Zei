"""
import asyncio
import os

from pyrogram.enums import ChatType
from pyrogram.errors import (ChannelPrivate, ChatSendPlainForbidden,
                             ChatWriteForbidden, FloodWait, Forbidden,
                             PeerIdInvalid, SlowmodeWait, UserBannedInChannel,
                             MessageIdInvalid)

from config import BLACKLIST_GCAST, DEVS
from Navy import bot
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task


@CMD.UBOT("test")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"<b>{em.proses}{proses_}</b>")

    text = client.get_message(message)

    if not text:
        return await proses.edit(
            f"{em.gagal}<code>{message.text.split()[0]}</code> <b>text or give text</b>"
        )

    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)

    await proses.edit(
        f
<blockquote>╭<b>{em.proses}{message.command[0]} {proses_}</b>
├{em.sukses}sᴜᴄᴄᴇss : <code>0</code>
├{em.gagal}ғᴀɪʟᴇᴅ : <code>0</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>

    )

    chats = await client.get_chat_id("group")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"{em.gagal}**Error failed broadcast:**\n"

    try:
        for index, chat_id in enumerate(chats, 1):
            if not task.is_active(task_id):
                try:
                    return await proses.edit(f"{em.gagal}{message.command[0]} cancelled.")
                except MessageIdInvalid:
                    return await proses.edit(f"{em.gagal}{message.command[0]} cancelled.")

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
            except SlowmodeWait:
                failed += 1
                error += f"SlowmodeWait or gc di timer {chat_id}\n"
            except ChatWriteForbidden:
                failed += 1
                error += f"ChatWriteForbidden or lu dimute {chat_id}\n"
            except Forbidden:
                failed += 1
                error += f"Forbidden or antispam grup aktif {chat_id}\n"
            except ChatSendPlainForbidden:
                failed += 1
                error += f"ChatSendPlainForbidden or ga bisa kirim teks {chat_id}\n"
            except UserBannedInChannel:
                failed += 1
                error += f"UserBannedInChannel or lu limit {chat_id}\n"
            except PeerIdInvalid:
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

            if index % 2 == 0:
                try:
                    await proses.edit(
                        f
<blockquote>╭<b>{em.proses}{message.command[0]} {proses_}</b>
├{em.sukses}sᴜᴄᴄᴇss : <code>{done}</code>
├{em.gagal}ғᴀɪʟᴇᴅ : <code>{failed}</code>
├{em.profil}<b>{owner_}</b>
╰{em.robot}<b><code>{prefix[0]}cancel {task_id}</code></b></blockquote>

                    )
                except MessageIdInvalid:
                    pass
    finally:
        task.end_task(task_id)
        try:
            await proses.delete()
        except MessageIdInvalid:
            pass

    if error:
        error_dir = "storage/cache"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await message.reply(
            f
<blockquote>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done}</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed}</b>
<b>├{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b>

<b>ᴛʏᴘᴇ <code>{prefix[0]}bc-error</code> ᴛᴏ ᴠɪᴇᴡ ғᴀɪʟᴇᴅ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ.</b></blockquote>
        )
    else:
        return await message.reply(
            f
<blockquote>❏<b>{em.warn}{sukses_}</b>
<b>├{em.sukses}sᴜᴄᴄᴇss : {done}</b>
<b>├{em.gagal}ғᴀɪʟᴇᴅ : {failed}</b>
<b>├{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>├{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>╰{em.profil}{owner_}</b></blockquote>
        )

"""