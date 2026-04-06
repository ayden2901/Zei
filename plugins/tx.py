import asyncio
import sys
from datetime import datetime, timezone

from pytz import timezone

from Navy import *
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task


__MODULES__ = "ᴅᴏɴᴇ"
__HELP__ = """<blockquote>Command Help **Done**</blockquote>

<blockquote>**Transaksi**</blockquote>
    **Display transaction receipt**
        `{0}done` [item,price,payment]
    
<b>   {1}</b>
"""

@CMD.UBOT("done")
async def done_command(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"<b>{em.proses}{proses_}</b>")
    await asyncio.sleep(5)
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2 or "," not in args[1]:
            await message.reply_text(f"{em.owner}<b>Penggunaan: `done` name item,price,payment</b>")
            return

        parts = args[1].split(",", 2)

        if len(parts) < 2:
            await message.reply_text(f"{em.owner}<b>Penggunaan: `done` name item,price,payment</b>")
            return

        name_item = parts[0].strip()
        price = parts[1].strip()
        payment = parts[2].strip() if len(parts) > 2 else "Lainnya"
        time = datetime.now(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
        response = (
            f"「 𝗧𝗥𝗔𝗡𝗦𝗔𝗞𝗦𝗜 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟 」\n\n"
            f"📦 <b>Barang : {name_item}</b>\n"
            f"💸 <b>Nominal : {price}</b>\n"
            f"🕰️ <b>Waktu : {time}</b>\n"
            f"💬 <b>Payment : {payment}</b>\n\n"
            f"𝗧𝗲𝗿𝗶𝗺𝗮𝗸𝗮𝘀𝗶𝗵 𝗧𝗲𝗹𝗮𝗵 𝗢𝗿𝗱𝗲𝗿"
        )
        await proses.edit(response)

    except Exception as e:
        await proses.edit(f"{em.gagal}Error failed {e}")
