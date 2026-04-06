import asyncio
import os

import requests
from bs4 import BeautifulSoup

from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ǫʀ ᴄᴏᴅᴇ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ǫʀ ᴄᴏᴅᴇ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ǫʀ ᴄᴏᴅᴇ</b>
    ➢ `{0}qr gen` [ᴄᴏᴅᴇ]
    ➢ `{0}qr read` [ʀᴇᴘʟʏ ɪᴍᴀɢᴇ]</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("qr")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give valid query `{message.text.split()[0]}` [gen or read]!**"
        )
    query = message.command[1]
    reply = message.reply_to_message or message

    if query == "gen":
        if not reply or reply and not reply.text:
            return await proses.edit(f"{em.gagal}**Please give barcode text**")
        text = reply.text or reply.caption
        data = (
            Tools.qr_gen(text)
            if reply
            else Tools.qr_gen(message.text.split(None, 2)[2])
        )
        try:
            QRcode = (
                requests.post(
                    "https://api.qrcode-monkey.com//qr/custom",
                    json=data,
                )
                .json()["imageUrl"]
                .replace("//api", "https://api")
            )
            await client.send_photo(
                message.chat.id, QRcode, reply_to_message_id=reply.id
            )
            return await proses.delete()
        except Exception as error:
            return await proses.edit(f"{em.gagal}**ERROR**: {str(error)}")

    elif query == "read":
        if not (reply and reply.media and (reply.photo or reply.sticker)):
            await proses.edit(f"{em.gagal}**Please reply to valid barcode!**")
            return
        if not os.path.isdir("storage/cache/"):
            os.makedirs("storage/cache/")
        down_load = await client.download_media(
            message=reply, file_name="storage/cache/"
        )
        cmd = [
            "curl",
            "-X",
            "POST",
            "-F",
            "f=@" + down_load + "",
            "https://zxing.org/w/decode",
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        out_response = stdout.decode().strip()
        err_response = stderr.decode().strip()
        os.remove(down_load)
        if not (out_response or err_response):
            await process.edit(f"{em.gagal}**Something error, try again!**")
            return
        try:
            soup = BeautifulSoup(out_response, "html.parser")
            qr_contents = soup.find_all("pre")[0].text
        except IndexError:
            await process.edit(f"{em.gagal}**Something error, try again!**")
            return
        return await proses.edit(
            f"{em.sukses}<b>Qr Text:</b>\n<code>{qr_contents}</code>"
        )
