import asyncio

from pyrogram import enums
from pyrogram.errors import (
    UsernameNotOccupied,
    InviteHashInvalid,
    UserAlreadyParticipant,
    FloodWait,
)

from config import BLACKLIST_GCAST
from Navy.database import dB
from Navy.helpers import CMD, Emoji

__MODULES__ = "ᴊᴏɪɴᴇᴅ"
__HELP__ = """<blockquote>Command Help **Joined**</blockquote>

<blockquote>**Leave all channel** </blockquote>
    **You can leave all channel from your account, except youre admin and blacklist leave**
        `{0}leave channel`

<blockquote>**Leave all channel and group**</blockquote>
    **You can leave all channel and group, except youre admin and blacklist leave**
        `{0}leave global`

<blockquote>**Leave all mute**</blockquote>
    **You can leave all chat group if you restricted**
        `{0}leave mute`

<blockquote>**Leave all group**</blockquote> 
    **You can leave all chat group, except youre admin and blacklist leave**
        `{0}leave group`

<blockquote>**Join chat**</blockquote>
    **You can join to chat use id, url, or username**
        `{0}join` (chatid)

<blockquote>**Leave chat** </blockquote>
    **You can leave this chat now**
        `{0}kickme`

<blockquote>**Blacklist leave**</blockquote> 
    **Add chat to blacklist leave if you want**
        `{0}bl-leave` (chatid)

<blockquote>**Remove blacklist leave**</blockquote> 
    **Delete chat from blacklist leave from  your account**
        `{0}unbl-leave` (chatid)

<blockquote>**Get blacklist leave** </blockquote>
    **You can view all chats on blacklist leave**
        `{0}getbl-leave`

<blockquote>**Clear all blacklist leave**</blockquote> 
    **Or you can clear or delete all chats on blacklist leave**
    `{0}cleardb-leave`

<blockquote>**Get mute group**</blockquote> 
    **This command for check, where you has been restricted from chat**
        `{0}getmute`

<blockquote>**Note**: For the blacklist leave, when you use the leave command then you will not leave from db leave blacklist. </blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("getmute")
@CMD.DEV_CMD("getmute")
@CMD.FAKEDEV("getmute")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    output = ""
    msg = await message.reply(f"{em.proses}**{proses_[4]}**")

    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(dialog.chat.id, client.me.id)
                if member.status == enums.ChatMemberStatus.RESTRICTED:
                    chat = await client.get_chat(dialog.chat.id)
                    output += f"{chat.title} | [`{chat.id}`]\n"
            except Exception:
                continue

    if output:
        text = f"<blockquote><b>The list of groups that mute you are:</b>\n{output}</blockquote>"
    else:
        text = "<blockquote>List of groups that mute you are empty</blockquote>"

    return await msg.edit(text)


@CMD.UBOT("join")
@CMD.DEV_CMD("join")
@CMD.FAKEDEV("join")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give me link or username group/channel to join!**"
        )

    arg = message.text.split()[1]

    try:
        await client.join_chat(arg)

        return await proses.edit(
            f"{em.sukses}**Succesfully joined chat: {arg}**",
            disable_web_page_preview=True,
        )

    except UserAlreadyParticipant:
        return await proses.edit(
            f"{em.gagal}**You are already a member of this group/channel!**"
        )

    except (UsernameNotOccupied, InviteHashInvalid):
        return await proses.edit(
            f"{em.gagal}**Invalid link or username! Please check again.**"
        )

    except Exception as ex:
        return await proses.edit(
            f"{em.gagal}**Error:** `{str(ex)}`"
        )


@CMD.UBOT("kickme")
@CMD.DEV_CMD("kickme")
@CMD.FAKEDEV("kickme")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    status = None
    if chat_id in BLACKLIST_GCAST:
        return await proses.edit(f"{em.gagal}**Sorry, you cant leave this group!**")
    try:
        chat_id = int(chat_id)
    except ValueError:
        chat_id = str(chat_id)
    try:
        chat_member = await client.get_chat_member(chat_id, "me")
        if chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR:
            status = "admin"
        elif chat_member.status == enums.ChatMemberStatus.OWNER:
            status = "owner"
        elif chat_member.status == enums.ChatMemberStatus.MEMBER:
            status = "member"
    except Exception as er:
        return await proses.edit(f"{em.gagal}**Error:** {str(er)}")
    if status in ["admin", "owner"]:
        return await proses.edit(
            f"{em.gagal}**Sorry you cant leave this chat because you as: {status} in this chat.!**"
        )
    else:
        return await client.leave_chat(chat_id)
        # return await proses.edit(f"{em.sukses}**Succesfully leave chat: {chat_id}**!")


@CMD.UBOT("leave")
@CMD.DEV_CMD("leave")
@CMD.FAKEDEV("leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    no_leave = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    no_leave.append(-1001818398503)
    no_leave.append(-1001537280879)
    if len(message.command) < 2 and message.command not in [
        "group",
        "channel",
        "global",
        "mute",
    ]:
        return await proses.edit(
            f"{em.gagal}**Please specify command!**\n**Example: `{message.text.split()[0]}` [group, channel, mute or global].**"
        )
    command = message.text.split()[1]
    if command == "mute":
        sukses = await leave_mute(client)
        await proses.delete()
        return await message.reply(
            f"{em.sukses}**Succesfully leaved muted group, succesed: {sukses}**"
        )
    sukses = 0
    arg = 0
    chats = await client.get_chat_id(command)
    for chat in chats:
        if chat in no_leave:
            continue
        try:
            chat_info = await client.get_chat_member(chat, "me")
            user_status = chat_info.status
            if user_status not in (
                enums.ChatMemberStatus.OWNER,
                enums.ChatMemberStatus.ADMINISTRATOR,
            ):
                sukses += 1
                await client.leave_chat(chat)
        except FloodWait as e:
            await asyncio.sleep(e)
            await client.leave_chat(chat)
            sukses += 1
        except Exception:
            arg += 1
    await proses.delete()
    return await message.reply(
        f"{em.sukses}**Succesfully leave {command}, succesed: {sukses} failed: {arg}.**"
    )


@CMD.UBOT("bl-leave")
@CMD.DEV_CMD("bl-leave")
@CMD.FAKEDEV("bl-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    blacklist = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await proses.edit(
            "{}<b>KONTOL KALO PAKE NONE PREFIX JANGAN ASAL KETIK GOBLOK\n\nBOT GW YANG EROR ANJ!!!</b>".format(
                em.gagal
            )
        )
    if chat_id in blacklist:
        return await proses.edit(
            f"{em.sukses}**{chat_id} Already in database blacklist leave!**"
        )
    await dB.add_to_var(client.me.id, "NO_LEAVE", chat_id)
    return await proses.edit(
        f"{em.sukses}**Added {chat_id} to database blacklist leave.**"
    )


@CMD.UBOT("unbl-leave")
@CMD.DEV_CMD("unbl-leave")
@CMD.FAKEDEV("unbl-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    blacklist = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    try:
        chat_id = (
            int(message.command[1]) if len(message.command) > 1 else message.chat.id
        )
        if chat_id not in blacklist:
            return await proses.edit(
                f"{em.gagal}**{chat_id} Not in database blacklist leave!**"
            )
        await dB.remove_from_var(client.me.id, "NO_LEAVE", chat_id)
        return await proses.edit(
            f"{em.sukses}**Removed {chat_id} from database blacklist leave.**"
        )
    except Exception as error:
        return await proses.edit(str(error))


@CMD.UBOT("getbl-leave")
@CMD.DEV_CMD("getbl-leave")
@CMD.FAKEDEV("getbl-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    msg = f"{em.sukses} List blacklist leave:\n\n"
    listbc = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    for num, x in enumerate(listbc, 1):
        try:
            get = await client.get_chat(x)
            msg += f"{num}. {get.title} - {get.id}\n"
        except Exception:
            msg += f"{num}. {x}\n"
    await proses.delete()
    return await message.reply(msg)


@CMD.UBOT("cleardb-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    get_bls = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    if not get_bls:
        return await proses.edit(f"{em.gagal}**You dont have blacklist leave!**")
    for x in get_bls:
        await dB.remove_from_var(client.me.id, "NO_LEAVE", x)
    return await proses.edit(
        f"{em.sukses}**Succesfully removed all group in blacklist leave!**"
    )


async def leave_mute(client):
    sukses = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(dialog.chat.id, client.me.id)
                if member.status == enums.ChatMemberStatus.RESTRICTED:
                    sukses += 1
                    await client.leave_chat(dialog.chat.id)
            except FloodWait as e:
                await asyncio.sleep(e)
                await client.leave_chat(dialog.chat.id)
                sukses += 1
            except Exception:
                continue
    return sukses
