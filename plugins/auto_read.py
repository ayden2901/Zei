import asyncio
from asyncio import CancelledError, create_task, sleep
from asyncio import create_task, sleep, CancelledError
import aiosqlite
from pyrogram import filters, Client, types
from pyrogram.raw.functions.messages import ReadMentions
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import Message
from Navy.helpers import CMD, Emoji, animate_proses, Tools
from Navy import bot, navy
from Navy.database import dB



autoread_tasks = {}

@CMD.UBOT("autoread")
async def autoread_handler(client, message: Message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    user_id = client.me.id
    pros = await animate_proses(message, em.proses)
    if not pros:
        return

    cmd = message.text.strip().lower()

    if cmd.endswith(" on"):
        if user_id in autoread_tasks and not autoread_tasks[user_id].done():
            return await pros.edit(f"{em.warn}{keterangan_} : AutoRead sudah aktif.")

        task = create_task(start_autoread_loop(client))
        autoread_tasks[user_id] = task
        await dB.set_var(user_id, "autoread", "on")
        return await pros.edit(f"{em.sukses}AutoRead diaktifkan.")

    elif cmd.endswith(" off"):
        task = autoread_tasks.get(user_id)
        if task:
            task.cancel()
            try:
                await task
            except CancelledError:
                pass
            autoread_tasks.pop(user_id, None)
            await dB.set_var(user_id, "autoread", "off")
            return await pros.edit(f"{em.gagal}AutoRead dimatikan.")
        else:
            return await pros.edit(f"{em.warn}{keterangan_} : AutoRead belum aktif.")

    else:
        status = await dB.get_var(user_id, "autoread")
        if status == "on":
            return await pros.edit(f"{em.msg}Status AutoRead: ON ✅")
        else:
            return await pros.edit(f"{em.msg}Status AutoRead: OFF ❌")


async def start_autoread_loop(client):
    user_id = client.me.id
    if await dB.get_var(user_id, "autoread") != "on":
        return

    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    username = client.me.username.lower() if client.me.username else None
    print(f"▶️ AutoRead berjalan untuk user {user_id}")

    try:
        while True:
            async for dialog in client.get_dialogs():
                chat = dialog.chat
                chat_id = chat.id
                unread = dialog.unread_messages_count

                if unread == 0:
                    continue

                try:
                    if chat.type in ["group", "supergroup"]:
                        mention_ids = []
                        reply_ids = []
                        messages_checked = 0
                        last_message_id = 0

                        while messages_checked < 1500:
                            messages = [
                                msg async for msg in client.get_chat_history(
                                    chat_id,
                                    limit=100,
                                    offset_id=last_message_id
                                )
                            ]
                            if not messages:
                                break

                            last_message_id = min(msg.id for msg in messages) - 1
                            messages_checked += len(messages)

                            for msg in messages:
                                if not isinstance(msg, Message):
                                    continue

                                # Cek mention ke username
                                if msg.entities:
                                    for ent in msg.entities:
                                        if ent.type == "mention" and username and f"@{username}" in msg.text.lower():
                                            mention_ids.append(msg.id)
                                        elif ent.type == "text_mention" and ent.user and ent.user.id == user_id:
                                            mention_ids.append(msg.id)

                                # Cek jika reply ke kita
                                if msg.reply_to_message and msg.reply_to_message.from_user:
                                    if msg.reply_to_message.from_user.id == user_id:
                                        reply_ids.append(msg.id)

                            if len(messages) < 100:
                                break

                        ids_to_read = list(set(mention_ids + reply_ids))
                        if ids_to_read:
                            await client.read_messages(chat_id, ids_to_read)
                        else:
                            await client.read_chat_history(chat_id)

                        # Hapus notifikasi @mention secara paksa
                        try:
                            await client.invoke(ReadMentions(peer=await client.resolve_peer(chat_id)))
                        except Exception as e:
                            print(f"⚠️ Gagal invoke ReadMentions di {chat_id}: {e}")

                    else:
                        # Untuk private, bot, channel: langsung read semua
                        await client.read_chat_history(chat_id)

                except Exception as e:
                    print(f"❗ Error saat baca chat {chat_id}: {e}")

            await sleep(10)

    except CancelledError:
        print(f"⛔ AutoRead untuk user {user_id} dihentikan.")
    except Exception as e:
        print(f"⚠️ Error utama di loop AutoRead: {e}")
        await sleep(10)


__MODULES__ = "ᴀᴜᴛᴏʀᴇᴀᴅ"
__HELP__ = """<blockquote expandable><u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **ᴀᴜᴛᴏʀᴇᴀᴅ**</u>

<blockquote>**Set your account ᴀᴜᴛᴏʀᴇᴀᴅ**</blockquote>
    **you can set read chat on your account**
        `{0}autoread on` mengaktifkan fitur
        `{0}autoread off` menonaktifkan fitur

<b>   {1}</blockquote></b>
"""