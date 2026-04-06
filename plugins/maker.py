import os
import shutil
import traceback
import uuid

import aiofiles
import aiohttp
from pyrogram.types import InputMediaPhoto
from pyrogram.enums import ParseMode
from config import API_MAELYN, API_BOTCHAX
from Navy.helpers import Bing, Emoji, Tools, animate_proses, CMD
from Navy.logger import logger


__MODULES__ = "ᴍᴀᴋᴇʀ"
__HELP__ = """<blockquote>Command Help **Maker**</blockquote>
<blockquote>**Image & Canvas Generator**</blockquote>
    <blockquote>**Text Only**
        `{0}maker sertifikat` (teks)</blockquote>
    <blockquote>**Reply Photo + Text**
        `{0}maker xnxx` (teks)</blockquote>
    <blockquote expandable>**Reply Photo Effects**
        `{0}maker hitam`
        `{0}maker ghibli`
        `{0}maker hijab`
        `{0}maker putih`
        `{0}maker gta`
        `{0}maker zombie`
        `{0}maker anime`
        `{0}maker cyberpunk`
        `{0}maker disney`
        `{0}maker pixar`
        `{0}maker cartoon`
        `{0}maker vangogh`
        `{0}maker pixelart`
        `{0}maker comicbook`
        `{0}maker tinggi`
        `{0}maker figure`</blockquote>

<b>   {1}</b>
"""

@CMD.UBOT("maker")
async def maker_img_cmd(client, message):
    em = Emoji(client)
    await em.get()

    if len(message.command) < 2:
        return await message.reply(
            f"<blockquote>{em.gagal}<b>Please give command!</b></blockquote>\n"
            f"<blockquote expandable>"
            f"{em.msg}<b>COMMAND:</b>\n"
            f"• sertifikat (teks) (reply photo)\n"
            f"• xnxx (teks) (reply photo)\n"
            f"• hitam (reply photo)\n"
            f"• ghibli (reply photo)\n"
            f"• hijab (reply photo)\n"
            f"• putih (reply photo)\n"
            f"• gta (reply photo)\n"
            f"• zombie (reply photo)\n"
            f"• anime (reply photo)\n"
            f"• cyberpunk (reply photo)\n"
            f"• disney (reply photo)\n"
            f"• pixar (reply photo)\n"
            f"• cartoon (reply photo)\n"
            f"• vangogh (reply photo)\n"
            f"• pixelart (reply photo)\n"
            f"• comicbook (reply photo)\n"
            f"• tinggi (reply photo)\n"
            f"• figure (reply photo)"
            f"</blockquote>",
            parse_mode=ParseMode.HTML
        )

    proses = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    cmd = message.command[1].lower()

    botcahx_endpoints = {
        "hitam": "jadihitam",
        "ghibli": "jadighibili",
        "hijab": "jadihijab",
        "putih": "jadiputih",
        "gta": "jadigta",
        "zombie": "jadizombie",
        "anime": "jadianime",
        "cyberpunk": "jadicyberpunk",
        "disney": "jadidisney",
        "pixar": "jadipixar",
        "cartoon": "jadicartoon",
        "vangogh": "jadivangogh",
        "pixelart": "jadipixelart",
        "comicbook": "jadicomicbook",
        "tinggi": "jadisdmtinggi",
        "figure": "tofigure"
    }

    try:
        async with aiohttp.ClientSession() as session:

            # =====================
            # SERTIFIKAT
            # =====================
            if cmd == "sertifikat":
                if len(message.command) < 3:
                    return await proses.edit("Give text!")

                text = " ".join(message.command[2:])
                url = f"https://api.siputzx.my.id/api/m/sertifikat-tolol?text={quote(text)}"

                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await proses.edit("API Error!")
                    result = await resp.read()

            # =====================
            # XNXX
            # =====================
            elif cmd == "xnxx":
                if len(message.command) < 3:
                    return await proses.edit(f"{em.gagal}Please give text!")

                if not reply or not reply.media:
                    return await proses.edit(f"{em.gagal}Reply photo first!")

                text = " ".join(message.command[2:])
                media = await reply.download()

                async with aiofiles.open(media, "rb") as f:
                    file_data = await f.read()

                url = "https://api.siputzx.my.id/api/canvas/xnxx"
                form = aiohttp.FormData()
                form.add_field("title", text)
                form.add_field(
                    "image",
                    file_data,
                    filename="image.jpg",
                    content_type="image/jpeg"
                )

                async with session.post(url, data=form) as resp:
                    if resp.status != 200:
                        os.remove(media)
                        return await proses.edit(f"{em.gagal}Failed to generate image.")
                    result = await resp.read()

                os.remove(media)

            # =====================
            # BOTCAHX
            # =====================
            elif cmd in botcahx_endpoints:
                if not reply or not reply.media:
                    return await proses.edit("Reply photo!")

                image_url = await Tools.upload_media(message)

                api_url = (
                    f"https://api.botcahx.eu.org/api/maker/{botcahx_endpoints[cmd]}"
                    f"?apikey={API_BOTCHAX}&url={image_url}"
                )

                async with session.get(api_url) as resp:
                    if resp.status != 200:
                        return await proses.edit("API Error!")
                    result = await resp.read()

            else:
                # ====== ELSE ASLI (TIDAK DIUBAH) ======
                return await proses.edit(
                    f"{em.gagal}<blockquote><b>Unknown maker command</b></blockquote>\n\n"
                    f"<blockquote expandable>"
                    f"{em.msg}<b>Available:</b>\n"
                    f"• sertifikat (teks) (reply photo)\n"
                    f"• xnxx (teks) (reply photo)\n"
                    f"• hitam (reply photo)\n"
                    f"• ghibli (reply photo)\n"
                    f"• hijab (reply photo)\n"
                    f"• putih (reply photo)\n"
                    f"• gta (reply photo)\n"
                    f"• zombie (reply photo)\n"
                    f"• anime (reply photo)\n"
                    f"• cyberpunk (reply photo)\n"
                    f"• disney (reply photo)\n"
                    f"• pixar (reply photo)\n"
                    f"• cartoon (reply photo)\n"
                    f"• vangogh (reply photo)\n"
                    f"• pixelart (reply photo)\n"
                    f"• comicbook (reply photo)\n"
                    f"• tinggi (reply photo)\n"
                    f"• figure (reply photo)"
                    f"</blockquote>",
                    parse_mode=ParseMode.HTML
                )

        # =====================
        # KIRIM HASIL
        # =====================
        file_path = f"{cmd}_{uuid.uuid4().hex}.jpg"
        with open(file_path, "wb") as f:
            f.write(result)

        await message.reply_photo(
            file_path,
            caption=f"{em.sukses}Successfully generated image."
        )

        os.remove(file_path)
        return await proses.delete()

    except Exception as e:
        return await proses.edit(f"{em.gagal}Error: {e}")