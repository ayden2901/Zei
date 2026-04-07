import re

from pyrogram import enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.helpers import ikb, kb
from pyrogram.types import InlineKeyboardMarkup, WebAppInfo, InlineKeyboardButton
from math import ceil
from typing import List, Optional, Tuple
from config import BOT_NAME, HELPABLE, ALIVE_PIC, HELP_LOGO
from Navy import bot, navy
from Navy.database import dB, state
from Navy.helpers import CMD, paginate_modules, Emoji
from Navy.logger import logger


async def cek_plugins(client, message):
    em = Emoji(client)
    await em.get()
    ubot_ = await em.get_costum_text()
    user_id = message.from_user.id
    prefix = navy.get_prefix(user_id)
    text_help = (
        await dB.get_var(user_id, "text_help") or f"{bot.me.mention}" 
    )
    full = f"<a href=tg://user?id={message.from_user.id}>{message.from_user.first_name} {message.from_user.last_name or '' }</a>"
    msg = """
    ❏ <b>ᴍᴇɴᴜ ɪɴʟɪɴᴇ</b>
    ├ <b>ᴘʀᴇғɪx ➟</b> <code>{}</code>
    ├ <b>ᴍᴏᴅᴜʟᴇs ➟</b> <code>{}</code>
    ├ <b>ᴏᴡɴᴇʀ ➟</b> {}
    ╰ <b>ᴜʙᴏᴛ ➟</b> {}""".format(
        " ".join(prefix), len(HELPABLE), full, text_help
    )
    return await message.reply_text(
        msg, reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", is_bot=True))
    )    


top_text = """
❏ <b>ᴍᴇɴᴜ ɪɴʟɪɴᴇ</b>
├ <b>ᴘʀᴇғɪx ➟</b> <code>{}</code>
├ <b>ᴍᴏᴅᴜʟᴇs ➟</b> <code>{}</code>
├ <b>ᴏᴡɴᴇʀ ➟</b> {}
╰ <b>ᴜʙᴏᴛ ➟</b> {}"""

text_markdown = "**To view markdown format please click on the button below.**"
text_formatting = """<blockquote expandable>
> **Markdown Formatting**
> Anda dapat memformat pesan Anda menggunakan **tebal**, _miring_, --garis bawah--, ~~coret~~, dan banyak lagi.
>
> `<code>kata kode</code>`: Tanda kutip terbalik digunakan buat font monospace. Ditampilkan sebagai: `kata kode`.
>
> `<i>miring</i>`: Garis bawah digunakan buat font miring. Ditampilkan sebagai: __kata miring__.
>
> `<b>tebal</b>`: Asterisk digunakan buat font tebal. Ditampilkan sebagai: **kata tebal**.
>
> `<u>garis bawah</u>`: Buat membuat teks --garis bawah--.
>
> `<strike>coret</strike>`: Tilda digunakan buat strikethrough. Ditampilkan sebagai: ~~coret~~.
>
> `<spoiler>spoiler</spoiler>`: Garis vertikal ganda digunakan buat spoiler. Ditampilkan sebagai: ||spoiler||.
>
> `[hyperlink](contoh)`: Ini adalah pemformatan yang digunakan buat hyperlink.
>
> `<blockquote>teks quote</blockquote>`: Ini adalah pemformatan untuk > teks quote >
>
> `Hallo Disini [Tombol 1|https://link.com]` : Ini adalah pemformatan yang digunakan membuat tombol.
> `Halo Disini [Tombol 1|t.me/link1][Tombol 2|t.me/link2|same]` : Ini akan membuat tombol berdampingan.
>
> Anda juga bisa membuat tombol callback_data dengan diawal tanda `cb_`
> Jika ingin membuat copy text gunakan Halo Disini `[Click To Copy|copy:1234]`
> Contoh callback `Halo Disini [Tombol 1|data][Tombol 2|data|same]`
</blockquote>"""

text_fillings = "<blockquote expandable><b>Fillings</b>\n\nAnda juga dapat menyesuaikan isi pesan Anda dengan data kontekstual. Misalnya, Anda bisa menyebut nama pengguna dalam pesan selamat datang, atau menyebutnya dalam filter!\n\n<b>Isian yang didukung:</b>\n\n<code>{first}</code>: Nama depan pengguna.\n<code>{last}</code>: Nama belakang pengguna.\n<code>{fullname}</code>: Nama lengkap pengguna.\n<code>{username}</code>: Nama pengguna pengguna. Jika mereka tidak memiliki satu, akan menyebutkan pengguna tersebut.\n<code>{mention}</code>: Menyebutkan pengguna dengan nama depan mereka.\n<code>{id}</code>: ID pengguna.\n<code>{date}</code>: Tanggal, <code>{day}</code>: hari, <code>{month}</code>: bulan, <code>{year}</code>: tahun, <code>{hour}</code>: jam, <code>{minute}</code>: menit.</blockquote>"


@CMD.CALLBACK("^markdown")
async def _(client, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    cekpic = await dB.get_var(user_id, "HELP_LOGO")
    costum_cq = (
        callback_query.edit_message_caption
        if cekpic
        else callback_query.edit_message_text
    )
    full = f"<a href=tg://user?id={callback_query.from_user.id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    costum_text = "caption" if cekpic else "text"
    prev_page_num = state.get(user_id, "prev_page_num")
    if data == "format":
        try:
            button = ikb(
                [
                    [
                        ("Formatting", "markdown_format", "callback_data"),
                        ("Fillings", "markdown_fillings", "callback_data"),
                        ("⌂", "close help", "callback_data"),
                    ],
                    [
                        ("ʙᴀᴄᴋ", f"help_back({prev_page_num})"),
                    ],
                ]
            )
            return await costum_cq(
                **{costum_text: text_formatting},
                reply_markup=button,
                parse_mode=enums.ParseMode.MARKDOWN,
            )

        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif data == "fillings":
        try:
            button = ikb(
                [
                    [
                        ("Formatting", "markdown_format", "callback_data"),
                        ("Fillings", "markdown_fillings", "callback_data"),
                    ],
                    [
                        ("ʙᴀᴄᴋ", f"help_back({prev_page_num})"),
                        ("⌂", "close help", "callback_data"),
                    ],
                ]
            )
            return await costum_cq(
                **{costum_text: text_fillings},
                reply_markup=button,
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return


@CMD.CALLBACK("help_(.*?)")
async def _(client, callback_query):
    await callback_query.answer()
    em = Emoji(client)
    await em.get()
    ubot_ = await em.get_costum_text()
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", callback_query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", callback_query.data)
    next_match = re.match(r"help_next\((.+?)\)", callback_query.data)
    back_match = re.match(r"help_back\((\d+)\)", callback_query.data)
    close_match = re.match(r"help_close\((\d+)\)", callback_query.data)
    create_match = re.match(r"help_create", callback_query.data)
    user_id = callback_query.from_user.id
    prefix = navy.get_prefix(user_id)
    x_ = next(iter(prefix))
    full = f"<a href=tg://user?id={callback_query.from_user.id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    cekpic = await dB.get_var(user_id, "HELP_LOGO")
    text_help = (
        await dB.get_var(user_id, "text_help") or f"{bot.me.mention}"
    )
    text_help2 = f"<blockquote><b>{bot.me.mention}\n©️ ᴄʀᴇᴀᴛᴇᴅ ʙʏ ➟</b> <a href=tg://user?id=5819562467>zei⋆</a></blockquote>"
    costum_cq = (
        callback_query.edit_message_caption
        if cekpic
        else callback_query.edit_message_text
    )
    costum_text = "caption" if cekpic else "text"
    if mod_match:
        module = mod_match.group(1)
        logger.info(f"line 48: {module}")
        prev_page_num = int(mod_match.group(2))
        state.set(user_id, "prev_page_num", prev_page_num)
        bot_text = f"{HELPABLE[module]['module'].__HELP__}".format(x_, text_help2)
        if "markdown" in bot_text:
            try:
                button_ = ikb(
                    [
                        [
                            ("Formatting", "markdown_format", "callback_data"),
                            ("Fillings", "markdown_fillings", "callback_data"),
                        ],
                        [
                            ("ʙᴀᴄᴋ", f"help_back({prev_page_num})"),
                            ("⌂", "close help", "callback_data"),
                        ],
                    ]
                )
                return await costum_cq(
                    **{costum_text: text_markdown},
                    reply_markup=button_,
                )
            except FloodWait as e:
                return await callback_query.answer(
                    f"FloodWait {e}, Please Waiting!!", True
                )

            except MessageNotModified:
                return
        else:
            try:
                button = ikb(
                    [
                        [
                            ("ʙᴀᴄᴋ", f"help_back({prev_page_num})", "callback_data"),
                            ("⌂", "close help", "callback_data"),
                        ]
                    ]
                )
                return await costum_cq(
                    **{costum_text: bot_text},
                    reply_markup=button,
                )
            except FloodWait as e:
                return await callback_query.answer(
                    f"FloodWait {e}, Please Waiting!!", True
                )

            except MessageNotModified:
                return

    elif prev_match:
        curr_page = int(prev_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page, HELPABLE, "help", is_bot=True)
                ),
            )
        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif next_match:
        next_page = int(next_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page, HELPABLE, "help", is_bot=True)
                ),
            )
        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif back_match:
        prev_page_num = int(back_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(prev_page_num, HELPABLE, "help", is_bot=True)
                ),
            )
        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return

    elif close_match:
        close_page = int(close_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: "✅ Help ditutup."
                },
                reply_markup=InlineKeyboardMarkup(None, "help")
            )
        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return

    elif create_match:
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help", is_bot=True)
                ),
            )
        except FloodWait as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return