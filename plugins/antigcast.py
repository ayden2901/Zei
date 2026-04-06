import asyncio
import os
import html
import re
import random
import unicodedata

from pyrogram import filters, Client, types
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from pyrogram.types import InlineKeyboardButton as Ikb

from pyrogram.enums import (
    ChatType,
    ParseMode,
    MessageEntityType,
    ChatMemberStatus
)

from pyrogram.errors import (
    FloodWait,
    MessageNotModified,
    UserNotParticipant,
    ChatAdminRequired,
    PeerIdInvalid,
    ChannelInvalid
)

from pyrogram.helpers import ikb

from config import BLACKLIST_GCAST
from Navy.database import dB
from Navy.helpers import CMD, Emoji
from Navy import bot, navy


REQUIRED_CHAT_ID = -1002886441190
REQUIRED_CHAT_LINK = "https://t.me/daredevilsnih"


trigger_words = [
    "join", "channel", "giveaway", "gcast", "support", "t.me/", "broadcast",
    "promo", "vcs", "open", "kontol", "openn", "opennn", "opennnn",
    "wts", "wtc", "byoh", "link", "linkk", "linkkk",
    "t3km10ut", "t0brut", "cnge", "wannhekktenggmi0otttagaii11innn",
    "byiooo", "by10", "bioulkkk", "tnio", "talent",
    "slot", "1slot", "2slot", "3slot", "4slot",
    "byouh", "private", "priv", "pvt",
    "omek", "omekk", "omekkk",
    "viral", "virall", "viralll",
    "opmin", "event", "redi", "ucast", "ukes", "yubot",
    "tmnin", "temnin", "nokos", "ubot",
    "biyoh", "asupan", "skandal", "konbrut",
    "knbrt", "tobrut", "tbrt",
    "memek", "kntl", "mmk",
    "ppq", "ppk", "pepeq", "pepek",
    "anjing", "anj", "ajg",
    "gikes", "ucast", "ankes",
    "ready", "redii", "rediii", "ridii", "ridihh",
    "bioh", "joinn", "ange",
    "gikesan", "kolseg", "kolsek",
    "callsex", "picies", "kolsex",
    "sex", "vicies", "vicis",
    "hentai", "crt", "crotttttt", "croottt",
    "tkmiotby0h", "angean", "vip",
    "mrvz", "morvenz",
    "spc", "spancer", "spencer",
    "iqis", "universal", "@",
    "gomez", "byyoihh",
]


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9@.\s:/]", "", text).lower()


async def is_user_joined_chat(client, user_id: int, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]
    except:
        return False


async def is_user_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        status = (await client.get_chat_member(chat_id, user_id)).status
        return status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False


def get_fullname(user):
    name = (user.first_name or "")
    if user.last_name:
        name += f" {user.last_name}"

    name = html.escape(name.strip())
    return f'<a href="tg://user?id={user.id}">{name}</a>'


async def auto_delete(msg: Message, delay: int = 2):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass


async def add_whitelist_user(chat_id: int, user_id: int):
    await dB.set_add(f"antigcast:whitelist:{chat_id}", user_id)


async def remove_whitelist_user(chat_id: int, user_id: int):
    await dB.set_remove(f"antigcast:whitelist:{chat_id}", user_id)


async def get_whitelist_users(chat_id: int):
    return await dB.get_set(f"antigcast:whitelist:{chat_id}")


async def set_antigcast_mode(chat_id: int, mode: str):
    await dB.set_var(chat_id, "ANTIGCAST_MODE", mode)


async def get_antigcast_mode(chat_id: int):
    mode = await dB.get_var(chat_id, "ANTIGCAST_MODE")
    return mode or "medium"

async def antigcast_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user or user.is_bot or message.sender_chat:
        return

    user_id = user.id

    # ================= COMMAND ================= #

    if message.text and message.text.startswith("/antigcast"):
        args = message.text.split()[1:] if message.text else []
        cmd = args[0].lower() if args else ""

        if not await is_user_admin(client, chat_id, user_id):
            res = await message.reply("❌ Kamu bukan admin Group.")
            await auto_delete(message)
            return await auto_delete(res, 3)

        if not await is_user_joined_chat(client, user_id, REQUIRED_CHAT_ID):
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📌𝗚𝗥𝗢𝗨𝗣 𝗦𝗨𝗣𝗣𝗢𝗥𝗧",
                            url=REQUIRED_CHAT_LINK
                        )
                    ]
                ]
            )

            res = await message.reply(
                f"<b>🔒 Hi {get_fullname(user)} kamu belum bergabung ke channel/grup untuk menggunakan perintah ini.</b>",
                reply_markup=keyboard
            )

            await auto_delete(message)
            return await auto_delete(res, 15)

        # ================= ON ================= #

        if cmd == "on":
            await dB.set_antigcast_status(chat_id, True)

            status_dict = await dB.get_antigcast_status()
            print(f"[DEBUG] Status setelah ON: {status_dict.get(chat_id)}")

            res = await message.reply("✅ AntiGcast diaktifkan.")

            await auto_delete(message)
            return await auto_delete(res, 3)

        # ================= OFF ================= #

        elif cmd == "off":
            await dB.set_antigcast_status(chat_id, False)

            status_dict = await dB.get_antigcast_status()
            print(f"[DEBUG] Status setelah OFF: {status_dict.get(chat_id)}")

            res = await message.reply("❎ AntiGcast dimatikan.")

            await auto_delete(message)
            return await auto_delete(res, 3)

        # ================= BLACKLIST ================= #

        elif cmd == "blacklist":
            try:

                if message.reply_to_message and message.reply_to_message.from_user:
                    target_user = message.reply_to_message.from_user

                elif len(args) > 1:
                    target_user = await client.get_users(args[1])

                else:
                    res = await message.reply(
                        "❌ Balas pesan user atau beri username/user_id."
                    )
                    await auto_delete(message)
                    return await auto_delete(res, 3)

                target_id = target_user.id
                name = get_fullname(target_user)

                bl_dict = await dB.get_bluser_dict()
                whitelist = await dB.get_whitelist_users(chat_id)

                if target_id in whitelist:
                    await dB.remove_whitelist_user(chat_id, target_id)
                    print(
                        f"[DEBUG] {name} ({target_id}) dihapus dari whitelist karena masuk blacklist"
                    )

                if target_id in bl_dict.get(chat_id, []):
                    res = await message.reply(
                        f"⚠️ {name} sudah ada di blacklist.",
                        parse_mode=ParseMode.HTML
                    )
                    await auto_delete(message)
                    return await auto_delete(res, 3)

                await dB.add_bluser(chat_id, target_id)

                res = await message.reply(
                    f"✅ {name} berhasil dimasukkan ke blacklist.",
                    parse_mode=ParseMode.HTML
                )

                await auto_delete(message)
                return await auto_delete(res, 3)

            except:
                res = await message.reply("❌ User tidak ditemukan.")
                await auto_delete(message)
                return await auto_delete(res, 3)

        # ================= UNBLACKLIST ================= #

        elif cmd == "unblacklist":
            try:

                if message.reply_to_message and message.reply_to_message.from_user:
                    target_user = message.reply_to_message.from_user

                elif len(args) > 1:
                    target_user = await client.get_users(args[1])

                else:
                    res = await message.reply(
                        "❌ Balas pesan user atau beri username/user_id."
                    )
                    await auto_delete(message)
                    return await auto_delete(res, 3)

                target_id = target_user.id
                name = get_fullname(target_user)

                bl_dict = await dB.get_bluser_dict()

                if target_id in bl_dict.get(chat_id, []):

                    await dB.remove_bluser(chat_id, target_id)

                    res = await message.reply(
                        f"✅ {name} berhasil dihapus dari blacklist.",
                        parse_mode=ParseMode.HTML
                    )

                else:

                    res = await message.reply(
                        f"⚠️ {name} tidak ada dalam blacklist.",
                        parse_mode=ParseMode.HTML
                    )

                await auto_delete(message)
                return await auto_delete(res, 3)

            except:
                res = await message.reply("❌ User tidak ditemukan.")
                await auto_delete(message)
                return await auto_delete(res, 3)

        # ================= LIST BLACKLIST ================= #

        elif cmd == "listblacklist":

            bl_dict = await dB.get_bluser_dict()
            whitelist = await dB.get_whitelist_users(chat_id)

            user_list = bl_dict.get(chat_id, [])

            if not user_list and not whitelist:

                res = await message.reply(
                    "✅ Tidak ada user dalam blacklist maupun whitelist."
                )

                await auto_delete(message)
                return await auto_delete(res, 3)

            text = "<b>📄 Daftar Blacklist:</b>\n"

            i = 1
            for uid in user_list:

                try:
                    user_obj = await client.get_users(uid)
                    name = get_fullname(user_obj)

                    text += f"{i}. {name} - <code>{uid}</code>\n"
                    i += 1

                except PeerIdInvalid:
                    await dB.remove_bluser(chat_id, uid)

            text += "\n<b>✅ Daftar Whitelist:</b>\n"

            j = 1
            for uid in whitelist:

                try:
                    user_obj = await client.get_users(uid)
                    name = get_fullname(user_obj)

                    text += f"{j}. {name} - <code>{uid}</code>\n"
                    j += 1

                except PeerIdInvalid:
                    await dB.remove_whitelist_user(chat_id, uid)

            res = await message.reply(
                f"<blockquote expandable>{text}</blockquote>",
                parse_mode=ParseMode.HTML
            )

            return await auto_delete(message)

        # ================= RM BLACKLIST ================= #

        elif cmd == "rmblacklist":

            await dB.remove_all_bluser(chat_id)
            await dB.remove_all_whitelist_users(chat_id)

            res = await message.reply("🗑️ Semua blacklist dihapus.")

            await auto_delete(message)
            return await auto_delete(res, 3)

        # ================= WHITELIST ================= #

        elif cmd == "whitelist":
            try:

                if message.reply_to_message and message.reply_to_message.from_user:
                    target_user = message.reply_to_message.from_user

                elif len(args) > 1:
                    target_user = await client.get_users(args[1])

                else:
                    res = await message.reply(
                        "❌ Balas pesan user atau beri username/user_id."
                    )
                    await auto_delete(message)
                    return await auto_delete(res, 3)

                target_id = target_user.id
                name = get_fullname(target_user)

                whitelist = await dB.get_whitelist_users(chat_id)
                bl_dict = await dB.get_bluser_dict()

                if chat_id in bl_dict and target_id in bl_dict[chat_id]:

                    await dB.remove_bluser(chat_id, target_id)

                    print(
                        f"[DEBUG] {name} ({target_id}) dihapus dari blacklist karena masuk whitelist"
                    )

                if target_id in whitelist:

                    res = await message.reply(
                        f"⚠️ {name} sudah ada dalam whitelist."
                    )

                else:

                    await dB.add_whitelist_user(chat_id, target_id)

                    res = await message.reply(
                        f"✅ {name} berhasil ditambahkan ke whitelist."
                    )

                await auto_delete(message)
                return await auto_delete(res, 3)

            except Exception as e:

                import traceback
                print(traceback.format_exc())

                res = await message.reply(
                    f"❌ Gagal mengambil user: {e}"
                )

                await auto_delete(message)
                return await auto_delete(res, 3)

        # ================= UNWHITELIST ================= #

        elif cmd == "unwhitelist":
            try:

                if message.reply_to_message and message.reply_to_message.from_user:
                    target_user = message.reply_to_message.from_user

                elif len(args) > 1:
                    target_user = await client.get_users(args[1])

                else:
                    res = await message.reply(
                        "❌ Balas pesan user atau beri username/user_id."
                    )
                    await auto_delete(message)
                    return await auto_delete(res, 3)

                target_id = target_user.id
                name = get_fullname(target_user)

                whitelist = await dB.get_whitelist_users(chat_id)

                if target_id in whitelist:

                    await dB.remove_whitelist_user(chat_id, target_id)

                    res = await message.reply(
                        f"✅ {name} berhasil dihapus dari whitelist."
                    )

                else:

                    res = await message.reply(
                        f"⚠️ {name} tidak ada dalam whitelist."
                    )

                await auto_delete(message)
                return await auto_delete(res, 3)

            except:
                res = await message.reply("❌ User tidak ditemukan.")
                await auto_delete(message)
                return await auto_delete(res, 3)

        # ================= MODE ================= #

        elif cmd == "mode":

            if len(args) < 2:

                res = await message.reply(
                    "❌ Gunakan:\n"
                    "<code>/antigcast mode slow</code>\n"
                    "<code>/antigcast mode medium</code>\n"
                    "<code>/antigcast mode expert</code>",
                    parse_mode=ParseMode.HTML
                )

                await auto_delete(message)
                return await auto_delete(res, 5)

            mode = args[1].lower()

            if mode not in ["slow", "medium", "expert"]:

                res = await message.reply(
                    "❌ Mode tersedia: slow, medium, expert"
                )

                await auto_delete(message)
                return await auto_delete(res, 5)

            await set_antigcast_mode(chat_id, mode)

            res = await message.reply(
                f"⚙️ Mode AntiGcast diubah ke <b>{mode.upper()}</b>",
                parse_mode=ParseMode.HTML
            )

            await auto_delete(message)
            return await auto_delete(res, 3)

        # ================= HELP ================= #

        elif cmd == "help":

            try:

                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "ᴘᴀɴᴅᴜᴀɴ",
                                callback_data="antigcast_panduan"
                            ),
                            InlineKeyboardButton(
                                "⌂",
                                callback_data="antigcast_close"
                            )
                        ]
                    ]
                )

                await message.reply(
                    "<b>Silakan pilih menu bantuan di bawah ini.</b>",
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )

                return await auto_delete(message)

            except Exception as e:
                print(f"Error di help: {e}")

        return

    # ================= SYSTEM ANTIGCAST ================= #

    chat_id = int(message.chat.id)

    status_dict = await dB.get_antigcast_status()

    if not status_dict.get(chat_id, False):
        return

    if await is_user_admin(client, chat_id, user_id):
        return

    # ================= BLACKLIST CHECK ================= #

    bl_dict = await dB.get_bluser_dict()

    if chat_id in bl_dict and user_id in bl_dict[chat_id]:

        try:
            await message.delete()

            res = await message.reply(
                f"<blockquote><b>{get_fullname(user)}</b> terdeteksi melakukan spam atau gcast dalam grup.</blockquote>",
                parse_mode=ParseMode.HTML
            )

            return await auto_delete(res, 3)

        except:
            return

    # ================= DETECTION ================= #

    mode = await get_antigcast_mode(chat_id)

    raw_text = message.text or message.caption or ""
    if not raw_text:
        return

    normalized = normalize_text(raw_text)

    whitelist = await dB.get_whitelist_users(chat_id)

    if user_id in whitelist:
        return

    if any(word in normalized for word in trigger_words):

        if mode == "slow":
            chance = 0.78
        elif mode == "medium":
            chance = 0.88
        elif mode == "expert":
            chance = 0.98
        else:
            chance = 0.88

        if random.random() <= chance:
            try:
                await message.delete()

                res = await message.reply(
                f"<blockquote><b>{get_fullname(user)}</b> terdeteksi melakukan spam atau gcast dalam grup.</blockquote>",
                    parse_mode=ParseMode.HTML
                )

                return await auto_delete(res, 3)

            except:
                return

    # ================= RANDOM NOISE ================= #

    if mode == "slow":
        noise = 0.50

    elif mode == "medium":
        noise = 0.70

    elif mode == "expert":
        noise = 0.90

    else:
        noise = 0.70

    if random.random() <= noise:

        try:

            await message.delete()

            res = await message.reply(
                f"<blockquote><b>{get_fullname(user)}</b> terdeteksi melakukan spam atau gcast dalam grup.</blockquote>",
                parse_mode=ParseMode.HTML
            )

            return await auto_delete(res, 3)

        except:
            pass


bot.on_message(
    filters.group & (filters.text | filters.caption),
    group=99
)(antigcast_handler)


@CMD.CALLBACK("^antigcast_")
async def _(client, callback_query: CallbackQuery):
    data = callback_query.data
    print(f"[DEBUG] Callback received: {data}")

    if data == "antigcast_panduan":
        try:
            mention = (await client.get_me()).mention

            text_ids = (
                f"<blockquote><b>{mention}\n"
                f"©️ ᴄʀᴇᴀᴛᴇᴅ ʙʏ ➟</b> "
                f"<a href=tg://user?id=768849986>#1↻￴`sтαя⋆</a></blockquote>"
            )

            text = f"""
<blockquote><u>📋 Command Help <b>ᴀɴᴛɪɢᴄᴀsᴛ</b></u></blockquote>

<blockquote expandable><b>❖ you can enable/disable ᴀɴᴛɪɢᴄᴀsᴛ</b>

    <b>➣ set ᴀɴᴛɪɢᴄᴀsᴛ on or off</b>
        <code>/antigcast on</code>
        <code>/antigcast off</code>

━━━━━━━━━━━━━━━━━━━
<b>❖ you can add users to the blacklist ᴀɴᴛɪɢᴄᴀsᴛ</b>

    <b>➣ set blacklist ᴀɴᴛɪɢᴄᴀsᴛ to add users to the list</b>
        <code>/antigcast blacklist</code> (reply/username/user id)

━━━━━━━━━━━━━━━━━━━
<b>❖ you can delete users from the blacklist ᴀɴᴛɪɢᴄᴀsᴛ</b>

    <b>➣ set unblacklist ᴀɴᴛɪɢᴄᴀsᴛ to delete users to the list</b>
        <code>/antigcast unblacklist</code> (reply/username/user id)

━━━━━━━━━━━━━━━━━━━
<b>❖ you can remove all users in the antigcast list</b>

    <b>➣ set rmblacklist ᴀɴᴛɪɢᴄᴀsᴛ to remove all users in the list</b>
        <code>/antigcast rmblacklist</code>

━━━━━━━━━━━━━━━━━━━
<b>❖ you can see the list of users who have been blacklisted</b>

    <b>➣ set listblacklist ᴀɴᴛɪɢᴄᴀsᴛ to see users in the blacklist</b>
        <code>/antigcast listblacklist</code>

━━━━━━━━━━━━━━━━━━━
<b>❖ you can add users to the whitelist ᴀɴᴛɪɢᴄᴀsᴛ</b>

    <b>➣ set whitelist ᴀɴᴛɪɢᴄᴀsᴛ to add users to the list</b>
        <code>/antigcast whitelist</code> (reply/username/user id)

━━━━━━━━━━━━━━━━━━━
<b>❖ you can change antigcast detection mode</b>

    <b>➣ set antigcast detection level</b>
        <code>/antigcast mode slow</code>
        <code>/antigcast mode medium</code>
        <code>/antigcast mode expert</code>

━━━━━━━━━━━━━━━━━━━
<b>❖ you can delete users from the whitelist ᴀɴᴛɪɢᴄᴀsᴛ</b>

    <b>➣ set whitelist ᴀɴᴛɪɢᴄᴀsᴛ to delete users to the list</b>
        <code>/antigcast unwhitelist</code> (reply/username/user id)

</blockquote>

<b>{text_ids}</b>
"""

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⟲", callback_data="antigcast_back"),
                        InlineKeyboardButton("⌂", callback_data="antigcast_close"),
                    ]
                ]
            )

            await callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

        except MessageNotModified:
            pass
        except Exception as e:
            print(f"[ERROR] antigcast_panduan: {e}")

    elif data == "antigcast_back":
        try:
            text = "<b>Silakan pilih menu bantuan di bawah ini.</b>"

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ᴘᴀɴᴅᴜᴀɴ",
                            callback_data="antigcast_panduan"
                        ),
                        InlineKeyboardButton(
                            "⌂",
                            callback_data="antigcast_close"
                        ),
                    ]
                ]
            )

            await callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

        except MessageNotModified:
            pass
        except Exception as e:
            print(f"[ERROR] antigcast_help_back: {e}")

    elif data == "antigcast_close":
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"[ERROR] close_antigcast: {e}")


__MODULES__ = "ᴀɴᴛɪɢᴄᴀsᴛ"
__HELP__ = """<blockquote><u>📋 Command Help **ᴀɴᴛɪɢᴄᴀsᴛ **</u></blockquote>
<blockquote>**you can enable/disable ᴀɴᴛɪɢᴄᴀsᴛ**</blockquote>
    **set ᴀɴᴛɪɢᴄᴀsᴛ on or off**
        `/antigcast on`
        `/antigcast off`

<blockquote>**you can add users to the blacklist ᴀɴᴛɪɢᴄᴀsᴛ**</blockquote>
    **set blacklist ᴀɴᴛɪɢᴄᴀsᴛ to add users to the list**
        `/antigcast blacklist` (reply/username/user id)

<blockquote>**you can delete users from the blacklist ᴀɴᴛɪɢᴄᴀsᴛ**</blockquote>
    **set unblacklist ᴀɴᴛɪɢᴄᴀsᴛ to delete users to the list**
        `/antigcast unblacklist` (reply/username/user id)

<blockquote>**you can remove all users in the antigcast list**</blockquote>
    **set rmblacklist ᴀɴᴛɪɢᴄᴀsᴛ to remove all users in the list**
        `/antigcast rmblacklist`

<blockquote>**you can see the list of users who have been blacklisted**</blockquote>
    **set listblacklist ᴀɴᴛɪɢᴄᴀsᴛ to see users in the blacklist**
        `/antigcast listblacklist`

<blockquote>**you can add users to the whitelist ᴀɴᴛɪɢᴄᴀsᴛ**</blockquote>
    **set whitelist ᴀɴᴛɪɢᴄᴀsᴛ to add users to the list**
        `/antigcast whitelist` (reply/username/user id)

<blockquote>**you can delete users from the whitelist ᴀɴᴛɪɢᴄᴀsᴛ**</blockquote>
    **set whitelist ᴀɴᴛɪɢᴄᴀsᴛ to delete users to the list**
        `/antigcast unwhitelist` (reply/username/user id)

<b>   {1}</b>
"""
