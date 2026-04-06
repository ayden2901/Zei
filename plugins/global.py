import asyncio
from io import BytesIO

from pyrogram.errors import (FloodWait, PeerIdInvalid, UsernameInvalid,
                             UsernameNotOccupied)
from pyrogram.raw.functions.messages import DeleteHistory
from pyrogram.types import ChatPermissions

from config import DEVS, BOT_ID, OWNER_ID, KYNAN
from Navy import bot, navy
from Navy.database import dB
from Navy.helpers import CMD, Emoji, task, animate_proses, Tools

__MODULES__ = "ɢʟᴏʙᴀʟ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ɢʟᴏʙᴀʟ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ɢʟᴏʙᴀʟ ʙᴀɴɴᴇᴅ</b>
    ➢ `{0}gban` [ᴜsᴇʀɴᴀᴍᴇ]
    ➢ `{0}ungban` [ᴜsᴇʀɴᴀᴍᴇ]</blockquote>
<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ɢʟᴏʙᴀʟ ᴍᴜᴛᴇ</b>
    ➢ `{0}gmute` [ᴜsᴇʀɴᴀᴍᴇ]
    ➢ `{0}ungmute` [ᴜsᴇʀɴᴀᴍᴇ]</blockquote>
<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ʟɪsᴛ ɢʟᴏʙᴀʟ</b>
    ➢ `{0}gbanlist`
    ➢ `{0}gmutelist`</blockquote>

<b>   {1}</b>
"""

async def gban_cmd(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    db_id = BOT_ID if client.me.is_bot else client.me.id

    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await proses.edit(
            f"{em.gagal}<b>You need to specify a user to gban (either by reply or username/ID)!</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await proses.edit(f"{em.gagal}<b>You need meet before interact!!</b>")
    mention = user.mention
    user_id = user.id
    if user_id == client.me.id:
        return await proses.edit(f"{em.gagal}<b>Go to the heal now!!</b>")
    if user_id in DEVS:
        try:
            await client.send_message(
                user_id, "<b>I try to do global banned your account!!</b>"
            )
            return await proses.edit(
                f"{em.gagal}<b>User: {user_id}|{mention} is a developer!!</b>"
            )
        except Exception:
            pass
    await proses.edit(
        f"{em.proses}<i>Task gban running #<code>{task_id}</code>. "
        f"Type <code>{prefix[0]}cancel {task_id}</code> to cancel gbanned!</i>"
    )
    done = 0
    fail = 0
    if client.me.is_bot:
        chats = await dB.get_list_from_var(BOT_ID, "GROUPS") or []
    else:
        chats = await client.get_chat_id("global")
    db_gban = await dB.get_list_from_var(db_id, "GBANNED")
    try:
        for chat in chats:
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}Gbanned cancelled.")
            if user_id in db_gban:
                await proses.edit(f"{em.gagal}<b>User already in gbanned</b>")
                return
            try:
                await client.ban_chat_member(chat, user_id)
                done += 1
                await asyncio.sleep(0.1)
            except Exception:
                fail += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                await client.ban_chat_member(chat, user_id)
                done += 1
                await asyncio.sleep(0.1)
    finally:
        task.end_task(task_id)

    await dB.add_to_var(db_id, "GBANNED", user_id)

    try:
        if not client.me.is_bot:
            await client.block_user(user_id)
    except Exception:
        pass

    try:
        if not client.me.is_bot:
            solve = await client.resolve_peer(user_id)
            await client.invoke(DeleteHistory(peer=(solve), max_id=0, revoke=True))
    except Exception:
        pass

    teks = f"""
<blockquote expandable><b>{em.warn}#GBANNED</b>
<b>{em.sukses}Success: {done}</b>
<b>{em.gagal}Failed: {fail}</b>
<b>{em.proses}Type: {message.command[0]}</b>
<b>{em.robot}Task ID: `{task_id}`</b>
<b>{em.profil}User: {mention}</b>
"""
    await proses.delete()
    try:
        return await message.reply(teks)
    except Exception as e:
        if "CHAT_SEND_PLAIN_FORBIDDEN" in str(e):
            from io import BytesIO
            bio = BytesIO(b"0")
            bio.name = "navy.jpg"
            return await message.reply_photo(bio, caption=teks)
        else:
            raise


async def ungban_cmd(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    db_id = BOT_ID if client.me.is_bot else client.me.id

    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await proses.edit(
            f"{em.gagal}<b>You need to specify a user to ungban (either by reply or username/ID)!</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await proses.edit(f"{em.gagal}<b>You need meet before interact!!</b>")
    mention = user.mention
    user_id = user.id
    await proses.edit(
        f"{em.proses}<i>Task ungban running #<code>{task_id}</code>. "
        f"Type <code>{prefix[0]}cancel {task_id}</code> to cancel ungbanned!</i>"
    )
    done = 0
    fail = 0
    if client.me.is_bot:
        chats = await dB.get_list_from_var(BOT_ID, "GROUPS") or []
    else:
        chats = await client.get_chat_id("global")
    db_gban = await dB.get_list_from_var(db_id, "GBANNED")
    try:
        for chat in chats:
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}UnGbanned cancelled.")
            if user_id not in db_gban:
                await proses.edit(f"{em.gagal}<b>User has not gbanned</b>")
                return
            try:
                await client.unban_chat_member(chat, user_id)
                done += 1
                await asyncio.sleep(0.1)
            except Exception:
                fail += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                await client.unban_chat_member(chat, user_id)
                done += 1
                await asyncio.sleep(0.1)
    finally:
        task.end_task(task_id)

    await dB.remove_from_var(db_id, "GBANNED", user_id)

    try:
        if not client.me.is_bot:
            await client.unblock_user(user_id)
    except Exception:
        pass

    teks = f"""
<blockquote expandable><b>{em.warn}#UNGBANNED</b>
<b>{em.sukses}Success: {done}</b>
<b>{em.gagal}Failed: {fail}</b>
<b>{em.proses}Type: {message.command[0]}</b>
<b>{em.robot}Task ID: `{task_id}`</b>
<b>{em.profil}User: {mention}</b>
"""
    await proses.delete()
    return await message.reply(teks)


async def gbanlist_cmd(client, message):
    em = Emoji(client)
    await em.get()

    db_id = BOT_ID if client.me.is_bot else client.me.id
    db_gban = await dB.get_list_from_var(db_id, "GBANNED")

    proses = await animate_proses(message, em.proses)
    if not db_gban:
        return await proses.edit(f"{em.gagal}<b>There are no users yet!</b>")
    teks = f"    Users \n"
    for num, user in enumerate(db_gban, 1):
        teks += f"│ {num}. {em.warn} {user}\n"
    try:
        await message.reply_text(teks)
    except Exception:
        await proses.edit(f"{em.proses}<b>Message too long, try to send document!</b>")
        with BytesIO(str.encode(teks)) as f:
            f.name = "gbanlist.txt"
            await message.reply_document(
                document=f, caption="<b>Here list of users</b>"
            )
    return await proses.delete()


async def gmute_cmd(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    db_id = BOT_ID if client.me.is_bot else client.me.id

    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await proses.edit(
            f"{em.gagal}<b>You need to specify a user to gmute (either by reply or username/ID)!</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)

    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await proses.edit(f"{em.gagal}<b>You need meet before interact!!</b>")

    mention = user.mention
    user_id = user.id
    if user_id == client.me.id:
        return await proses.edit(f"{em.gagal}<b>Go to the heal now!!</b>")
    if user_id in DEVS:
        try:
            await client.send_message(
                user_id, "<b>I try to do global mute your account!!</b>"
            )
            return await proses.edit(
                f"{em.gagal}<b>User: {user_id}|{mention} is a developer!!</b>"
            )
        except Exception:
            pass
    await proses.edit(
        f"{em.proses}<i>Task gmute running #<code>{task_id}</code>. "
        f"Type <code>{prefix[0]}cancel {task_id}</code> to cancel gmuted!</i>"
    )
    done = 0
    fail = 0
    if client.me.is_bot:
        chats = await dB.get_list_from_var(BOT_ID, "GROUPS") or []
    else:
        chats = await client.get_chat_id("group")
    db_gmute = await dB.get_list_from_var(db_id, "GMUTE")
    try:
        for chat in chats:
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}Gmuted cancelled.")
            if user_id in db_gmute:
                await proses.edit(f"{em.gagal}<b>User already gmuted</b>")
                return
            try:
                await client.restrict_chat_member(chat, user_id, ChatPermissions())
                done += 1
                await asyncio.sleep(0.1)
            except Exception:
                fail += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                await client.restrict_chat_member(chat, user_id, ChatPermissions())
                done += 1
                await asyncio.sleep(0.1)
    finally:
        task.end_task(task_id)

    await dB.add_to_var(db_id, "GMUTE", user_id)

    teks = f"""
<blockquote expandable><b>{em.warn}#GMUTED</b>
<b>{em.sukses}Success: {done}</b>
<b>{em.gagal}Failed: {fail}</b>
<b>{em.msg}Type: {message.command[0]}</b>
<b>{em.robot}Task ID: `{task_id}`</b>
<b>{em.profil}User: {mention}</b>
"""
    await proses.delete()
    return await message.reply(teks)


async def ungmute_cmd(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses = await animate_proses(message, em.proses)
    db_id = BOT_ID if client.me.is_bot else client.me.id

    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await proses.edit(
            f"{em.gagal}<b>You need to specify a user to ungmute (either by reply or username/ID)!</b>"
        )
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)

    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await proses.edit(f"{em.gagal}<b>You need meet before interact!!</b>")
    mention = user.mention
    user_id = user.id
    await proses.edit(
        f"{em.proses}<i>Task ungmute running #<code>{task_id}</code>. "
        f"Type <code>{prefix[0]}cancel {task_id}</code> to cancel ungmuted!</i>"
    )
    done = 0
    fail = 0
    if client.me.is_bot:
        chats = await dB.get_list_from_var(BOT_ID, "GROUPS") or []
    else:
        chats = await client.get_chat_id("group")
    db_gmute = await dB.get_list_from_var(db_id, "GMUTE")
    try:
        for chat in chats:
            if not task.is_active(task_id):
                return await proses.edit(f"{em.gagal}Ungmuted cancelled.")
            if user_id not in db_gmute:
                await proses.edit(f"{em.gagal}<b>User has not gmuted</b>")
                return
            try:
                await client.unban_member(chat, user_id, ChatPermissions())
                done += 1
                await asyncio.sleep(0.1)
            except Exception:
                fail += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                await client.unban_member(chat, user_id, ChatPermissions())
                done += 1
                await asyncio.sleep(0.1)
    finally:
        task.end_task(task_id)

    await dB.remove_from_var(db_id, "GMUTE", user_id)

    teks = f"""
<blockquote expandable><b>{em.warn}#UNGMUTED</b>
<b>{em.sukses}Success: {done}</b>
<b>{em.gagal}Failed: {fail}</b>
<b>{em.msg}Type: {message.command[0]}</b>
<b>{em.robot}Task ID: `{task_id}`</b>
<b>{em.profil}User: {mention}</b>
"""
    await proses.delete()
    return await message.reply(teks)


async def gmutelist_cmd(client, message):
    em = Emoji(client)
    await em.get()

    db_id = BOT_ID if client.me.is_bot else client.me.id
    db_gban = await dB.get_list_from_var(db_id, "GMUTE")

    proses = await animate_proses(message, em.proses)
    if not db_gban:
        return await proses.edit(f"{em.gagal}<b>There are no users yet!</b>")
    teks = f"    Users \n"
    for num, user in enumerate(db_gban, 1):
        teks += f"│ {num}. {em.warn} {user}\n"
    try:
        await message.reply_text(teks)
    except Exception:
        await proses.edit(f"{em.proses}<b>Message too long, try to send document!</b>")
        with BytesIO(str.encode(teks)) as f:
            f.name = "gmutelist.txt"
            await message.reply_document(
                document=f, caption="<b>Here list of users</b>"
            )
    return await proses.delete()

async def clean_gban(client, message):
    db_id = BOT_ID if client.me.is_bot else client.me.id

    raw = await dB.get_var(db_id, "GBANNED")
    if not raw:
        return await message.reply("No data found.")

    try:
        # jika tersimpan sebagai list python
        if str(raw).startswith("["):
            data = eval(str(raw))
        else:
            data = [int(x) for x in str(raw).split()]

        unique = list(set(int(x) for x in data))
        fixed_format = " ".join(str(x) for x in unique)

        await dB.set_var(db_id, "GBANNED", fixed_format)

        await message.reply(f"Cleaned. Total now: {len(unique)}")

    except Exception as e:
        await message.reply(f"Error repairing DB: {e}")

# ==============UBOT HANDLER===============

@CMD.UBOT("gban")
@CMD.DEV_CMD("gban")
@CMD.FAKEDEV("gban")
async def ubot_gban(client, message):
    await gban_cmd(client, message)

@CMD.UBOT("ungban")
@CMD.DEV_CMD("ungban")
@CMD.FAKEDEV("ungban")
async def ubot_ungban(client, message):
    await ungban_cmd(client, message)

@CMD.UBOT("gmute")
@CMD.DEV_CMD("gmute")
@CMD.FAKEDEV("gmute")
async def ubot_gmute(client, message):
    await gmute_cmd(client, message)

@CMD.UBOT("ungmute")
@CMD.DEV_CMD("ungmute")
@CMD.FAKEDEV("ungmute")
async def ubot_ungmute(client, message):
    await ungmute_cmd(client, message)

@CMD.UBOT("gbanlist")
@CMD.DEV_CMD("gbanlist")
@CMD.FAKEDEV("gbanlist")
async def ubot_gbanlist(client, message):
    await gbanlist_cmd(client, message)

@CMD.UBOT("gmutelist")
@CMD.DEV_CMD("gmutelist")
@CMD.FAKEDEV("gmutelist")
async def ubot_gmutelist(client, message):
    await gmutelist_cmd(client, message)

# ==============BOT HANDLER===============

ALLOWED_USERS = set(DEVS) | set(KYNAN) | {OWNER_ID}

@CMD.BOT("gban")
async def bot_gban(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await gban_cmd(client, message)


@CMD.BOT("ungban")
async def bot_ungban(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await ungban_cmd(client, message)


@CMD.BOT("gmute")
async def bot_gmute(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await gmute_cmd(client, message)


@CMD.BOT("ungmute")
async def bot_ungmute(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await ungmute_cmd(client, message)


@CMD.BOT("gbanlist")
async def bot_gbanlist(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await gbanlist_cmd(client, message)


@CMD.BOT("gmutelist")
async def bot_gmutelist(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await gmutelist_cmd(client, message)


@CMD.BOT("cleangban")
async def bot_clean_gban(client, message):
    if not message.from_user or message.from_user.id not in ALLOWED_USERS:
        return await message.reply("❌ You are not allowed to use this command.")
    await clean_gban(client, message)