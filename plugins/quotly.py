import base64
import io
import json
import os
import random
from io import BytesIO

from config import SUDO_OWNERS
from Navy.helpers import CMD, Emoji, Quotly

__MODULES__ = "ǫᴜᴏᴛʟʏ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ǫᴜᴏᴛʟʏ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ǫᴜᴏᴛʟʏ</b>
    ➢ `{0}q` [ᴄᴏʟᴏʀ] [ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ]
    ➢ `{0}q @ydhinistar` [ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ]
    ➢ `{0}qcolor`</blockquote>

<b>   {1}</b>
"""


async def consu(dok):
    try:
        with open(dok, "rb") as file:
            data_bytes = file.read()
        json_data = json.loads(data_bytes)
        image_data_base64 = json_data.get("image")
        if not image_data_base64:
            raise ValueError("Tidak ada data gambar dalam JSON")
        image_data = base64.b64decode(image_data_base64)
        image_io = io.BytesIO(image_data)
        image_io.name = "Quotly.webp"
        return image_io
    except Exception as e:
        raise e


@CMD.UBOT("qcolor")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    iymek = f"\n•".join(Quotly.loanjing)
    jadi = f"{em.sukses}Color for quotly\n•"
    if len(iymek) > 4096:
        with open("qcolor.txt", "w") as file:
            file.write(iymek)
        await message.reply_document(
            "qcolor.txt", caption=f"{em.sukses}Color for quotly"
        )
        os.remove("qcolor.txt")
        return
    else:
        return await message.reply(jadi + iymek)


@CMD.UBOT("q|qr")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    acak = None
    messages = None
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses}{proses_}")
    if not message.reply_to_message:
        return await pros.edit("{}Please reply to message!!".format(em.gagal))
    is_reply = bool(message.command[0].endswith("r"))
    rep = message.reply_to_message
    if len(message.command) > 1:
        tag = message.command[1].strip()
        if tag.startswith("@"):
            user_id = tag[1:]
            try:
                org = await client.get_users(user_id)
                if org.id in SUDO_OWNERS:
                    await pros.edit(f"{em.gagal}You can't quote this user")
                    return
                rep = await client.get_messages(
                    message.chat.id, message.reply_to_message.id, replies=0
                )
                rep.from_user = org
                messages = [rep]
            except Exception as e:
                return await pros.edit(f"{em.gagal}{e}")
            warna = message.text.split(None, 2)[2] if len(message.command) > 2 else None
            if warna:
                acak = warna
            else:
                acak = random.choice(Quotly.loanjing)
            hasil = await Quotly.quotly(messages, acak, is_reply=is_reply)
            bio_sticker = BytesIO(hasil)
            bio_sticker.name = "biosticker.webp"
            await message.reply_sticker(bio_sticker)
            return await pros.delete()
        elif not tag.startswith("@"):
            warna = message.text.split(None, 1)[1] if len(message.command) > 1 else None
            if warna:
                acak = warna
            else:
                acak = random.choice(Quotly.loanjing)
            m_one = await client.get_messages(
                chat_id=message.chat.id,
                message_ids=message.reply_to_message.id,
                replies=0,
            )
            messages = [m_one]
            hasil = await Quotly.quotly(messages, acak, is_reply=is_reply)
            bio_sticker = BytesIO(hasil)
            bio_sticker.name = "biosticker.webp"
            await message.reply_sticker(bio_sticker)
            return await pros.delete()
        elif int(tag):
            if int(tag) > 10:
                return await pros.edit(f"{em.gagal}Max 10 messages")
            warna = message.text.split(None, 2)[2] if len(message.command) > 2 else None
            if warna:
                acak = warna
            else:
                acak = random.choice(Quotly.loanjing)
            messages = [
                i
                for i in await client.get_messages(
                    chat_id=message.chat.id,
                    message_ids=range(
                        message.reply_to_message.id,
                        message.reply_to_message.id + int(tag),
                    ),
                    replies=0,
                )
                if not i.empty and not i.media
            ]
            hasil = await Quotly.quotly(messages, acak, is_reply=is_reply)
            bio_sticker = BytesIO(hasil)
            bio_sticker.name = "biosticker.webp"
            await message.reply_sticker(bio_sticker)
            return await pros.delete()
    else:
        acak = random.choice(Quotly.loanjing)
        m_one = await client.get_messages(
            chat_id=message.chat.id, message_ids=message.reply_to_message.id, replies=0
        )
        messages = [m_one]
    try:
        hasil = await Quotly.quotly(messages, acak, is_reply=is_reply)
        bio_sticker = BytesIO(hasil)
        bio_sticker.name = "biosticker.webp"
        await message.reply_sticker(bio_sticker)
        await pros.delete()
        return
    except Exception as e:
        return await pros.edit(f"{em.gagal}{e}")
