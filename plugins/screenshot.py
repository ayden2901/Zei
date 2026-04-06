from pyrogram import Client, filters
import os
from datetime import datetime
from Navy import bot, navy
from Navy.helpers import CMD, ButtonUtils, Emoji
from config import (API_MAELYN, BOT_ID, BOT_NAME, HELPABLE, SUDO_OWNERS, URL_LOGO, ALIVE_PIC)
import subprocess

@CMD.UBOT("ss")
async def take_screenshot(client, message):
    if not os.path.exists("data"):
        os.makedirs("data")
    
    filepath = "data/screenshot.png"

    try:
        subprocess.run(["scrot", filepath], check=True)
        await client.send_photo("me", photo=filepath, caption="📸 Screenshot berhasil.")
        await message.reply_text("✅ Screenshot dikirim ke Pesan Tersimpan.")
    except Exception as e:
        await message.reply_text(f"❌ Gagal mengambil screenshot:\n`{e}`")