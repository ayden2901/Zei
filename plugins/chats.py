import asyncio

from pyrogram import raw
from pyrogram.errors import FloodWait, PeerIdInvalid

from Navy.helpers import CMD, Emoji

__MODULES__ = "ᴄʜᴀᴛs"
__HELP__ = """<blockquote>Command Help **Chats**</blockquote>

<blockquote>**Clear chat user in group** </blockquote>
    **You can delete all message user from chat**
        `{0}cc` (username/reply user)

<blockquote>**Endchat all bot** </blockquote>
    **You can clear all history chat from bot**
        `{0}endchat bot`

<blockquote>**Endchat all users**</blockquote> 
    **You can clear all history chat from private messages**
        `{0}endchat private`

<blockquote>**Endchat all bot and users** </blockquote>
    **This command will clear all history chat from bot and private messages**
        `{0}endchat all`

<blockquote>**Endchat user**</blockquote> 
    **You can clear history chat from target**
        `{0}endchat` (username/reply user)

<blockquote>**Create a channel**</blockquote>
    **You can create a channel with this command**
        `{0}create ch`

<blockquote>**Create a group**</blockquote> 
    **You can create a super group with this command**
        `{0}create gc`

<blockquote>**Create invite chat link** </blockquote>
    **You can get invite link chats**
        `{0}getlink`

<blockquote>**Get total member chat**</blockquote> 
    **Check total members from chat**
        `{0}cekmember`

<blockquote>**Get online member chat**</blockquote> 
    **Get online members from chat**
        `{0}cekonline`

<blockquote>**Check message count user**</blockquote> 
    **Get total messages user from chat**
        `{0}cekmsg` (username/reply user)
    
<b>   {1}</b>
"""


@CMD.UBOT("cc")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        aan = await message.reply_text(f"{em.gagal}**Please reply to valid user_id!**")
        await asyncio.sleep(0.5)
        return await aan.delete()
    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        aa = await message.reply_text(
            f"{em.gagal}**Please reply to user or give username!**"
        )
        await asyncio.sleep(0.5)
        return await aa.delete()
    await message.delete()
    try:
        return await client.delete_user_history(message.chat.id, user)
    except Exception:
        pass


@CMD.UBOT("endchat")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    query = ["bot", "private", "all"]
    if len(message.command) < 2 and not reply:
        return await proses.edit(f"{em.gagal}**Please give query or username!**")
    if len(message.command) == 1 and reply:
        who = reply.from_user.id
        try:
            info = await client.resolve_peer(who)
            await client.invoke(
                raw.functions.messages.DeleteHistory(peer=info, max_id=0, revoke=True)
            )
        except PeerIdInvalid:
            pass
        await message.reply(f"{em.sukses}<b>Succesfully endchat: {who}</b>")
    elif message.command[1] in query:
        target = await client.get_chat_id(message.command[1])
        for ids in target:
            try:
                info = await client.resolve_peer(ids)
                await client.invoke(
                    raw.functions.messages.DeleteHistory(
                        peer=info, max_id=0, revoke=True
                    )
                )
            except PeerIdInvalid:
                continue
            except FloodWait as e:
                await asyncio.sleep(e.value)
                info = await client.resolve_peer(ids)
                await client.invoke(
                    raw.functions.messages.DeleteHistory(
                        peer=info, max_id=0, revoke=True
                    )
                )
        await message.reply(
            f"{em.sukses}**Succesfully endchat: `{message.command[1]}`, total: `{len(target)}`**"
        )
    else:
        who = message.text.split()[1]
        try:
            info = await client.resolve_peer(who)
            await client.invoke(
                raw.functions.messages.DeleteHistory(peer=info, max_id=0, revoke=True)
            )
        except PeerIdInvalid:
            pass
        await message.reply(f"{em.sukses}<b>Succesfully endchat: {who}</b>")
    return await proses.delete()


@CMD.UBOT("create")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    if len(message.command) < 3:
        return await message.reply(
            f"{em.gagal}<b>Please `{message.text.split()[0]}` `gc` to create a group, or `ch` to create a channel.</b>"
        )
    group_type = message.command[1]
    split = message.command[2:]
    group_name = " ".join(split)
    proses = await message.reply(f"{em.proses}**{proses_}**")
    args = ["gc", "ch"]
    if message.command[1] not in args:
        return await proses.edit(
            f"{em.gagal}<b>Please `{message.text.split()[0]}` `gc` to create a group, or `ch` to create a channel.</b>"
        )
    try:
        desc = "Welcome To My " + ("Group" if group_type == "gc" else "Channel")
        if group_type == "gc":
            _id = await client.create_supergroup(group_name, desc)
            link = await client.get_chat(_id.id)
            return await proses.edit(
                f"{em.sukses}<b>Succesfully created group: [{group_name}]({link.invite_link})</b>",
                disable_web_page_preview=True,
            )
        elif group_type == "ch":
            _id = await client.create_channel(group_name, desc)
            link = await client.get_chat(_id.id)
            return await proses.edit(
                f"{em.sukses}<b>Succesfully created channel: [{group_name}]({link.invite_link})</b>",
                disable_web_page_preview=True,
            )
    except Exception as err:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(err)}")


@CMD.UBOT("getlink")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_}**")
    chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
    try:
        link = await client.export_chat_invite_link(chat_id)
        return await proses.edit(
            f"{em.sukses}**This is invite link: {chat_id}\n\n{link}",
            disable_web_page_preview=True,
        )
    except Exception as er:
        return await proses.edit(f"{em.gagal}**ERROR:** `{str(er)}`")


@CMD.UBOT("cekmember")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_}**")
    try:
        member_count = await client.get_chat_members_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(
            f"{em.sukses}**Total members in group: {chat_id} is `{member_count}` members.**"
        )
    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")


@CMD.UBOT("cekonline")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_}**")
    try:
        member_online = await client.get_chat_online_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(
            f"{em.sukses}**Total members online in group: {chat_id} is `{member_online}` members.**"
        )
    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")


@CMD.UBOT("cekmsg")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    chat_id = message.chat.id
    user_id = None

    if len(message.command) > 1:
        chat_id = message.command[1] if message.command[1].isdigit() else chat_id
        user_id = message.command[2] if len(message.command) > 2 else message.command[1]
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

    if not user_id:
        return await message.reply_text(
            f"{em.gagal}**Please reply to a user or provide a username/ID!**"
        )

    try:
        user = await client.get_users(user_id)
        umention = user.mention
    except (PeerIdInvalid, KeyError):
        return await message.reply_text(
            f"{em.gagal}**Error: PeerIdInvalid or invalid user ID/username.**"
        )

    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_}**")

    try:

        total_msg = await client.search_messages_count(chat_id, from_user=user.id)
        await asyncio.sleep(1)
        await proses.edit(
            f"{em.sukses}**Total messages by {umention} in chat `{chat_id}`: `{total_msg}` messages.**"
        )
    except Exception as e:
        await proses.edit(f"{em.gagal}**Error:** `{str(e)}`")
