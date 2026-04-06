from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pyrogram.types import Message
import re
import os
import storage
from Navy.helpers import CMD, Emoji
from Navy.helpers.emoji_logs import emotikon
from Navy import navy
import aiohttp


@CMD.UBOT("brat")
async def brat_handler(client, message: Message):
    em = Emoji(client)
    await em.get()
    proses_ = (await em.get_costum_text())[4]
    msg = await message.reply_text(f"<b>{em.proses}{proses_}</b>")

    # Ambil input teks dan mode
    input_text = message.text.split(maxsplit=1)
    text = None
    mode = "normal"

    if len(input_text) == 2:
        if input_text[1].lower().startswith("tr "):
            mode = "transparan"
            text = input_text[1][3:].strip()
        else:
            text = input_text[1].strip()
    elif message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    else:
        return await msg.edit_text(f"<b>{em.gagal}Berikan teks atau reply untuk dibuat sticker!</b>")

    if not text:
        return await msg.edit_text(f"<b>{em.gagal}Teks tidak ditemukan!</b>")

    try:
        # Pilih font dari daftar yang tersedia
        font_paths = [
            "storage/Symbola.ttf",
            "storage/symbola_hint.ttf",
            "storage/Acme-Regular.ttf",
            "storage/seguiemj.ttf"
        ]
        font_path = next((f for f in font_paths if os.path.exists(f)), None)
        if not font_path:
            return await msg.edit_text("<b>❌ Font emoji tidak ditemukan di sistem.</b>")

        # Konfigurasi dasar
        image_size = 400
        padding = 25
        base_font_size = 80

        # Warna tergantung mode
        bg_color = (0, 0, 0, 0) if mode == "transparan" else (255, 255, 255, 255)
        text_color = (255, 255, 255, 255) if mode == "transparan" else (0, 0, 0, 255)

        # Buat dummy image untuk ukur teks
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)

        def wrap_text(draw, font, text, max_width):
            words = text.split()
            lines = []
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width - 2 * padding:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
            return lines

        # Cari ukuran font optimal
        font_size = base_font_size
        while font_size >= 20:
            font = ImageFont.truetype(font_path, font_size)
            lines = wrap_text(dummy_draw, font, text, image_size)
            line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
            total_height = line_height * len(lines)
            if total_height <= image_size - 2 * padding:
                break
            font_size -= 2

        # Gambar final
        image = Image.new("RGBA", (image_size, image_size), bg_color)
        draw = ImageDraw.Draw(image)
        y = (image_size - total_height) // 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (image_size - line_width) // 2
            draw.text((x, y), line, font=font, fill=text_color)
            y += line_height

        # Simpan jadi sticker
        output = BytesIO()
        output.name = "brat.webp"
        image.save(output, "WEBP")
        output.seek(0)

        await msg.delete()
        return await message.reply_sticker(output)

    except Exception as e:
        return await msg.edit_text(f"<b>{em.gagal}Terjadi error:\n<code>{str(e)}</code></b>")



__MODULES__ = "ʙʀᴀᴛ"
__HELP__ = """<blockquote>Command Help **Brat**</blockquote>

<blockquote>**Make brat text** </blockquote>
    **You can make brat the message with this message**
        `{0}brat` (reply message)

<b>   {1}</b>
"""
