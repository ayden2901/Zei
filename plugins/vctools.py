import asyncio
import random

from pyrogram.errors import ChatIdInvalid
from pyrogram.raw import functions
from pyrogram.raw.functions.phone import DiscardGroupCall
from pyrogram.raw.types import InputGroupCall
from pytgcalls.exceptions import (NoActiveGroupCall, NotInCallError)
from Navy.helpers.exceptions import AlreadyJoinedError
from pyrogram.enums import ParseMode, ChatType
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses


__MODULES__ = "ᴠᴄᴛᴏᴏʟs"
__HELP__ = """<blockquote>Command Help **VcTools**</blockquote>

<blockquote>**Start end vc group**</blockquote>
    **Start voice chat group/channel**
        `{0}startvc` 
    **End voice chat group/channel**
        `{0}stopvc`
        
<blockquote>**Join leave vc group**</blockquote>
    **Join voice chat group/channel**
        `{0}joinvc` (chatid)
    **Leave voice chat group/channel**
        `{0}leavevc` (chatid)

<blockquote>**Get listeners vc group**</blockquote>
    **Check listeners from voice chat**
        `{0}listeners`
        
<blockquote>**Change vc title**</blockquote>
    **Edit title voice chat group**
        `{0}vctitle` (title)

<b>   {1}</b>
"""


@CMD.UBOT("startvc")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    args = message.command[1:]

    chat_id = None
    title = None

    if len(args) == 0:
        chat_id = message.chat.id
    elif len(args) == 1:
        if args[0].startswith("@"):
            try:
                chat_id = (await client.get_chat(args[0])).id
            except Exception:
                pros = await animate_proses(message, emo.proses)
                await pros.edit(f"{emo.gagal}<b>Cannot find the group.</b>")
                return await pros.delete(8)
        elif args[0].startswith("-100"):
            chat_id = int(args[0])
        else:
            chat_id = message.chat.id
            title = args[0]

    elif len(args) == 2:
        if args[0].startswith("@"):
            chat_id = (await client.get_chat(args[0])).id
            title = args[1]
        elif args[0].startswith("-100"):
            chat_id = int(args[0])
            title = args[1]
        else:
            try:
                chat_id = int(args[0])
            except ValueError:
                pros = await animate_proses(message, emo.proses)
                await pros.edit(
                    f"{emo.gagal}<b>The first argument is not valid. Please use a valid group ID or username.</b>"
                )
                return await pros.delete(8)
            title = args[1]

    elif (
        len(args) == 2
        and not args[0].startswith("@")
        and not args[0].startswith("-100")
    ):
        chat_id = message.chat.id
        title = args[0]

    if chat_id is None:
        chat_id = message.chat.id

    pros = await animate_proses(message, emo.proses)
    if not pros:
        return

    try:
        chat = await client.get_chat(chat_id)
        chat_title = chat.title
        if title is None:
            title = chat.title
    except Exception:
        chat_title = chat_id
        if title is None:
            title = chat_id

    group_call = await client.get_call(client, chat_id)
    if group_call:
        title = group_call.title if group_call.title else chat_title
        await pros.edit(
            f"{emo.gagal}<b>Voice chat already exists:\n"
            f"{emo.profil}Group: <code>{chat_title}</code>\n"
            f"{emo.warn}Title: <code>{title}</code></b>"
        )
        return await pros.delete(8)

    txt = (
        f"<b>{emo.sukses}Starting Voice Chat:\n"
        f"{emo.profil}Group: <code>{chat_title}</code>\n"
        f"{emo.warn}Title: <code>{title}</code></b>"
    )

    try:
        await client.invoke(
            functions.phone.CreateGroupCall(
                peer=(await client.resolve_peer(chat_id)),
                random_id=random.randint(10000, 999999999),
                title=title,
            )
        )
        await pros.edit(f"{txt}")
        return await pros.delete(8)

    except Exception as e:
        if "CHAT_ADMIN_REQUIRED" in str(e):
            await pros.edit(f"{emo.gagal}<b>You are not an admin!</b>")
            return await pros.delete(8)

        await pros.edit(f"{emo.gagal}<b>Error:</b>\n\n<code>{str(e)}</code>")
        return await pros.delete(8)

@CMD.UBOT("stopvc")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    args = message.command[1:]

    chat_id = None

    if len(args) == 0:
        chat_id = message.chat.id
    elif len(args) == 1:
        if args[0].startswith("@"):
            try:
                chat_id = (await client.get_chat(args[0])).id
            except Exception:
                pros = await animate_proses(message, emo.proses)
                await pros.edit(f"{emo.gagal}<b>Cannot find the chat.</b>")
                return await pros.delete(8)

        elif args[0].startswith("-100"):
            chat_id = int(args[0])
        else:
            chat_id = message.chat.id

    elif (
        len(args) == 1
        and not args[0].startswith("@")
        and not args[0].startswith("-100")
    ):
        chat_id = message.chat.id

    if chat_id is None:
        chat_id = message.chat.id

    pros = await animate_proses(message, emo.proses)
    if not pros:
        return

    try:
        chat = await client.get_chat(chat_id)
        title = chat.title
    except Exception:
        title = chat_id

    group_call = await client.get_call(client, chat_id)

    if not group_call:
        await pros.edit(
            f"{emo.gagal}<b>No Voice Chat:\n{emo.profil}Group: <code>{title}</code></b>"
        )
        return await pros.delete(8)

    try:
        call = InputGroupCall(id=group_call.id, access_hash=group_call.access_hash)
        await client.invoke(DiscardGroupCall(call=call))

        await pros.edit(
            f"{emo.sukses}<b>Stopped Voice Chat:\n{emo.profil}Group: <code>{title}</code>.</b>"
        )
        return await pros.delete(8)

    except Exception as e:
        if "CHAT_ADMIN_REQUIRED" in str(e):
            await pros.edit(f"{emo.gagal}<b>You are not an admin!</b>")
            return await pros.delete(8)

        await pros.edit(
            f"{emo.gagal}<b>Failed to stop Voice Chat:\n"
            f"{emo.profil}Group: <code>{title}</code>\n\n"
            f"<code>{str(e)}</code></b>"
        )
        return await pros.delete(8)

@CMD.UBOT("joinvc|jvc")
@CMD.DEV_CMD("joinvc|jvc")
@CMD.FAKEDEV("joinvc|jvc")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    args = message.chat.id if len(message.command) < 2 else message.text.split(maxsplit=1)[1]
    pros = await animate_proses(message, emo.proses)

    if not pros:
        return

    if isinstance(args, str) and "t.me/+" in args:
        try:
            await client.join_chat(args)
            return await pros.edit(
                f"{emo.sukses}<b>Berhasil join grup, ulangi perintah .jvc</b>"
            )
        except UserAlreadyParticipant:
            pass
        except (InviteHashInvalid, InviteHashExpired):
            return await pros.edit(
                f"{emo.gagal}<b>Link invite tidak valid / expired</b>"
            )

    if isinstance(args, str) and "t.me/" in args:
        args = args.split("t.me/")[1]

    try:
        chat = await client.get_chat(args)
    except ChatIdInvalid:
        return await pros.edit(
            f"{emo.gagal}<b>Link / Username / ID tidak valid</b>"
        )

    if not chat or not chat.id:
        return await pros.edit(
            f"{emo.gagal}<b>Chat tidak ditemukan</b>"
        )

    title = chat.title
    chat_id = chat.id

    group_call = await client.get_call(client, chat_id)
    if not group_call:
        await pros.edit(
            f"{emo.gagal}<b>Voice Chat di <code>{title}</code> belum aktif</b>"
        )
        return await pros.delete(8)

    try:
        await client.group_call.play(chat_id)
        await asyncio.sleep(1)
        await client.group_call.unmute_stream(chat_id)

        await pros.edit(
            f"{emo.sukses}<b>Berhasil join Voice Chat:\n{emo.profil}Group <code>{title}</code></b>"
        )
        return await pros.delete(8)

    except NoActiveGroupCall:
        await pros.edit(
            f"{emo.gagal}<b>Aktifkan dulu Voice Chat di <code>{title}</code></b>"
        )
        return await pros.delete(8)

    except AlreadyJoinedError:
        await pros.edit(
            f"{emo.gagal}<b>Akun sudah berada di Voice Chat</b>"
        )
        return await pros.delete(8)

    except Exception as e:
        await pros.edit(
            f"{emo.gagal}<b>Gagal join VC di:\n"
            f"{emo.profil}Group <code>{title}</code>\n"
            f"Error:\n<code>{e}</code></b>"
        )
        return await pros.delete(8)


@CMD.UBOT("leavevc|lvc")
@CMD.DEV_CMD("leavevc|lvc")
@CMD.FAKEDEV("leavevc|lvc")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    args = message.chat.id if len(message.command) < 2 else message.text.split()[1]
    pros = await animate_proses(message, emo.proses) 

    if not pros:
        return

    try:
        chat = await client.get_chat(args)
    except ChatIdInvalid:
        await pros.edit(
            f"{emo.gagal}<b>Cannot find the Group, please give username or chatid</b>"
        )
        return await pros.delete(8)

    title = chat.title
    chat_id = chat.id

    try:
        await client.group_call.leave_call(chat_id)
        await pros.edit(
            f"{emo.sukses}<b>Successfully left Voice Chat:\n{emo.profil}Group: <code>{title}</code></b>"
        )
        return await pros.delete(8)

    except NotInCallError:
        await pros.edit(
            f"{emo.gagal}<b>Your account is not in the Voice Chat <code>{title}</code></b>"
        )
        return await pros.delete(8)

    except Exception as e:
        await pros.edit(
            f"{emo.gagal}<b>Failed to leave Voice Chat:\n"
            f"{emo.profil}Group: <code>{title}</code>\n"
            f"{emo.block}Error: <code>{e}</code></b>"
        )
        return await pros.delete(8)

@CMD.UBOT("listeners")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await animate_proses(message, emo.proses) 

    if not pros:
        return

    chat = message.command[1] if len(message.command) > 1 else message.chat.id
    try:
        if isinstance(chat, int):
            chat_id = chat
        else:
            chat_info = await client.get_chat(chat)
            chat_id = chat_info.id
        try:
            info = await client.get_chat(chat_id)
            title = info.title if info.title else f"{chat_id}"
        except Exception:
            title = f"{chat_id}"
        group_call = await client.get_call(client, info.id)
        if not group_call:
            return await pros.edit(
                f"{emo.gagal}<b>Cannot find Voice Chat in <code>{title}</code></b>"
            )
        try:
            call_title = group_call.title
            client.group_call.cache_peer(chat_id)
            participants = await client.group_call.get_participants(chat_id)
            mentions = []
            for participant in participants:
                user_id = participant.user_id
                try:
                    user = await client.get_users(user_id)
                    mention = user.mention
                    volume = participant.volume
                    status = "🔇" if participant.muted else "🔊"
                    mentions.append(
                        f"<b>{mention} | ᴍɪᴄ: <code>{status}</code> | ᴠᴏʟ: <code>{volume}%</code></b>"
                    )
                except Exception:
                    mentions.append(f"{user_id} status Unknown")

            total_participants = len(participants)
            if total_participants == 0:
                return await pros.edit(
                    f"{emo.gagal}<b>No one is in the Voice Chat.</b>"
                )

            mentions_text = "\n".join(
                [
                    (f"❖ {mention}" if i < total_participants - 1 else f"❖ {mention}")
                    for i, mention in enumerate(mentions)
                ]
            )

            text = f"""
{emo.sukses}<u>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ʟɪsᴛᴇɴᴇʀs</u>
{emo.owner}ᴄʜᴀᴛ : <code>{title}</code>.
{emo.profil}ᴛᴏᴛᴀʟ : <code>{total_participants}</code> people.
{emo.warn}ᴛɪᴛʟᴇ : <code>{call_title}</code>
━━━━━━━━━━━━━━━━━━━━
{emo.ket}<u>ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛs</u>
<b>{mentions_text}</b>
"""
            return await pros.edit(f"<blockquote expandable>{text}</blockquote>")

        except Exception as e:
            await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{e}</code>")
    except Exception as e:
        await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{e}</code>")


@CMD.UBOT("vctitle")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    chat_id = message.chat.id
    pros = await animate_proses(message, emo.proses) 

    if not pros:
        return
    if len(message.command) < 2:
        return await pros.edit(
            f"{emo.gagal}<b>Provide text/reply to text to set as Voice Chat Title.</b>"
        )
    title = message.text.split(maxsplit=1)[1]
    try:
        chat = await client.get_chat(chat_id)
    except Exception:
        return await pros.edit(
            f"{emo.gagal}<b>Cannot find the group <code>{chat_id}</code></b>"
        )
    chat_title = chat.title
    try:
        group_call = await client.get_call(client, chat_id)
        if not group_call:
            return await pros.edit(
                f"{emo.gagal}<b>No Voice Chat:\n{emo.profil}Group: <code>{chat_title}</code></b>"
            )

        await client.invoke(
            functions.phone.EditGroupCallTitle(
                call=InputGroupCall(
                    id=group_call.id, access_hash=group_call.access_hash
                ),
                title=title,
            )
        )
        return await pros.edit(
            f"{emo.sukses}<b>Successfully changed Voice Chat Title:\n{emo.profil}Group: <code>{chat_title}</code>.\n{emo.warn}Title: <code>{title}</code>.</b>"
        )
    except Exception as e:
        if "CHAT_ADMIN_REQUIRED" in str(e):
            return await pros.edit(f"{emo.gagal}<b>You are not an admin!</b>")
        return await pros.edit(
            f"{emo.profil}Group: <code>{message.chat.title}</code>{emo.gagal}Error:\n <code>{str(e)}</code></b>"
        )
        return await pros.delete(8)

@CMD.UBOT("join_os")
@CMD.FAKE_NLX
async def joinos_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await animate_proses(message, em.proses) 

    if not proses:
        return
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    sk = 0
    gl = 0
    try:
        for X in client._ubot:
            if "/+" in str(chat_id):
                gid = await X.get_chat(str(chat_id))
                chat_id = int(gid.id)
            elif "t.me/" in str(chat_id) or "@" in str(chat_id):
                chat_id = chat_id.replace("https://t.me/", "")
                gid = await X.get_chat(str(chat_id))
                chat_id = int(gid.id)
            else:
                chat_id = int(chat_id)
            try:
                await X.group_call.play(chat_id)
                await X.group_call.unmute_stream(chat_id)
                sk += 1
            except:
                gl += 1
                continue
        return await proses.edit(
            "<b>{} Berhasil Naik Os:\nChat ID: `{}`\nSukses `{}`\nGagal `{}`\nDari Total Userbot: {}</b>".format(
                em.sukses, chat_id, sk, gl, len(client._ubot)
            )
        )
        await proses.delete(8)

    except Exception as e:

        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")
        await proses.delete(8)

@CMD.UBOT("turun_os")
@CMD.FAKE_NLX
async def turunos_cmd(client, message):
    em = Emoji(client)
    await em.get()

    proses = await animate_proses(message, em.proses)
    if not proses:
        return

    chat_input = message.command[1] if len(message.command) > 1 else message.chat.id

    sk = 0
    gl = 0

    try:
        for X in client._ubot:
            try:
                # ==============================
                # INVITE LINK (t.me/+xxxx)
                # ==============================
                if "t.me/+" in str(chat_input) or "joinchat" in str(chat_input):
                    # tidak bisa get_chat().id → langsung leave pakai link
                    target = str(chat_input)

                # ==============================
                # USERNAME LINK / @username
                # ==============================
                elif "t.me/" in str(chat_input) or "@" in str(chat_input):
                    username = str(chat_input).replace("https://t.me/", "")
                    target = username

                # ==============================
                # CHAT ID ANGKA
                # ==============================
                else:
                    target = int(chat_input)

                # ==============================
                # TURUN OS (LEAVE VC)
                # ==============================
                await X.group_call.leave_call(target)
                sk += 1

            except:
                gl += 1
                continue

        await proses.edit(
            f"<b>{em.sukses} Berhasil Turun Os\n"
            f"Target: `{chat_input}`\n"
            f"Sukses: `{sk}`\n"
            f"Gagal: `{gl}`\n"
            f"Total Userbot: `{len(client._ubot)}`</b>"
        )

        await proses.delete(8)

    except Exception as e:
        await proses.edit(f"{em.gagal} **ERROR:** `{e}`")
        return await proses.delete(8)