import asyncio
from asyncio import sleep
import html
import contextlib
from Navy import bot
from config import DEVS
from Navy.database import dB
from pyrogram.enums import ParseMode
from pyrogram import filters, Client
from Navy.helpers import CMD
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, Message



last_welcome_messages = {}

@CMD.BOT("welcome")
async def welcome_cmd(client, message: Message):
    print(f"[DEBUG] /welcome command triggered by {message.from_user.id if message.from_user else 'Unknown'}")
    
    if not message.from_user or message.from_user.id not in DEVS:
        print("[DEBUG] User not in DEVS, command aborted")
        return await message.reply("**Hanya developer yang dapat mengatur fitur welcome.**")

    if len(message.command) == 1:
        print("[DEBUG] No subcommand provided")
        return await message.reply("Gunakan: `/welcome on` atau `/welcome off`")

    status = message.command[1].strip().lower()
    group_id = str(message.chat.id)
    print(f"[DEBUG] Setting welcome status '{status}' for group {group_id}")

    if status in ["off", "no"]:
        await dB.set_var(group_id, "WELCOME", "OFF")
        print("[DEBUG] Welcome disabled in DB")
        return await message.reply("✅ **Welcome dinonaktifkan di grup ini.**")

    elif status in ["on", "yes"]:
        await dB.remove_var(group_id, "WELCOME")
        print("[DEBUG] Welcome enabled (default ON) in DB")
        return await message.reply("✅ **Welcome diaktifkan kembali (default ON).**")

    print("[DEBUG] Invalid subcommand provided")
    return await message.reply("Gunakan: `/welcome on` atau `/welcome off`")


@bot.on_message(filters.new_chat_members, group=98)
async def welcome_event(client, message: Message):
    print(f"[DEBUG] New chat members detected in chat {message.chat.id}")
    
    # Cek status welcome di DB
    welcome_status = await dB.get_var(str(message.chat.id), "WELCOME")
    print(f"[DEBUG] Welcome status from DB: {welcome_status}")
    if welcome_status == "OFF":
        print("[DEBUG] Welcome is OFF, ignoring event")
        return

    for user in message.new_chat_members:
        print(f"[DEBUG] Processing new member: {user.id} ({user.first_name})")
        try:
            # Hapus pesan welcome lama jika ada
            old_msg_id = last_welcome_messages.get(message.chat.id)
            if old_msg_id:
                print(f"[DEBUG] Deleting old welcome message {old_msg_id}")
                with contextlib.suppress(Exception):
                    await client.delete_messages(message.chat.id, old_msg_id)

            # Dapatkan jumlah member
            count = await client.get_chat_members_count(message.chat.id)
            print(f"[DEBUG] Total members count: {count}")

            # Format nama member
            fullname = f"{user.first_name} {user.last_name or ''}".strip()
            fullname = html.escape(fullname)
            mention = f'<a href="tg://user?id={user.id}">{fullname}</a>'

            # Format nama grup
            if message.chat.username:
                group_link = f"https://t.me/{message.chat.username}"
                groupname = f'<a href="{group_link}">{html.escape(message.chat.title)}</a>'
            else:
                groupname = html.escape(message.chat.title)
            print(f"[DEBUG] Group name: {groupname}")

            # Caption welcome
            caption = f"""<b>❅─────✧❅✦❅✧─────❅</b>
<blockquote><b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <code>{groupname}</code></b>
▰▰▰▰▰▰▰▰▰▰▰▰
<b>➻ ɴᴀᴍᴇ »</b> {mention}
<b>➻ ᴜsᴇʀ ɪᴅ »</b> <code>{user.id}</code>
<b>➻ ᴜsᴇʀɴᴀᴍᴇ »</b> @{user.username or "N/A"}
<b>➻ ᴛᴏᴛᴀʟ »</b> {count} ᴍᴇᴍʙᴇʀs
▰▰▰▰▰▰▰▰▰▰▰▰</blockquote>
<blockquote><b>ᴇɴᴊᴏʏ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ, ᴅᴏɴ'ᴛ ғᴏʀɢᴇᴛ ᴛᴏ ʀᴇᴀᴅ ᴀɴᴅ ᴏʙᴇʏ ᴛʜᴇ ʀᴜʟᴇs. ᴛʜᴀɴᴋ ʏᴏᴜ.</b></blockquote>
<b>❅─────✧❅✦❅✧─────❅</b>"""

            # Kirim photo, fallback ke teks jika gagal
            try:
                sent = await client.send_photo(
                    message.chat.id,
                    photo="storage/welcome.png",
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏", user_id=user.id)],
                        [InlineKeyboardButton("๏ sᴜᴘᴘᴏʀᴛ ๏", url="https://t.me/+YePmwjntxSM3OTU1")],
                        [InlineKeyboardButton("๏ ᴍᴏʀᴇ ɪɴғᴏ ๏", url="https://FerlyKurniawan.github.io/Portofolio")]
                    ])
                )
                print(f"[DEBUG] Welcome photo sent with message ID {sent.id}")
            except Exception as e:
                print(f"[WELCOME WARNING] Failed to send photo: {e}")
                sent = await client.send_message(
                    message.chat.id,
                    caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏", user_id=user.id)],
                        [InlineKeyboardButton("๏ sᴜᴘᴘᴏʀᴛ ๏", url="https://t.me/+YePmwjntxSM3OTU1")],
                        [InlineKeyboardButton("๏ ᴍᴏʀᴇ ɪɴғᴏ ๏", url="https://FerlyKurniawan.github.io/Portofolio")]
                    ])
                )
                print(f"[DEBUG] Welcome message sent as text fallback with message ID {sent.id}")

            # Simpan ID pesan terakhir
            last_welcome_messages[message.chat.id] = sent.id

            # Tunggu 120 detik lalu hapus pesan
            await sleep(120)
            if last_welcome_messages.get(message.chat.id) == sent.id:
                with contextlib.suppress(Exception):
                    await client.delete_messages(message.chat.id, sent.id)
                last_welcome_messages.pop(message.chat.id, None)
                print(f"[DEBUG] Welcome message {sent.id} deleted after 120s")

        except Exception as e:
            print(f"[WELCOME ERROR] {e}")