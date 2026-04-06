import os
import asyncio
from pyrogram.types import Message
from pyrogram.enums import MessagesFilter
from config import LOG_BACKUP
from Navy.helpers import CMD, Emoji
from pyrogram.enums import MessagesFilter


__MODULES__ = "ᴄᴏʟᴏɴɢ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ᴄᴏʟᴏɴɢ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ᴄᴏʟᴏɴɢ</b>
    ➢ `{0}colong` [ʀᴇᴘʟʏ ᴍᴇᴅɪᴀ]
➢ `{0}colongall` [ᴛᴜᴊᴜᴀɴ] [ǫᴜᴇʀʏ] [ᴄᴏᴜɴᴛ]</blockquote>
<blockquote>❖ ʟɪsᴛ ǫᴜᴇʀʏ :
    ➢ ᴘʜᴏᴛᴏ
    ➢ ᴠɪᴅᴇᴏ
    ➢ ᴀᴜᴅɪᴏ
    ➢ ᴅᴏᴄᴜᴍᴇɴᴛ</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("colong")
async def _(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply ke pesan media yang mau kamu colong, bro 😎")

    msg = message.reply_to_message

    try:
        # Download media ke file lokal
        file_path = await client.download_media(msg)
        if not file_path:
            return await message.reply("❌ Gagal download media.")

        # Kirim ulang ke Saved Messages
        await client.send_document("me", file_path, caption=msg.caption or "")
        # Kirim ulang ke log backup
        await client.send_document(LOG_BACKUP, file_path, caption=msg.caption or "")

        # Hapus file lokal
        os.remove(file_path)

    except Exception as e:
        return await message.reply(f"❌ Gagal nyolong media:\n<code>{e}</code>")

    await message.delete()


@CMD.UBOT("colongall")
async def _(client, message: Message):
    if len(message.command) < 4:
        return await message.reply(
            "Format: `.colongall <chat_id> <photo|video|audio|document> <limit>`\n"
            "Contoh: `.colongall @channel video 5`"
        )

    chat_input = message.command[1]

    # Bersihkan input
    chat_input = (
        chat_input
        .replace("https://t.me/", "")
        .replace("http://t.me/", "")
        .replace("t.me/", "")
        .replace("@", "")
        .strip()
    )

    # Resolve chat
    try:
        chat = await client.get_chat(chat_input)
        chat_id = chat.id
    except Exception as e:
        return await message.reply(
            "❌ Chat tidak ditemukan atau username tidak valid.\n"
            "Kemungkinan penyebab:\n"
            "- Username salah\n"
            "- Channel private (belum join)\n"
            "- Channel sudah dihapus\n"
            f"\nError: <code>{e}</code>"
        )

    media_type = message.command[2].lower()

    try:
        limit = int(message.command[3])
    except ValueError:
        return await message.reply("Limit harus berupa angka.")

    filters_map = {
        "photo": MessagesFilter.PHOTO,
        "video": MessagesFilter.VIDEO,
        "audio": MessagesFilter.AUDIO,
        "document": MessagesFilter.DOCUMENT,
    }

    if media_type not in filters_map:
        return await message.reply(
            "Filter tidak valid.\nGunakan: photo, video, audio, document"
        )

    proses = await message.reply("🔄 Mengambil media...")
    count = 0

    try:
        async for msg in client.search_messages(
            chat_id,
            filter=filters_map[media_type],
            limit=limit
        ):
            try:
                # Cara normal (copy)
                await msg.copy("me")
                await msg.copy(LOG_BACKUP)

            except Exception as e:
                # Jika forward/copy dibatasi (channel protect)
                if "CHAT_FORWARDS_RESTRICTED" in str(e):
                    file_path = await msg.download()
                    if file_path:
                        await client.send_document(
                            "me",
                            file_path,
                            caption=msg.caption or ""
                        )
                        await client.send_document(
                            LOG_BACKUP,
                            file_path,
                            caption=msg.caption or ""
                        )
                        os.remove(file_path)
                else:
                    raise e

            count += 1
            await asyncio.sleep(1)

    except Exception as e:
        return await proses.edit(f"❌ Gagal:\n<code>{e}</code>")

    await proses.edit(f"✅ Berhasil mencuri {count} {media_type}")
    await message.delete()