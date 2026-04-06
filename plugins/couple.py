import asyncio
import os
import html
from pyrogram.enums import ChatType, ParseMode

from pyrogram.types import InputMediaPhoto
from Navy import navy
from config import API_BOTCHAX
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses



__MODULES__ = "ᴄᴏᴜᴘʟᴇ"
__HELP__ = """<blockquote expandable>Command Help **COUPLE**</blockquote>

<blockquote>**ɢᴇᴛ ʀᴀɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ ᴘʜᴏᴛᴏ**</blockquote>
    **ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ʀᴀɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ ᴘʀᴏғɪʟᴇ ᴘʜᴏᴛᴏ**
        `{0}couple`

<b>   {1}</b>
"""


@CMD.UBOT("couple")
async def couple_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    url = f"https://api.botcahx.eu.org/api/wallpaper/couplepp?apikey={API_BOTCHAX}"

    msg = await animate_proses(message, em.proses)
    if not msg:
        return

    try:
        res = await Tools.get(url)

        if not res.get("status"):
            return await msg.edit("❌ Gagal mengambil data dari API.")

        male = res["result"]["male"]
        female = res["result"]["female"]

        male_photo = await Tools.get_media_data(male, "jpg")
        female_photo = await Tools.get_media_data(female, "jpg")

        media = [
            InputMediaPhoto(male_photo, caption="👨 Male"),
            InputMediaPhoto(female_photo, caption="👩 Female"),
        ]

        await message.reply_media_group(media)
        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error:\n`{e}`")