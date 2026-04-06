import asyncio
import sys
from datetime import datetime, timezone

from pytz import timezone

from Navy import *
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses


@CMD.UBOT("tx")
async def done_command(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await animate_proses(message, em.proses)
    await asyncio.sleep(5)
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2 or "," not in args[1]:
            await message.reply_text(f"{em.owner}<b>Penggunaan: `{0}done` name item,price,payment</b>")
            return

        parts = args[1].split(",", 2)

        if len(parts) < 2:
            await message.reply_text(f"{em.owner}<b>Penggunaan: `{0}done` name item,price,payment</b>")
            return

        name_item = parts[0].strip()
        price = parts[1].strip()
        payment = parts[2].strip() if len(parts) > 2 else "Lainnya"
        time = datetime.now(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
        response = (
            f"「 <b>• Hones Review For •</b> 」\n\n"
            f"<emoji id=6283073379184415506>🎁</emoji> <b>Barang : {name_item}</b>\n"
            f"<emoji id=6185807599884047344>💵</emoji> <b>Nominal : Rp. {price}</b>\n"
            f"<emoji id=6185851228161840333>🗓️</emoji> <b>Waktu : {time}</b>\n"
            f"<emoji id=6188426477667619174>🔗</emoji> <b>Payment : {payment}</b>\n"
            f"<emoji id=6185989569058444369>⭐️</emoji> <b>Isi rate komen nya kak : <a href=https://t.me/astrophilemarket/74>Klik Di Sini</a></b>"
        )
        await proses.edit(response)

    except Exception as e:
        await proses.edit(f"{em.gagal}Error failed {e}")
