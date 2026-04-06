from Navy import bot, navy
from pyrogram import enums, errors
import asyncio
import random
import time
import traceback
from config import API_BOTCHAX, BLACKLIST_KATA, BOT_ID
from Navy.database import dB
from Navy.helpers import CMD, MessageFilter, Tools, task, get_cached_list, reply_same_type, url_mmk

__MODULES__ = "ᴄʜᴀᴛʙᴏᴛ"
__HELP__ = """<blockquote>Command Help **chatbot**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can turned on chatbot in group chat**
        `{0}chatbot` (on)
    **You can turned off chatbot in group chat**
        `{0}chatbot` (off)
    **You can turned on chatbot from admins in group chat**
        `{0}chatbot admin` (on)
    **You can turned off chatbot from admins in group chat**
        `{0}chatbot admin` (off)
    **You can turned on chatbot for allchats if someone reply your messages**
        `{0}chatbot reply` (on)
    **You can turned off chatbot for allchats if someone reply your messages**
        `{0}chatbot reply` (off)
    **You can ignore chatbot for user in group chat**
        `{0}chatbot ignore` (userID/reply user)
    **You can reignore chatbot for user  in group chat**
        `{0}chatbot reignore` (userID/reply user)
    **You can check status on database**
        `{0}chatbot` (status)
    **You can set role for chatbot**
        `{0}chatbot` (role)

**Note:** This feature will work if someone replies to your message.</blockquote>
<b>   {1}</b>
"""




userbot_ids = set()
blacklisted_chats = set()
validator = MessageFilter()
SEMAPHORE = asyncio.Semaphore(10)
last_msg_cache = {}
message_queue = {}
processed_messages = set()

TEXT_ROLE = """lu adalah manusia dengan karakter toxic. serta balaslah pesan menggunakan huruf kecil disemua teks dan balaslah pesan 1 patah, 2 patah atau 3 patah kata saja."""

DEFAULT_ROLE = """lu adalah manusia dengan karakter toxic. serta balaslah pesan menggunakan huruf kecil disemua teks dan balaslah pesan satu patah, dua patah, tiga patah sampai empat patah kata saja.

aturan khusus:
kalau ada yang ngomong "ubot" atau "userbot" atau "yubot"
balas:
"ubot gacor ga? ubot yang gacor cuma di @starbotdevs"

kalau ada yang ngomong "bot"
balas:
"bot pala lu" atau "bukan bot ka" atau "najis bgt"

kalau ada yang ngomong "uno"
balas:
"kayak jago aja."

kalau ada yang ngomong "mole" atau "emel"
balas:
"lu aja nub lol"

kalau ada yang ngomong "demus"
balas:
"lonli bgt demus di tele"

kalau ada yang ngomong "sfs" atau "espies" atau "esfies"
balas:
"nihh subs ch orang ganteng @quotedamn"

kalau ada yang ngomong "os"
balas:
"os disini aja njir"

kalau ada yang ngomong "opmin"
balas:
"disini juga opmin 😎"

kalau ada ngomong "wen" atau "when ya" atau "wen ya" atau "wen ia"
balas :
"wen wen"

selain dari itu balaslah pesan se toxic mungkin satu patah, dua patah atau tiga patah kata saja.
"""

async def gen_text(client, message):
    text = (message.text or message.caption).strip()
    if not text:
        return

    role = await dB.get_var(client.me.id, "ROLE_CHATBOT") or DEFAULT_ROLE

    from urllib.parse import quote
    text = quote(f"{role}\n\nuser: {text}")

    API_URL = f"https://api.botcahx.eu.org/api/search/gpt?text={text}&apikey={API_BOTCHAX}"

    try:
        res = await Tools.fetch.get(API_URL)
        if res.status_code == 200:
            result = res.json().get("message")
            if not result:
                return None
            return result
    except Exception:
        return None


async def get_random_text():
    # Hapus dulu CHATBOT_TEXT
    await dB.remove_var(BOT_ID, "CHATBOT_TEXT")

    # Baru ambil ulang dari DB
    return await dB.get_var(BOT_ID, "CHATBOT_TEXT") or []


async def add_auto_text(text):
    auto_text = await get_random_text()
    auto_text.append(text)
    await dB.set_var(BOT_ID, "CHATBOT_TEXT", auto_text)


@CMD.UBOT("chatbot")
async def chatbot_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply(
            f"<b>Usage: `{message.text.split()[0]} on | off | status | role | ignoreadmin | reignoreadmin`</b>"
        )

    cmd = message.command[1].lower()

    if cmd == "on":
        if message.chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
            return await message.reply("<b>Please enable in group.</b>")
        if message.chat.id in await dB.get_list_from_var(client.me.id, "CHATBOT"):
            return await message.reply(f"**Chat already in database.**")
        await dB.add_to_var(client.me.id, "CHATBOT", message.chat.id)
        return await message.reply(f"<b> Chatbot turned on in this group.</b>")

    elif cmd == "off":
        if len(message.command) < 3:
            if message.chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
                return await message.reply("<b>Please enable in group.</b>")
            chat_id = message.chat.id
            if chat_id not in await dB.get_list_from_var(client.me.id, "CHATBOT"):
                return await message.reply(f"**`{chat_id}` is not found!**")
            await dB.remove_from_var(client.me.id, "CHATBOT", chat_id)
            name = (await client.get_chat(chat_id)).title
            return await message.reply(f"<b>Turned off chatbot for chat: {name}</b>")
        else:
            if message.command[2] == "all":
                for cid in await dB.get_list_from_var(client.me.id, "CHATBOT"):
                    await dB.remove_from_var(client.me.id, "CHATBOT", cid)
                return await message.reply(f"<b>All chatbot group lists cleared.</b>")
            else:
                try:
                    chat_id = int(message.command[2])
                except ValueError:
                    return await message.reply(
                        f"**Invalid chat ID `{message.command[2]}`.**"
                    )
                if chat_id not in await dB.get_list_from_var(client.me.id, "CHATBOT"):
                    return await message.reply(f"`{chat_id}` **Not found!**")
                await dB.remove_from_var(client.me.id, "CHATBOT", chat_id)
                name = (await client.get_chat(chat_id)).title
                return await message.reply(
                    f"<b>Turned off chatbot for chat: {name}</b>"
                )
    elif cmd == "status":
        chats = await dB.get_list_from_var(client.me.id, "CHATBOT")
        if not chats:
            return await message.reply(f"<b>No active groups using chatbot.</b>")
        msg = ""
        for i, chat_id in enumerate(chats, 1):
            try:
                chat = await client.get_chat(chat_id)
                msg += f"<b>{i}. {chat.title} | `{chat.id}`</b>\n"
            except Exception:
                continue
        return await message.reply(msg or f"<b>All active groups inaccessible.</b>")

    elif cmd == "role":
        if not message.reply_to_message:
            return await message.reply(
                f"<b>Usage: reply to a message → `{message.text.split()[0]} role`</b>"
            )
        role = message.reply_to_message.text or message.reply_to_message.caption
        await dB.set_var(client.me.id, "ROLE_CHATBOT", role)
        return await message.reply(f"<b>Role set to:</b> <code>{role}</code>")

    elif cmd == "ignore":
        reply = message.reply_to_message
        try:
            target = reply.from_user.id if reply else message.text.split()[2]
        except (AttributeError, IndexError):
            return await message.reply(
                f"<b>You need to specify a user (either by reply or username/ID)!</b>"
            )
        try:
            user = await client.get_users(target)
        except (
            errors.PeerIdInvalid,
            KeyError,
            errors.UsernameInvalid,
            errors.UsernameNotOccupied,
        ):
            return await message.reply(f"<b>You need meet before interact!!</b>")
        user_id = user.id
        if user_id in await dB.get_list_from_var(client.me.id, "CHATBOT_IGNORE"):
            return await message.reply(f"**User already ignored chatbot.**")
        await dB.add_to_var(client.me.id, "CHATBOT_IGNORE", user_id)
        return await message.reply(
            f"<b>Chatbot will now ignore {user_id} in this group.</b>"
        )
    elif cmd == "reignore":
        reply = message.reply_to_message
        try:
            target = reply.from_user.id if reply else message.text.split()[2]
        except (AttributeError, IndexError):
            return await message.reply(
                f"<b>You need to specify a user (either by reply or username/ID)!</b>"
            )
        try:
            user = await client.get_users(target)
        except (
            errors.PeerIdInvalid,
            KeyError,
            errors.UsernameInvalid,
            errors.UsernameNotOccupied,
        ):
            return await message.reply(f"<b>You need meet before interact!!</b>")
        user_id = user.id
        if user_id not in await dB.get_list_from_var(client.me.id, "CHATBOT_IGNORE"):
            return await message.reply(f"**User not found in database.**")

        await dB.remove_from_var(client.me.id, "CHATBOT_IGNORE_ADMIN", user_id)
        return await message.reply(
            f"<b>Chatbot will now respond {user_id} again in this group.</b>"
        )
    elif cmd == "admin":
        if len(message.command) < 3:
            return await message.reply(f"**Please give query on or off.**")
        query = message.text.split()[2]
        if query.lower() == "on":
            if await dB.get_var(client.me.id, "CHATBOT_ADMIN"):
                await dB.remove_var(client.me.id, "CHATBOT_ADMIN")
                return await message.reply(
                    f"**Chatbot will respond message from admins now.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot respond from admins already enable.**"
                )
        elif query.lower() == "off":
            if not await dB.get_var(client.me.id, "CHATBOT_ADMIN"):
                await dB.set_var(client.me.id, "CHATBOT_ADMIN", True)
                return await message.reply(
                    f"**Chatbot will pass message from admins now.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot respond from admins already disable.**"
                )
        else:
            return await message.reply(f"**Please give query on or off.**")
    elif cmd == "reply":
        if len(message.command) < 3:
            return await message.reply(f"**Please give query on or off.**")
        query = message.text.split()[2]
        if query.lower() == "on":
            if not await dB.get_var(client.me.id, "CHATBOT_REPLY"):
                await dB.set_var(client.me.id, "CHATBOT_REPLY", True)
                return await message.reply(
                    f"**Chatbot will respond all chats if someone reply your messages.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot reply user for all chats already enable.**"
                )
        elif query.lower() == "off":
            if await dB.get_var(client.me.id, "CHATBOT_REPLY"):
                await dB.remove_var(client.me.id, "CHATBOT_REPLY")
                return await message.reply(
                    f"**Chatbot reply user for all chats disable.**"
                )
            else:
                return await message.reply(
                    f"**Chatbot reply user for all chats already disable.**"
                )
        else:
            return await message.reply(f"**Please give query on or off.**")

    else:
        return await message.reply(
            f"<b>Usage: `{message.text.split()[0]} on | off | status | role | ignoreadmin | reignoreadmin`</b>"
        )


@CMD.NO_CMD("CHATBOT", navy)
async def auto_reply_trigger(client, message):
    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    if message.from_user.id in client._get_my_id:
        return

    text = message.text or message.caption
    if (
        message.reply_to_message
        and (message.reply_to_message.from_user or message.reply_to_message.sender_chat)
        and (
            message.reply_to_message.from_user or message.reply_to_message.sender_chat
        ).id
        == client.me.id
    ):
        if await dB.get_var(client.me.id, "CHATBOT_REPLY"):
            if text:
                for word in BLACKLIST_KATA:
                    if word in text:
                        return
                if url_mmk(text) or validator.is_text_abnormal(text):
                    return
                await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
                response = await gen_text(client, message)

                if response:
                    try:
                        await message.reply(response)
                        await add_auto_text(response)
                    except errors.FloodWait as e:
                        await asyncio.sleep(e.value)
                        await message.reply(response)
                        await add_auto_text(response)
                else:
                    fallback = await get_random_text()
                    if fallback:
                        await message.reply(random.choice(fallback))

                return await client.send_chat_action(
                    message.chat.id, enums.ChatAction.CANCEL
                )
            else:
                return await reply_same_type(message)
    elif client.me.username and (
        (message.text and client.me.username in message.text)
        or (message.caption and client.me.username in message.caption)
    ):
        if not await dB.get_var(client.me.id, "CHATBOT_REPLY"):
            return
        mention = message.from_user.mention()
        caption_text = (message.caption or "").replace(client.me.username, mention)
        if message.text:
            for word in BLACKLIST_KATA:
                if word in text:
                    return
            if url_mmk(text) or validator.is_text_abnormal(text):
                return
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            response = await gen_text(client, message)

            if response:
                try:
                    await message.reply(response)
                    await add_auto_text(response)
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await message.reply(response)
                    await add_auto_text(response)
            else:
                fallback = await get_random_text()
                if fallback:
                    await message.reply(random.choice(fallback))

            return await client.send_chat_action(
                message.chat.id, enums.ChatAction.CANCEL
            )
        else:
            return await reply_same_type(message, mention_text=caption_text)