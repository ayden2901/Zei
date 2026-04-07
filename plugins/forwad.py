import asyncio
import os
import random

from pyrogram.enums import ChatType 
from Navy.helpers.exceptions import ChatSendPlainForbidden
from pyrogram.errors import (ChannelPrivate,
                             ChatWriteForbidden, FloodWait, Forbidden,
                             PeerIdInvalid, SlowmodeWait, UserBannedInChannel)

from config import BLACKLIST_GCAST, DEVS
from Navy import bot
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task

__MODULES__ = "ғᴏʀᴡᴀʀᴅ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **ғᴏʀᴡᴀʀᴅ**</u>

<blockquote>**Perintah broadcast ғᴏʀᴡᴀʀᴅ**</blockquote>
 `{0}bcfw` (reply pesan)

<blockquote>**Menambahkan Pesan ᴀᴜᴛᴏғᴏʀᴡᴀʀᴅ**</blockquote>
 `{0}autofw add` (reply pesan)

<blockquote>**Aktif/nonaktifkan ᴀᴜᴛᴏғᴏʀᴡᴀʀᴅ**</blockquote>
    `{0}autofw` (on/off)

<blockquote>**Hapus pesan dari daftar ᴀᴜᴛᴏғᴏʀᴡᴀʀᴅ**</blockquote>
    `{0}autofw del` (nomor/all)

<blockquote>**Set delay antar forward**</blockquote>
    `{0}autofw delay` (menit)

<blockquote>**Daftar pesan ᴀᴜᴛᴏғᴏʀᴡᴀʀᴅ**</blockquote>
    `{0}listautofw`

<b>   {1}</b>
"""


@CMD.UBOT("bcfw")
@CMD.DEV_CMD("bcfw")
@CMD.FAKEDEV("bcfw")
async def broadcast_forward_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"<b>{em.proses}{proses_}</b>")

    # Pastikan pesan direply
    if not message.reply_to_message:
        return await proses.edit(
            f"{em.gagal}<code>{message.command[0]}</code> hanya bisa dijalankan dengan membalas pesan yang ingin diteruskan."
        )

    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    await proses.edit(
        f"""
<blockquote><b>{message.command[0]} {proses_}</b>{em.proses}
{em.profil}<b>{owner_}</b>
{em.robot}<b>ᴄᴀɴᴄᴇʟ {message.command[0]} ᴜsɪɴɢ <code>{prefix[0]}cancel {task_id}</code> !!</b></blockquote>"""
    )

    chats = await client.get_chat_id("group")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"{em.gagal}**Error failed broadcast:**\n"

    try:
        for chat_id in chats:
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}{message.command[0]} cancelled.")
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await message.reply_to_message.forward(chat_id)
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
            except ChatSendPlainForbidden:
                error += f"ChatSendPlainForbidden or ga bisa kirim teks {chat_id}\n"
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
                    await message.reply_to_message.forward(chat_id)
                except Exception:
                    failed += 1
                except SlowmodeWait:
                    failed += 1
                    error += f"Grup timer {chat_id}\n"
            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"
    finally:
        task.end_task(task_id)
        await proses.delete()

    if error:
        error_dir = "storage/cache"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await message.reply(
            f"""
<blockquote><b>{em.warn}{sukses_}</b>
<b>{em.sukses}sᴜᴄᴄᴇss : {done}</b>
<b>{em.gagal}ғᴀɪʟᴇᴅ : {failed}</b>
<b>{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>{em.profil}{owner_}</b>

<b>ᴛʏᴘᴇ <code>{prefix[0]}bc-error</code> ᴛᴏ ᴠɪᴇᴡ ғᴀɪʟᴇᴅ ɪɴ ʙʀᴏᴀᴅᴄᴀsᴛ.</b></blockquote>"""
        )
    else:
        return await message.reply(
            f"""
<blockquote><b>{em.warn}{sukses_}</b>
<b>{em.sukses}sᴜᴄᴄᴇss : {done}</b>
<b>{em.gagal}ғᴀɪʟᴇᴅ : {failed}</b>
<b>{em.msg}ᴛʏᴘᴇ : {message.command[0]}</b>
<b>{em.robot}ᴛᴀsᴋ ɪᴅ : `{task_id}`</b>
<b>{em.profil}{owner_}</b></blockquote>"""
        )


AFW = []

def extract_type_and_text(message):
    args = message.text.split(None, 2)
    if len(args) < 2:
        return None, None
    return args[1], args[2] if len(args) > 2 else None

@CMD.UBOT("autofw")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    msg = await message.reply(f"{em.proses}**{proses_[4]}**")
    
    type, value = extract_type_and_text(message)
    reply = message.reply_to_message
    logs = "me"
    auto_fw_vars = await dB.get_var(client.me.id, "AUTO_FWD")
    send_msg = []

    if type == "on":
        if not auto_fw_vars:
            return await msg.edit(f"{em.gagal}**Tambah pesan dulu sebelum nyalakan auto forward!**")

        if client.me.id not in AFW:
            await msg.edit(
                f"<blockquote><b>ᴅɪᴍᴜʟᴀɪ</b>{em.proses}</blockquote>\n"
                f"<blockquote>{em.sukses}<b>ᴀᴜᴛᴏғᴏʀᴡᴀʀᴅ</b>\n"
                f"{em.robot}<b>ᴍᴀᴛɪᴋᴀɴ ᴅᴇɴɢᴀɴ `{message.text.split()[0]} off`.</b></blockquote>"
            )
            AFW.append(client.me.id)
            done = 0

            while client.me.id in AFW:
                delay = await dB.get_var(client.me.id, "DELAY_FWD") or 1
                blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
                send_msg.clear()

                for ax in auto_fw_vars:
                    send_msg.append(int(ax["message_id"]))

                txt = random.choice(send_msg)
                msg_id = await client.get_messages(logs, txt)

                proses_msg = await message.reply(f"{em.proses} Sedang mengirim auto forward putaran ke `{done+1}`...")

                group = 0
                async for dialog in client.get_dialogs():
                    if (
                        dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
                        and dialog.chat.id not in blacklist
                        and dialog.chat.id not in BLACKLIST_GCAST
                    ):
                        try:
                            await asyncio.sleep(1)
                            await msg_id.forward(dialog.chat.id)
                            group += 1
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            await msg_id.forward(dialog.chat.id)
                            group += 1
                        except Exception:
                            pass

                if client.me.id not in AFW:
                    return

                done += 1
                await proses_msg.delete()
                await message.reply(
                    f"<blockquote>{em.sukses}<b>Auto Forward ke: `{group}` grup</b>\n"
                    f"{em.robot}<b>Putaran ke: `{done}`</b>\n"
                    f"{em.proses}<b>Tunggu `{delay}` menit</b></blockquote>"
                )

                await asyncio.sleep(int(60 * int(delay)))

        else:
            return await msg.delete()

    elif type == "off":
        if client.me.id in AFW:
            AFW.remove(client.me.id)
            return await msg.edit(f"{em.gagal}<b>Auto forward dimatikan.</b>")
        else:
            return await msg.delete()

    elif type == "add":
        if not reply:
            return await msg.edit(f"{em.gagal}<b>Reply ke pesan dulu goblok!</b>")
        await add_forward_message(message)
        return await msg.edit(f"{em.sukses}<b>Pesan disimpan untuk auto forward.</b>")

    elif type == "delay":
        await dB.set_var(client.me.id, "DELAY_FWD", value)
        return await msg.edit(f"{em.sukses}<b>Delay auto forward diatur ke: <code>{value}</code> menit</b>")

    elif type == "del":
        if not value:
            return await msg.edit(f"{em.gagal}<b>Masukkan nomor atau ketik `all`.</b>")
        if value == "all":
            await dB.set_var(client.me.id, "AUTO_FWD", [])
            return await msg.edit(f"{em.sukses}<b>Semua pesan dihapus dari auto forward.</b>")
        try:
            value = int(value) - 1
            auto_fw_vars.pop(value)
            await dB.set_var(client.me.id, "AUTO_FWD", auto_fw_vars)
            return await msg.edit(f"{em.sukses}<b>Pesan nomor <code>{value+1}</code> dihapus.</b>")
        except Exception as error:
            return await msg.edit(str(error))

    else:
        return await msg.edit(f"{em.gagal}<b>Salah perintah bang, baca help!</b>")


@CMD.UBOT("listautofw")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    msg = await message.reply(f"{em.proses}**{proses_[4]}**")
    data = await dB.get_var(client.me.id, "AUTO_FWD") or []
    if not data:
        return await msg.edit(f"{em.gagal}<b>Belum ada pesan untuk auto forward.</b>")
    teks = f"<u>{em.data}<b>Daftar Pesan Auto Forward:</b></u>\n\n"
    for i, x in enumerate(data, 1):
        msgx = await client.get_messages("me", int(x["message_id"]))
        if msgx.text:
            teks += f"<blockquote><b>{i}. {msgx.text}</b></blockquote>\n"
        else:
            teks += f"<blockquote><b>{i}. Media type: {x['type']}</b></blockquote>\n"
    return await msg.edit(teks)


async def add_forward_message(message):
    client = message._client
    data = await dB.get_var(client.me.id, "AUTO_FWD") or []
    rep = message.reply_to_message
    type_mapping = {
        "text": rep.text,
        "photo": rep.photo,
        "voice": rep.voice,
        "audio": rep.audio,
        "video": rep.video,
        "video_note": rep.video_note,
        "animation": rep.animation,
        "sticker": rep.sticker,
        "document": rep.document,
        "contact": rep.contact,
    }
    for media_type, media in type_mapping.items():
        if media:
            send = await rep.forward("me")
            value = {
                "type": media_type,
                "message_id": send.id,
            }
            data.append(value)
            await dB.set_var(client.me.id, "AUTO_FWD", data)
            break