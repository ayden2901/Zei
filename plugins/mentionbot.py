import asyncio
from collections import defaultdict, deque
from html import escape
from pyrogram.errors import FloodWait
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from Navy import bot, navy
from pyrogram.enums import ChatType, ParseMode, ChatMembersFilter, ChatMemberStatus
from Navy.helpers import CMD, Emoji


__MODULES__ = "ᴛᴀɢᴀʟʟʙᴏᴛ"
__HELP__ = """<blockquote><u>📋 Command Help **ᴛᴀɢᴀʟʟʙᴏᴛ **</u></blockquote>
"""

# ================= GLOBAL =================

_active_task_ids = {}
_tagall_messages = defaultdict(list)
_clear_waiter = defaultdict(asyncio.Event)
_stop_events = defaultdict(asyncio.Event)
_tagall_texts = {}

_tagall_queue = defaultdict(deque)

# ================= ADMIN CHECK =================

async def is_user_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

# ================= QUEUE =================

async def update_queue_positions(chat_id):
    for idx, (func, args, kwargs) in enumerate(_tagall_queue[chat_id]):
        msg = kwargs.get("init_message")
        if msg:
            try:
                await msg.edit(f"⏳ Task di antrian\nPosisi : #{idx+1}")
            except:
                pass

async def enqueue_tagall(chat_id, func, *args, **kwargs):
    _tagall_queue[chat_id].append((func, args, kwargs))
    await update_queue_positions(chat_id)
    if chat_id not in _active_task_ids:
        await run_next_in_queue(chat_id)

async def run_next_in_queue(chat_id):
    if not _tagall_queue[chat_id]:
        return

    func, args, kwargs = _tagall_queue[chat_id].popleft()
    _active_task_ids[chat_id] = True

    msg = kwargs.get("init_message")
    if msg:
        try:
            await msg.edit("🚀 Task dijalankan...")
        except:
            pass

    await func(*args, **kwargs)

    _active_task_ids.pop(chat_id, None)
    await run_next_in_queue(chat_id)

# ================= COMMAND =================

@CMD.BOT("tagall")
async def tagall_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if not message.from_user:
        return await message.reply("❌ User tidak valid")
    if not await is_user_admin(client, chat_id, message.from_user.id):
        return await message.reply("❌ Kamu bukan admin")

    text = message.text.split(None, 1)
    if len(text) < 2 and not message.reply_to_message:
        return await message.reply("❌ Masukkan teks atau reply pesan")
    if message.reply_to_message:
        text = message.reply_to_message.text or ""
    else:
        text = text[1]

    safe_text = escape(text)
    _tagall_texts[chat_id] = safe_text

    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5 Menit", f"tagall|{chat_id}|300|0"),
            InlineKeyboardButton("10 Menit", f"tagall|{chat_id}|600|0")
        ],
        [
            InlineKeyboardButton("15 Menit", f"tagall|{chat_id}|900|0"),
            InlineKeyboardButton("30 Menit", f"tagall|{chat_id}|1800|0")
        ],
        [
            InlineKeyboardButton("Unlimited", f"tagall|{chat_id}|0|0")
        ],
        [
            InlineKeyboardButton("❌ Cancel", f"canceltag|{chat_id}")
        ]
    ])

    msg = await message.reply(
        "🕰 Pilih timeout tagall",
        reply_markup=markup
    )
    _tagall_messages[chat_id].append(msg.id)

@CMD.BOT("admin")
async def tagadmin_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if not message.from_user:
        return await message.reply("❌ User tidak valid")
    if not await is_user_admin(client, chat_id, message.from_user.id):
        return await message.reply("❌ Kamu bukan admin")

    text = message.text.split(None, 1)
    if len(text) < 2 and not message.reply_to_message:
        return await message.reply("❌ Masukkan teks atau reply pesan")
    if message.reply_to_message:
        text = message.reply_to_message.text or ""
    else:
        text = text[1]

    safe_text = escape(text)
    _tagall_texts[chat_id] = safe_text

    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5 Menit", f"tagall|{chat_id}|300|1"),
            InlineKeyboardButton("10 Menit", f"tagall|{chat_id}|600|1")
        ],
        [
            InlineKeyboardButton("15 Menit", f"tagall|{chat_id}|900|1"),
            InlineKeyboardButton("30 Menit", f"tagall|{chat_id}|1800|1")
        ],
        [
            InlineKeyboardButton("Unlimited", f"tagall|{chat_id}|0|1")
        ],
        [
            InlineKeyboardButton("❌ Cancel", f"canceltag|{chat_id}")
        ]
    ])

    msg = await message.reply(
        "🕰 Pilih timeout tag admin",
        reply_markup=markup
    )
    _tagall_messages[chat_id].append(msg.id)

# ================= CALLBACK =================

@CMD.CALLBACK("^tagall")
async def tagall_callback(client: Client, callback: CallbackQuery):
    _, chat_id, timeout, admin_flag = callback.data.split("|")
    chat_id = int(chat_id)
    timeout = int(timeout)
    admin_only = bool(int(admin_flag))

    if not await is_user_admin(client, chat_id, callback.from_user.id):
        return await callback.answer("❌ Kamu bukan admin", True)

    safe_text = _tagall_texts.get(chat_id)
    try:
        await callback.message.edit_reply_markup(None)
    except:
        pass

    await enqueue_tagall(
        chat_id,
        run_tagall,
        client,
        callback.message,
        safe_text,
        chat_id,
        timeout,
        callback.from_user,
        admin_only,
        init_message=callback.message
    )

# ================= SAFE SEND =================

async def safe_send(client, chat_id, text, **kwargs):
    while True:
        try:
            return await client.send_message(chat_id, text, **kwargs)
        except FloodWait as e:
            await asyncio.sleep(e.value)

# ================= RUN TAGALL =================

async def run_tagall(client, message, safe_text, chat_id, timeout, creator, admin_only=False, init_message=None):
    em = Emoji(client)
    await em.get()
    ids = f"{em.pin}ᴄʀᴇᴀᴛᴇᴅ ʙʏ @quotedamn"

    if not safe_text:
        safe_text = "📢 Tagall"

    _clear_waiter[chat_id] = asyncio.Event()
    _stop_events[chat_id].clear()

    start = await safe_send(
        client,
        chat_id,
        "🚀 Tagall dimulai...",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⛔ Stop Tagall", f"stoptag|{chat_id}")]
        ])
    )
    _tagall_messages[chat_id].append(start.id)

    admins = {
        m.user.id async for m in client.get_chat_members(
            chat_id,
            filter=ChatMembersFilter.ADMINISTRATORS
        )
    }

    buf = ""
    count = 0

    # proses tag
    async for m in client.get_chat_members(chat_id):
        if _stop_events[chat_id].is_set():
            break

        if timeout != 0:
            now = asyncio.get_event_loop().time()
            if now - asyncio.get_event_loop().time() >= timeout:
                break

        if not m.user or m.user.is_bot or m.user.is_deleted:
            continue
        if admin_only and m.user.id not in admins:
            continue

        name = escape(m.user.first_name or "User")
        buf += f'👤 <a href="tg://user?id={m.user.id}">{name}</a>\n'
        count += 1

        if count == 5:
            msg = await safe_send(
                client,
                chat_id,
                f"<blockquote>{safe_text}</blockquote>\n"
                f"<blockquote>{buf}</blockquote>\n"
                f"<blockquote>{ids}</blockquote>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⛔ Stop Tagall", f"stoptag|{chat_id}")]
                ])
            )
            _tagall_messages[chat_id].append(msg.id)
            buf = ""
            count = 0
            await asyncio.sleep(5)

    # sisa buffer
    if buf:
        msg = await safe_send(
            client,
            chat_id,
            f"<blockquote>{safe_text}</blockquote>\n"
            f"<blockquote>{buf}</blockquote>\n"
            f"<blockquote>{ids}</blockquote>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⛔ Stop Tagall", f"stoptag|{chat_id}")]
            ])
        )
        _tagall_messages[chat_id].append(msg.id)

    done = await safe_send(
        client,
        chat_id,
        f"<b>Tagall selesai</b>\nDibuat oleh : {creator.mention}",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧹 Clear", f"cleartag|{chat_id}")]
        ])
    )
    _tagall_messages[chat_id].append(done.id)

    await _clear_waiter[chat_id].wait()


# ================= STOP =================

@CMD.CALLBACK("^stoptag")
async def stoptag(client: Client, callback: CallbackQuery):

    chat_id = int(callback.data.split("|")[1])

    if not await is_user_admin(client, chat_id, callback.from_user.id):
        return await callback.answer("❌ Kamu bukan admin", True)

    _stop_events[chat_id].set()

    await callback.message.edit(
        f"❌ Tagall dihentikan oleh {callback.from_user.mention}"
    )


# ================= CANCEL =================

@CMD.CALLBACK("^canceltag")
async def cancel_tag(client: Client, callback: CallbackQuery):

    chat_id = int(callback.data.split("|")[1])

    if not await is_user_admin(client, chat_id, callback.from_user.id):
        return await callback.answer("❌ Kamu bukan admin", True)

    try:
        await callback.message.delete()
    except:
        pass

    await callback.answer("❌ Tagall dibatalkan")


# ================= CLEAR =================

@CMD.CALLBACK("^cleartag")
async def cleartag(client: Client, callback: CallbackQuery):

    chat_id = int(callback.data.split("|")[1])

    if not await is_user_admin(client, chat_id, callback.from_user.id):
        return await callback.answer("❌ Kamu bukan admin", True)

    for mid in _tagall_messages.get(chat_id, []):

        try:
            await client.delete_messages(chat_id, mid)
        except:
            pass

    _tagall_messages.pop(chat_id, None)

    _clear_waiter[chat_id].set()

    await callback.answer("🧹 Message dibersihkan")