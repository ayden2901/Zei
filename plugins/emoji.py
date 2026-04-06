from pyrogram import Client, types
from pyrogram.types import Message
from pyrogram.enums import ParseMode, ChatType
from pyrogram.errors import ChatSendPhotosForbidden

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import datetime

from Navy.database import dB
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses
from config import DEVS
from Navy import bot, navy


__MODULES__ = "ᴇᴍᴏᴊɪ"
__HELP__ = """<blockquote>Command Help **Emoji**</blockquote>

<blockquote>**Set emoji ping**</blockquote>
    **You can set ping emoji with this command**
        `{0}setemoji ping` (emoji)

<blockquote>**Set emoji uptime**</blockquote>
    **You can set uptime emoji with this command**
        `{0}setemoji uptime` (emoji)

<blockquote>**Set emoji profil**</blockquote>
    **You can set profile emoji with this command**
        `{0}setemoji profil` (emoji)

<blockquote>**Set emoji robot**</blockquote>
    **You can set robot emoji with this command**
        `{0}setemoji robot` (emoji)

<blockquote>**Set emoji msg**</blockquote>
    **You can set msg emoji with this command**
        `{0}setemoji msg` (emoji)

<blockquote>**Set emoji warn**</blockquote>
    **You can set warn emoji with this command**
        `{0}setemoji warn` (emoji)

<blockquote>**Set emoji block**</blockquote>
    **You can set block emoji with this command**
        `{0}setemoji block` (emoji)

<blockquote>**Set emoji gagal**</blockquote>
    **You can set gagal emoji with this command**
        `{0}setemoji gagal` (emoji)

<blockquote>**Set emoji sukses**</blockquote>
    **You can set sukses emoji with this command**
        `{0}setemoji sukses` (emoji)

<blockquote>**Set emoji owner**</blockquote>
    **You can set owner emoji with this command**
        `{0}setemoji owner` (emoji)

<blockquote>**Set emoji klip**</blockquote>
    **You can set klip emoji with this command**
        `{0}setemoji klip` (emoji)

<blockquote>**Set emoji net**</blockquote>
    **You can set net emoji with this command**
        `{0}setemoji net` (emoji)

<blockquote>**Set emoji up**</blockquote>
    **You can set up emoji with this command**
        `{0}setemoji up` (emoji)

<blockquote>**Set emoji down**</blockquote>
    **You can set down emoji with this command**
        `{0}setemoji down` (emoji)

<blockquote>**Set emoji speed**</blockquote>
    **You can set speed emoji with this command**
        `{0}setemoji speed` (emoji)

<blockquote>**Set emoji proses**</blockquote>
    **You can set proses emoji with this command**
        `{0}setemoji proses` (emoji)

<blockquote>**Set emoji status**</blockquote>
    **You can set status emoji with this command**
        `{0}setemoji status` (emoji)

<blockquote>**Get id from message**</blockquote>
    **You can set id emoji or media with this command**
        `{0}id` (reply message)

<blockquote>**Get status emoji**</blockquote>
    **Get all youre emoji set**
        `{0}getemoji`
    
<blockquote>**Note**: Emoji only working on premium users.</blockquote>
    
<b>   {1}</b>
"""


@CMD.UBOT("id")
@CMD.DEV_CMD("id")
@CMD.FAKEDEV("id")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    chat = message.chat
    your_id = message.from_user if message.from_user else message.sender_chat
    message_id = message.id
    reply = message.reply_to_message

    text = f"<blockquote><b>{em.data}ʏᴏᴜʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>\n{em.owner}<b>ʏᴏᴜʀ ɪᴅ</b> : <code>{your_id.id}</code>\n{em.robot}<b>ᴍᴇssᴀɢᴇ ɪᴅ</b> : <code>{message_id}</code>\n{em.warn}<b>ᴄʜᴀᴛ ɪᴅ</b> : <code>{chat.id}</code></blockquote>\n"

    if reply:
        replied_user = reply.from_user if reply.from_user else reply.sender_chat
        if replied_user:
            text += f"<blockquote>{em.data}<b>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>\n{em.sukses}<b>ᴜsᴇʀ ɪᴅ</b> : <code>{replied_user.id}</code>\n{em.robot}<b>ᴍᴇssᴀɢᴇ ɪᴅ</b> : <code>{reply.id}</code></blockquote>\n"
        if reply.entities:
            for entity in reply.entities:
                if entity.custom_emoji_id:
                    text += f"<blockquote>{em.data}<b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴅᴀᴛᴀ</b>\n{em.robot}<b>ᴇᴍᴏᴊɪ ɪᴅ</b> : <code>{entity.custom_emoji_id}</code></blockquote>"
        if reply.photo:
            text += f"<blockquote>{em.data}<b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴅᴀᴛᴀ</b>\n{em.robot}<b>ғᴏᴛᴏ ɪᴅ</b> : <code>{reply.photo.file_id}</code></blockquote>"
        elif reply.video:
            text += f"<blockquote>{em.data}<b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴅᴀᴛᴀ</b>\n{em.robot}<b>ᴠɪᴅᴇᴏ ɪᴅ</b> : <code>{reply.video.file_id}</code></blockquote>"
        elif reply.sticker:
            text += f"<blockquote>{em.data}<b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴅᴀᴛᴀ</b>\n{em.robot}<b>sᴛɪᴄᴋᴇʀ ɪᴅ</b> : <code>{reply.sticker.file_id}</code></blockquote>"
        elif reply.animation:
            text += f"<blockquote>{em.data}<b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴅᴀᴛᴀ</b>\n{em.robot}<b>ɢɪғ ɪᴅ</b> : <code>{reply.animation.file_id}</code></blockquote>"
        elif reply.document:
            text += f"<blockquote>{em.data}<b>ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴅᴀᴛᴀ</b>\n{em.robot}<b>ᴅᴏᴄᴜᴍᴇɴᴛ ɪᴅ</b> : <code>{reply.document.file_id}</code></blockquote>"

    user = reply.from_user if reply and reply.from_user else message.from_user
    if not user:
        return await message.reply(f"{em.gagal} Tidak bisa mendapatkan Informasi Pengguna!")

    name = user.first_name + (f" {user.last_name}" if user.last_name else "")
    username = f"@{user.username}" if user.username else "None"
    dc_id = getattr(user, "dc_id", "Unknown")
    date = datetime.datetime.now().strftime("%d %b %Y")

    card = Image.open("storage/photo.png").convert("RGBA")
    card_width, card_height = card.size
    draw = ImageDraw.Draw(card)

    font_path = "storage/cache/font.ttf"
    font_bold = ImageFont.truetype(font_path, 32)
    font_label = ImageFont.truetype(font_path, 18)
    font_footer = ImageFont.truetype(font_path, 24)

# Download dan pasang foto profil dalam bentuk bulat
    try:
        if user.photo:
            pfp = await client.download_media(user.photo.big_file_id, file_name="pfp.jpg")
            pfp_img = Image.open(pfp).resize((205, 205)).convert("RGBA")

            mask = Image.new("L", (205, 205), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 203, 203), fill=277)

            pfp_bulat = Image.new("RGBA", (205, 205))
            pfp_bulat.paste(pfp_img, (0, 0), mask)

            if card.mode != "RGBA":
                card = card.convert("RGBA")

            card.paste(pfp_bulat, (83, 69), pfp_bulat)
    except Exception as e:
        print("Gagal ambil foto profil:", e)

    x_text = 320
    s_text = 320
    draw.text((s_text, 60), f"ID CARD TELEGRAM", font=font_bold, fill="blue")
    draw.text((x_text, 110), f"Name             : {name}", font=font_label, fill="black")
    draw.text((x_text, 140), f"User ID           : {user.id}", font=font_label, fill="black")
    draw.text((x_text, 170), f"Username   : {username}", font=font_label, fill="black")
    draw.text((x_text, 200), f"DC ID               : {dc_id}", font=font_label, fill="black")
    draw.text((x_text, 230), f"Date                 : {date}", font=font_label, fill="black")
    draw.text((195, card_height - 90), "CREATED BY @ydhinipapi", font=font_footer, fill="black")

    output = BytesIO()
    output.name = "id_card.jpg"
    card.convert("RGB").save(output, "JPEG")
    # Kirim foto + caption (gabung teks info dan ID card)
    if len(message.command) == 2:
         try:
             split = message.text.split(None, 1)[1].strip()
             user_id = (await client.get_users(split)).id
             text += f"<blockquote>{em.speed}<b>ᴍᴇɴᴛɪᴏɴᴇᴅ ᴜsᴇʀ ɪᴅ</b> : <code>{user_id}</code></blockquote>"
         except Exception:
             return await message.reply_text(f"{em.gagal}<b>ᴜsᴇʀ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ.</b>")

    try:
        await message.reply_photo(
            output,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    except ChatSendPhotosForbidden:
        await message.reply(
            f"{text}",
            parse_mode=ParseMode.HTML,
        )
 

@CMD.UBOT("getemoji")
@CMD.DEV_CMD("getemoji")
@CMD.FAKEDEV("getemoji")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await emo.get_costum_text()
    prem = client.me.is_premium
    pros = await animate_proses(message, emo.proses) 

    if not pros:
        return

    if message.command[0] == "getemoji":
        return await pros.edit(
            f"<blockquote expandable><b>❏ Emoji anda saat ini:</b>\n├ Ping: {emo.ping}\n├ Msg: {emo.msg}\n├ Sukses: {emo.sukses}\n├ Gagal: {emo.gagal}\n├ Proses: {emo.proses}\n├ Warn: {emo.warn}\n├ Block: {emo.block}\n├ Owner: {emo.owner}\n├ Uptime: {emo.uptime}\n├ Robot: {emo.robot}\n├ Klip: {emo.klip}\n├ Net: {emo.net}\n├ Up: {emo.up}\n├ Down: {emo.down}\n├ Speed: {emo.speed}\n├ Data: {emo.data}\n├ Ket: {emo.ket}\n├ Afk: {emo.afk}\n├ Pin: {emo.pin}\n├ Paranormal: {emo.paranormal}\n├ Saya: {emo.saya}\n├ Jodoh: {emo.jodoh}\n├ Love: {emo.love}\n╰ Profil: {emo.profil}</b></blockquote>"
        )

    elif len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(
            f"{emo.gagal}<b>Gunakan Format : <code>setemoji [value]</code></b>"
        )
    variable = message.command[1].lower() if len(message.command) > 1 else None
    value = None
    emoji_id = None

    if message.reply_to_message:
        value = message.reply_to_message.text or message.reply_to_message.caption
        if prem and message.reply_to_message.entities:
            for entity in message.reply_to_message.entities:
                if entity.custom_emoji_id:
                    emoji_id = entity.custom_emoji_id
                    break
    elif len(message.command) >= 3:
        value = " ".join(message.command[2:])
        if prem and message.entities:
            for entity in message.entities:
                if entity.custom_emoji_id:
                    emoji_id = entity.custom_emoji_id
                    break

    valid_variables = [
        "ping",
        "msg",
        "warn",
        "block",
        "proses",
        "gagal",
        "sukses",
        "profil",
        "owner",
        "robot",
        "klip",
        "net",
        "up",
        "down",
        "speed",
        "uptime",
        "data",
        "ket",
        "afk",
        "pin",
        "paranormal",
        "saya",
        "jodoh",
        "love"
    ]
    if (
        not variable
        or variable not in valid_variables
        or not value
        and variable != "status"
    ):
        return await pros.edit(f"{emo.gagal}<b>Query tidak ditemukan!</b>!")
    if variable == "status":
        return await set_emoji_status(client, message)

    if prem and emoji_id:
        await dB.set_var(client.me.id, f"emo_{variable}", emoji_id)
        return await pros.edit(
            f"{emo.sukses}<b>Berhasil set Emoji {variable.capitalize()} menjadi:</b> <emoji id={emoji_id}>{value}</emoji>"
        )

    await dB.set_var(client.me.id, f"emo_{variable}", value)
    return await pros.edit(
        f"{emo.sukses}<b>Berhasil set Emoji {variable.capitalize()} menjadi:</b> {value}"
    )


@CMD.UBOT("setemoji")
@CMD.DEV_CMD("setemoji")
@CMD.FAKEDEV("setemoji")
async def setemoji_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    prem = client.me.is_premium

    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await emo.get_costum_text()
    pros = await animate_proses(message, emo.proses) 

    if not pros:
        return

    # HARUS REPLY
    rep = message.reply_to_message
    if not rep:
        return await pros.edit(
            f"{emo.gagal}<b>Silahkan balas Custom Emoji Premium.</b>"
        )

    # ambil custom emoji id
    emoji_id = None
    if prem and rep.entities:
        for entity in rep.entities:
            if entity.custom_emoji_id:
                emoji_id = entity.custom_emoji_id
                break

    if not emoji_id:
        return await pros.edit(
            f"{emo.gagal}<b>Custom Emoji tidak ditemukan.</b>"
        )

    # ===============================
    # 1️⃣ .setemoji  → set STATUS akun
    # ===============================
    if len(message.command) == 1:
        if not prem:
            return await pros.edit(
                f"{emo.gagal}<b>Anda bukan pengguna Telegram Premium.</b>"
            )

        await client.set_emoji_status(
            types.EmojiStatus(custom_emoji_id=emoji_id)
        )
        return await pros.edit(
            f"{emo.sukses}<b>Status Emoji berhasil diubah:</b> "
            f"<emoji id={emoji_id}>🙂</emoji>"
        )

    # =========================================
    # 2️⃣ .setemoji <variable> → set emoji config
    # =========================================
    if len(message.command) == 2:
        variable = message.command[1].lower()

        valid_variables = [
            "ping", "msg", "warn", "saya",
            "block", "proses", "gagal",
            "sukses", "profil", "owner",
            "robot", "klip", "net", "up",
            "down", "speed", "uptime",
            "data", "ket", "afk", "pin",
            "paranormal", "jodoh", "love"
        ]

        if variable not in valid_variables:
            return await pros.edit(
                f"{emo.gagal}<b>Variable tidak valid!</b>"
            )

        await dB.set_var(client.me.id, f"emo_{variable}", emoji_id)
        return await pros.edit(
            f"{emo.sukses}<b>Emoji {variable.capitalize()} berhasil diubah:</b> "
            f"<emoji id={emoji_id}>🙂</emoji>"
        )

    # ===============================
    # 3️⃣ selain itu → error
    # ===============================
    return await pros.edit(
        f"{emo.gagal}<b>Format perintah tidak valid.</b>"
    )