import asyncio
from Navy import bot, navy
from pyrogram import Client
from pyrogram.types import Message
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, task, animate_proses
from datetime import datetime, timedelta



__MODULES__ = "ᴛʀᴀɴsғᴇʀ"
__HELP__ = """<blockquote>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **ᴛʀᴀɴsғᴇʀ**</blockquote>

<blockquote>**ᴛʜɪs ɪs ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜᴇ ғᴀᴋᴇ ᴛʀᴀɴsғᴇʀ ᴄᴏᴍᴍᴀɴᴅ.** </blockquote>
    **ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ғᴀᴋᴇ ᴛʀᴀɴsғᴇʀ ᴄᴏᴍᴍᴀɴᴅ**
        `{0}tf` (ɴᴏᴍɪɴᴀʟ) (ʙᴀɴᴋ/ᴇ-ᴡᴀʟʟᴇᴛ) (ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ)

<b>   {1}</b>
"""


# ================= TERBILANG =================
def terbilang(n):
    angka = [
        "", "Satu", "Dua", "Tiga", "Empat", "Lima",
        "Enam", "Tujuh", "Delapan", "Sembilan",
        "Sepuluh", "Sebelas"
    ]

    n = int(n)

    if n < 12:
        return angka[n]
    elif n < 20:
        return terbilang(n - 10) + " Belas"
    elif n < 100:
        return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200:
        return "Seratus " + terbilang(n - 100)
    elif n < 1000:
        return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000:
        return "Seribu " + terbilang(n - 1000)
    elif n < 1_000_000:
        return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1_000_000_000:
        return terbilang(n // 1_000_000) + " Juta " + terbilang(n % 1_000_000)
    elif n < 1_000_000_000_000:
        return terbilang(n // 1_000_000_000) + " Miliar " + terbilang(n % 1_000_000_000)
    elif n < 1_000_000_000_000_000:
        return terbilang(n // 1_000_000_000_000) + " Triliun " + terbilang(n % 1_000_000_000_000)
    else:
        return "Nominal Terlalu Besar"

# ============= DATE =============

def format_waktu_id():
    bulan = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    now_utc = datetime.utcnow()

    # AUTO zona (Indonesia)
    jam = now_utc.hour

    if jam + 7 < 24:
        zona, offset = "WIB", 7
    elif jam + 8 < 24:
        zona, offset = "WITA", 8
    else:
        zona, offset = "WIT", 9

    now_id = now_utc + timedelta(hours=offset)

    return f"{now_id.day:02d}/{bulan[now_id.month]}/{now_id.year}, {now_id:%H.%M} {zona}"

# ================= COMMAND TRANSFER =================
@CMD.UBOT("tf")
async def transfer(client: Client, message: Message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    pros = await animate_proses(message, em.proses)
    if not pros:
        return

    # wajib reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await pros.edit(f"{em.gagal}Reply ke user yang ingin ditransfer")

    if len(message.command) < 3:
        return await pros.edit(f"{em.gagal}Gunakan: `.tf <nominal> <bank/e-wallet>`")

    try:
        nominal = int(message.command[1])
        if nominal <= 0:
            return await pros.edit(f"{em.gagal}Nominal harus lebih dari 0")
    except ValueError:
        return await pros.edit(f"{em.gagal}Nominal harus berupa angka")

    via = message.command[2].upper()

    from_user = message.from_user
    to_user = message.reply_to_message.from_user

    mention_from = from_user.mention
    mention_to = to_user.mention

    waktu = format_waktu_id()
    nominal_rp = f"Rp{nominal:,}".replace(",", ".")
    pembilang = terbilang(nominal).strip() + " Rupiah"

    text = f"""
<blockquote>ㅤㅤㅤ{em.sukses}𝗧𝗥𝗔𝗡𝗦𝗙𝗘𝗥 𝗗𝗢𝗡𝗘{em.sukses}</blockquote>
<blockquote>{em.owner}𝗙𝗥𝗢𝗠 : {mention_from}
{em.profil}𝗧𝗢 : {mention_to}
{em.msg}𝗡𝗢𝗠𝗜𝗡𝗔𝗟 : <code>{nominal_rp}</code>
{em.uptime}𝗗𝗔𝗧𝗘 : <code>{waktu}</code>
{em.klip}𝗕𝗔𝗡𝗞/𝗘-𝗪𝗔𝗟𝗟𝗘𝗧 : <code>{via}</code>
{em.data}𝗣𝗘𝗠𝗕𝗜𝗟𝗔𝗡𝗚 : <i>Terbilang {pembilang}</i></blockquote>
<blockquote>{em.robot}<b>©️ᴄᴏᴘʏʀɪɢʜᴛ ʙʏ</b> @StarBotDevs</blockquote>
"""

    await pros.edit(text)