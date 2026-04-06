__MODULES__ = "ʀᴇᴍɪɴɪ"
__HELP__ = """<blockquote>Command Help **Remini**</blockquote>

<blockquote>**Enchancer image** </blockquote>
    **Change image to hd with this command**
        `{0}remini` (reply image)

<b>   {1}</b>
"""

from config import API_MAELYN, API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools
from PIL import Image
import io
import httpx


@CMD.UBOT("remini")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")

    rep = message.reply_to_message or message
    if len(message.command) < 2 and not rep:
        return await prs.edit(f"{em.gagal}**Please reply to image or give link!**")

    # Ambil media atau link
    if rep and rep.media:
        arg = await Tools.upload_media(message)
    else:
        arg = client.get_text(message)
        if not arg.startswith("https://"):
            return await prs.edit(f"{em.gagal}**Please give valid link or reply media**")

    # Ambil resolusi (untuk Botcahx)
    try:
        resolusi = int(message.command[1])
        if resolusi not in [16, 32, 64]:
            resolusi = 16
    except (IndexError, ValueError):
        resolusi = 16

    # ==============================
    # 1️⃣ COBA API MAELYN DULU
    # ==============================
    try:
        url_maelyn = f"https://api.maelyn.tech/api/img2img/remini?url={arg}&apikey={API_MAELYN}"
        respon = await Tools.fetch.get(url_maelyn)

        if respon and respon.status_code == 200:
            data = respon.json()
            result = data.get("result")

            if result:
                image_url = result.get("url")
                type_img = result.get("type", "Unknown")
                size_img = result.get("size", "-")
                expired = result.get("expired", "-")

                await prs.delete()
                return await message.reply_photo(
                    image_url,
                    caption=f"{em.sukses}**API**: Maelyn\n**Type**: {type_img}\n**Size**: {size_img}\n**Expired**: {expired}"
                )
    except:
        pass  # Kalau error langsung lanjut fallback

    # ==============================
    # 2️⃣ FALLBACK KE BOTCAHX
    # ==============================
    try:
        await prs.edit(f"{em.proses}**Maelyn failed, trying Botcahx...**")

        url_botcahx = f"https://api.botcahx.eu.org/api/tools/remini-v4?url={arg}&resolusi={resolusi}&apikey={API_BOTCHAX}"
        respon = await Tools.fetch.get(url_botcahx)

        if not respon or respon.status_code != 200:
            return await prs.edit(f"{em.gagal}**Both APIs failed! ({respon.status_code if respon else 'No Response'})**")

        data = respon.json()
        image_url = data.get("url")
        type_img = data.get("type", "Unknown")
        expired = data.get("expired", "-")

        if not image_url:
            return await prs.edit(f"{em.gagal}**Botcahx returned no image**")

        # Ambil ukuran gambar
        size_img = "-"
        async with httpx.AsyncClient() as client_fetch:
            resp_img = await client_fetch.get(image_url)
            if resp_img.status_code == 200:
                try:
                    img = Image.open(io.BytesIO(resp_img.content))
                    size_img = f"{img.width}x{img.height}"
                except:
                    size_img = "-"

        await prs.delete()
        return await message.reply_photo(
            image_url,
            caption=f"{em.sukses}**API**: Botcahx\n**Type**: {type_img}\n**Size**: {size_img}\n**Expired**: {expired}\n**Resolution**: {resolusi}"
        )

    except Exception as er:
        await prs.delete()
        return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")