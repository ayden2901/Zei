import asyncio
import os
from datetime import datetime
from io import BytesIO

from pyrogram import enums
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import (ChannelPrivate, FloodWait, PeerIdInvalid,
                             UsernameOccupied, UserNotParticipant)
from pyrogram.raw import functions

from Navy.helpers import CMD, Emoji

__MODULES__ = "sᴛᴀғғ"
__HELP__ = """<<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>sᴛᴀғғ</b></u>

<blockquote>❖ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>sᴛᴀғғ</b>
    ➢ `{0}adminlist`
    ➢ `{0}me`</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("adminlist")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(
        f"{emo.proses}<b>Processing to check the list of groups where you are an admin ..</b>"
    )

    a_chats = []
    me = await client.get_me()

    # 🔁 RETRY GET DIALOGS
    for _ in range(3):
        try:
            async for dialog in client.get_dialogs():
                try:
                    tipe = dialog.chat.type
                    if tipe in (enums.ChatType.SUPERGROUP, enums.ChatType.GROUP):
                        try:
                            gua = await dialog.chat.get_member(int(me.id))
                            if gua.status in (
                                enums.ChatMemberStatus.OWNER,
                                enums.ChatMemberStatus.ADMINISTRATOR,
                            ):
                                a_chats.append(dialog.chat)
                        except Exception:
                            continue
                except Exception:
                    continue
            break  # sukses, keluar loop

        except Exception as e:
            # 🔥 HANDLE SEMUA ERROR TELEGRAM
            if "Timeout" in str(e) or "RPC_CALL_FAIL" in str(e):
                await asyncio.sleep(3)
                continue
            else:
                return await pros.edit(
                    "❌ <b>Failed to get dialogs (Telegram error)</b>"
                )

    text = "<b>❒ LIST OF GROUPS WHERE YOU ARE AN ADMIN:</b>\n┃\n"

    if len(a_chats) == 0:
        text += "<b>You are not an admin anywhere.</b>"
        return await pros.edit(f"{text}")

    for count, chat in enumerate(a_chats, 1):
        try:
            title = chat.title
        except Exception:
            title = "Private Group"

        if count == len(a_chats):
            text += f"<b>┖ {title}</b>\n"
        else:
            text += f"<b>┣ {title}</b>\n"

    if len(text) > 4096:
        from io import BytesIO
        with BytesIO(str.encode(text)) as out_file:
            out_file.name = "adminlist.txt"
            await message.reply_document(
                document=out_file,
                caption=f"{emo.sukses}<b>Admin List {client.me.mention}.</b>",
            )
            return await pros.delete()
    else:
        return await pros.edit(f"{text}")


@CMD.UBOT("me")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"{emo.proses}<b>Processing to gather statistics ..</b>")
    start = datetime.now()
    pc = 0
    groups = 0
    super_groups = 0
    channels = 0
    bots = 0
    adminchats = 0
    banned = 0
    here = set()
    gue = await client.get_me()

    try:
        async for dialog in client.get_dialogs():
            try:
                if dialog.chat.type == ChatType.PRIVATE:
                    pc += 1
                elif dialog.chat.type == ChatType.BOT:
                    bots += 1
                elif dialog.chat.type == ChatType.GROUP:
                    groups += 1
                    ucel = await dialog.chat.get_member(int(gue.id))
                    if ucel.status in (
                        ChatMemberStatus.OWNER,
                        ChatMemberStatus.ADMINISTRATOR,
                    ):
                        adminchats += 1
                elif dialog.chat.type == ChatType.SUPERGROUP:
                    super_groups += 1
                    user_s = await dialog.chat.get_member(int(gue.id))
                    if user_s.status in (
                        ChatMemberStatus.OWNER,
                        ChatMemberStatus.ADMINISTRATOR,
                    ):
                        adminchats += 1
                elif dialog.chat.type == ChatType.CHANNEL:
                    channels += 1
            except ChannelPrivate:
                banned += 1
                here.add(dialog.chat.id)
                continue
            except UserNotParticipant:
                await client.leave_chat(dialog.chat.id)
                print(f"Bot is not a member of this chat, leaving: {dialog.chat.id}")
                continue
    except ChannelPrivate:
        banned += 1
        here.add(dialog.chat.id)
    except Exception as e:
        print(f"An error occurred: {str(e)} {dialog.chat.id}")

    end = datetime.now()
    waktu = (end - start).seconds

    if not here:
        here = 0

    return await pros.edit(
        f"""
{emo.sukses}<b>Successfully extracted your data in <code>{waktu}</code> seconds:

• <code>{pc}</code> Private Messages.
• <code>{groups}</code> Groups.
• <code>{super_groups}</code> Super Groups.
• <code>{channels}</code> Channels.
• <code>{adminchats}</code> Admin Chats.
• <code>{bots}</code> Bots.
• <code>{banned}</code> Problematic Groups.

I encountered issues with these chats: 
• <code>{here}</code></b>
"""
    )
