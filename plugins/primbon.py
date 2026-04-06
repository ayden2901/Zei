import asyncio
import io
import os
import random
import traceback
from uuid import uuid4

import aiofiles
from google import genai
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from pyrogram.errors import MessageTooLong

from Navy import bot, navy
from urllib.parse import quote
from config import API_GEMINI, API_MAELYN, LOLHUMAN_KEY, API_BOTCHAX
from Navy.logger import logger
from Navy.database import state
from Navy.helpers import Bing, ButtonUtils, Emoji, Tools, animate_proses, CMD



MAX_MEDIA_PER_BATCH = 7

MAX_CAPTION_LENGTH = 700

DEFAULT_CERPEN_IMAGE = "https://files.catbox.moe/hnjkpt.jpg"

IMAGE_RESULT = "https://primbon.com/ramalan_kecocokan_cinta2.png"

def split_message(text, length=824):
    return [text[i : i + length] for i in range(0, len(text), length)]



__MODULES__ = "ᴘʀɪᴍʙᴏɴ"
__HELP__ = """<blockquote>Command Help **ᴘʀɪᴍʙᴏɴ**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search ᴘʀɪᴍʙᴏɴ for arti nama**
        `{0}artinama` (question)
    **Search ᴘʀɪᴍʙᴏɴ for tafsir mimpi**
        `{0}artimimpi` (question)
    **Search ᴘʀɪᴍʙᴏɴ for zodiak**
        `{0}zodiak` (query)</blockquote>
    **Search ᴘʀɪᴍʙᴏɴ for soulmate**
        `{0}cekjodoh` (nama1&nama2)</blockquote>
<b>   {1}</b>
"""



@CMD.UBOT("artinama|nama")
async def artiname_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)
    if message.reply_to_message:
        if message.reply_to_message.sender_chat:
            nama = message.reply_to_message.sender_chat.title
        elif message.reply_to_message.from_user:
            nama = message.reply_to_message.from_user.first_name
            if message.reply_to_message.from_user.last_name:
                nama = f"{message.reply_to_message.from_user.first_name} {message.reply_to_message.from_user.last_name or ''}"
        else:
            return await proses.edit(f"{em.gagal} <b>Name not found!</b>")
    else:
        if len(message.command) < 2:
            return await proses.edit(
                f"{em.gagal}<b>You need to specify a user (either by reply user or give name)!</b>"
            )
        try:
            nama = message.text.split()[1]
        except IndexError:
            return await proses.edit(
                f"{em.gagal} <b>Please reply message or give name.</b>"
            )

    url = f"https://api.botcahx.eu.org/api/primbon/artinama?apikey={API_BOTCHAX}&nama={nama}"

    rp = await Tools.fetch.get(url)
    if rp.status_code != 200:
        return await proses.edit(f"{em.gagal} <b>Please try again later.</b>")

    data = rp.json()
    if not data.get("status"):
        return await proses.edit(f"{em.gagal} <b>Name not found in data!</b>")

    nama_res = data["data"]["nama"].title()
    arti_res = data["data"]["arti"]
    catatan_res = data["data"].get("catatan", "")

    reply_text = (
        f"<blockquote expandable>**🔍 Arti Nama: {nama_res}**\n\n"
        f"<b>📖 {arti_res}</b>\n</blockquote>"
    )
    if catatan_res:
        reply_text += f"<b>\n💡 <i>{catatan_res}</i></b>"

    return await proses.edit(reply_text)


@CMD.UBOT("zodiak|zodiac")
async def zodiak_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)
    ZODIAK_LIST = [
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagitarius",
        "capricorn",
        "aquarius",
        "pisces",
    ]
    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give zodiak name\n\n<code>{', '.join([z.capitalize() for z in ZODIAK_LIST])}</code>**"
        )
    try:
        query = message.text.split(None, 1)[1].strip().lower()
    except IndexError:
        return await proses.edit(
            f"{em.gagal} <b>Please give zodiak name!\n\nExample:</b> <code>{message.text.split()[0]} gemini</code>"
        )
    if query not in ZODIAK_LIST:
        return await proses.edit(
            f"{em.gagal} <b>Zodiak not found!</b>\n\n"
            f"<b>Daftar Zodiak:</b>\n"
            f"<code>{', '.join([z.capitalize() for z in ZODIAK_LIST])}</code>"
        )
    url = f"https://api.botcahx.eu.org/api/primbon/zodiak?apikey={API_BOTCHAX}&zodiak={query}"
    rp = await Tools.fetch.get(url)

    if rp.status_code != 200:
        return await proses.edit(f"{em.gagal} <b>Gagal mengambil data dari API.</b>")

    data = rp.json()
    if not data.get("status"):
        return await proses.edit(
            f"{em.gagal} <b>Data tidak ditemukan untuk zodiak ini.</b>"
        )

    z = data["data"]
    teks = (
        f"<b>♈ Zodiak:</b> {z['zodiak']}\n"
        f"<b>🔢 Nomor Keberuntungan:</b> {z['nomor_keberuntungan']}\n"
        f"<b>🌸 Aroma Keberuntungan:</b> {z['aroma_keberuntungan']}\n"
        f"<b>🪐 Planet Penguasa:</b> {z['planet_yang_mengitari']}\n"
        f"<b>🌼 Bunga Keberuntungan:</b> {z['bunga_keberuntungan']}\n"
        f"<b>🎨 Warna Keberuntungan:</b> {z['warna_keberuntungan']}\n"
        f"<b>💎 Batu Keberuntungan:</b> {z['batu_keberuntungan']}\n"
        f"<b>🌪️ Elemen:</b> {z['elemen_keberuntungan']}\n\n"
        f"<b>❤️ Pasangan Zodiak & Kepribadian:</b>\n<blockquote>{z['pasangan_zodiak']}</blockquote>"
    )

    return await proses.edit(f"<blockquote expandable>{teks}</blockquote>")


@CMD.UBOT("artimimpi|mimpi")
async def tafsir_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)

    prompt = client.get_text(message)
    if not prompt:
        return await proses.edit(
            f"{em.gagal} <b>Enter the dream text to interpret.</b>"
        )

    url = f"https://api.botcahx.eu.org/api/primbon/artimimpi?mimpi={prompt}&apikey={API_BOTCHAX}"
    response = await Tools.fetch.get(url)
    if response.status_code != 200:
        return await proses.edit(
            f"{em.gagal} <b>Server is having problems, please try again later.</b>"
        )

    data = response.json().get("data")
    if not data:
        return await proses.edit(f"{em.gagal} <b>Data not found.</b>")

    keyword = data.get("keyword", "Tidak diketahui")
    hasil_list = data.get("hasil", [])
    total = data.get("total", "0")
    solusi = data.get("solusi", "")

    hasil_teks = ""
    if hasil_list:
        hasil_teks = "\n".join(f"• {item}" for item in hasil_list)
    else:
        hasil_teks = "<i>(There is no direct interpretation for this dream.)</i>"

    solusi_teks = solusi.strip().replace("      ", "").replace("\n", "\n")

    teks = (
        f"<b>🌙 Tafsir Mimpi</b>\n\n"
        f"<b>🔑 Keyword:</b> {keyword}\n"
        f"<b>📊 Total Ditemukan:</b> {total}\n\n"
        f"<b>📖 Hasil Tafsir:</b>\n{hasil_teks}\n\n"
        f"<b>💡 Solusi:</b>\n<blockquote expandable>{solusi_teks}</blockquote>"
    )

    return await proses.edit(teks)


@CMD.UBOT("cekjodoh")
async def cekjodoh_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)

    user = message.from_user
    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    # Validasi input
    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}<b>Gunakan format:</b> <code>.cekjodoh nama1&nama2</code>"
        )

    try:
        query = message.text.split(None, 1)[1]

        if "&" not in query:
            return await proses.edit(
                f"{em.gagal}<b>Format salah!</b>\nGunakan: <code>.cekjodoh nama1&nama2</code>"
            )

        nama1, nama2 = query.split("&", 1)
        nama1 = nama1.strip()
        nama2 = nama2.strip()

        if not nama1 or not nama2:
            return await proses.edit(
                f"{em.gagal}<b>Kedua nama harus diisi!</b>"
            )

    except Exception:
        return await proses.edit(
            f"{em.gagal}<b>Terjadi kesalahan saat membaca nama.</b>"
        )

    # Encode nama (lebih aman dari replace)
    nama1_url = quote(nama1)
    nama2_url = quote(nama2)

    url = (
        f"https://api.botcahx.eu.org/api/primbon/kecocokanpasangan"
        f"?cowo={nama1_url}&cewe={nama2_url}&apikey={API_BOTCHAX}"
    )

    # Request API
    try:
        rp = await Tools.fetch.get(url)
    except Exception:
        return await proses.edit(
            f"{em.gagal}<b>Tidak dapat terhubung ke server.</b>"
        )

    if rp.status_code != 200:
        return await proses.edit(
            f"{em.gagal}<b>Gagal mengambil data, coba lagi nanti.</b>"
        )

    data = rp.json()

    if not data.get("status"):
        return await proses.edit(
            f"{em.gagal}<b>API Error:</b> {data.get('message', 'Unknown error')}"
        )

    result = data.get("result", {}).get("message", {})

    nama_anda = result.get("nama_anda", nama1.title())
    nama_pasangan = result.get("nama_pasangan", nama2.title())
    sisi_positif = result.get("sisi_positif", "-")
    sisi_negatif = result.get("sisi_negatif", "-")
    catatan = result.get("catatan", "-")

    teks = (
        f"<blockquote><b>{em.love} 𝗖𝗘𝗞 𝗞𝗘𝗖𝗢𝗖𝗢𝗞𝗔𝗡 𝗝𝗢𝗗𝗢𝗛</b></blockquote>\n"
        f"<blockquote expandable>"
        f"{em.saya}<b> 𝗡𝗮𝗺𝗮 : {nama_anda}</b>\n"
        f"{em.jodoh} 𝗣𝗮𝘀𝗮𝗻𝗴𝗮𝗻 : <b>{nama_pasangan}</b>\n\n"
        f"{em.sukses} <b>𝗦𝗶𝘀𝗶 𝗣𝗼𝘀𝗶𝘁𝗶𝗳 :</b>\n{sisi_positif}\n\n"
        f"{em.gagal} <b>𝗦𝗶𝘀𝗶 𝗡𝗲𝗴𝗮𝘁𝗶𝗳 :</b>\n{sisi_negatif}\n"
        f"</blockquote>\n"
        f"<blockquote expandable>{em.ket} <b>𝗖𝗮𝘁𝗮𝘁𝗮𝗻 :</b>\n{catatan}</blockquote>\n"
        f"<blockquote>{em.paranormal} <b> 𝗣𝗮𝗿𝗮𝗻𝗼𝗿𝗺𝗮𝗹:</b> {mention}</blockquote>"
    )

    # Output teks saja
    await proses.edit(teks)