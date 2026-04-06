import asyncio
import platform
import sys
import time
from asyncio import create_subprocess_exec as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from datetime import datetime
from os import remove
from platform import python_version
from shutil import which

import psutil
from pytgcalls import __version__ as pytgcalls

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Message
from assistant.callback import spc_callback
from assistant.inline import inline_spc
from config import (BOT_ID, FAKE_DEVS, KYNAN, LOG_BACKUP, LOG_SELLER, OWNER_ID,  SUDO_OWNERS, AKSES_DEPLOY)
from Navy import bot, navy
from Navy.helpers import (CMD, ButtonUtils, Emoji, Message, Quotly, Sticker, Tools, YoutubeSearch, cookies, stream, task, telegram, youtube)
import pyrogram.utils


__MODULES__ = "ᴄᴘᴜ"
__HELP__ = """
"""


@CMD.BOT("spc")
async def psu_bot(client, message):
    print("🟢 Perintah /spc dijalankan oleh bot")
    # Batasi akses hanya untuk developer/akses_deploy
    DEVS = [8568361057]  # tambahkan akses_deploy jika kamu punya variabel itu
    user_id = message.from_user.id if message.from_user else 0
    me = await client.get_me()
    if user_id == me.id:
        return await message.reply("❌ Kamu tidak memiliki izin untuk menggunakan perintah ini.")
    if user_id not in DEVS:
        print(f"🚫 Akses ditolak untuk user_id: {user_id}")
        return await message.reply("❌ Kamu tidak memiliki izin untuk menggunakan perintah ini.")

    def get_size(bytes, suffix="B"):
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    uname = platform.uname()
    softw = "**🖥️ Informasi Sistem**\n"
    softw += f"`Sistem     : {uname.system}`\n"
    softw += f"`Rilis      : {uname.release}`\n"
    softw += f"`Versi      : {uname.version}`\n"
    softw += f"`Mesin      : {uname.machine}`\n"

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    softw += f"`Waktu Hidup: {bt.day}/{bt.month}/{bt.year}  {bt.hour}:{bt.minute}:{bt.second}`\n"

    cpuu = "**🧠 Informasi CPU**\n"
    cpuu += f"`Physical cores   : {psutil.cpu_count(logical=False)}`\n"
    cpuu += f"`Total cores      : {psutil.cpu_count(logical=True)}`\n"
    cpufreq = psutil.cpu_freq()
    cpuu += f"`Max Frequency    : {cpufreq.max:.2f}Mhz`\n"
    cpuu += f"`Min Frequency    : {cpufreq.min:.2f}Mhz`\n"
    cpuu += f"`Current Frequency: {cpufreq.current:.2f}Mhz`\n"

    cpuu += "**💡 CPU Usage Per Core**\n"
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        cpuu += f"`Core {i} : {percentage}%`\n"
    cpuu += "**⚙️ Total CPU Usage**\n"
    cpuu += f"`Semua Core: {psutil.cpu_percent()}%`\n"

    svmem = psutil.virtual_memory()
    memm = "**📦 Memori Digunakan**\n"
    memm += f"`Total     : {get_size(svmem.total)}`\n"
    memm += f"`Available : {get_size(svmem.available)}`\n"
    memm += f"`Used      : {get_size(svmem.used)}`\n"
    memm += f"`Percentage: {svmem.percent}%`\n"

    net = psutil.net_io_counters()
    bw = "**📶 Bandwidth Digunakan**\n"
    bw += f"`Unggah   : {get_size(net.bytes_sent)}`\n"
    bw += f"`Download : {get_size(net.bytes_recv)}`\n"

    help_string = "━━━━━━━━━━━━━━━━━━━━━━\n"
    help_string += f"{softw}"
    help_string += "━━━━━━━━━━━━━━━━━━━━━━\n"
    help_string += f"{cpuu}"
    help_string += "━━━━━━━━━━━━━━━━━━━━━━\n"
    help_string += f"{memm}"
    help_string += "━━━━━━━━━━━━━━━━━━━━━━\n"
    help_string += f"{bw}"
    help_string += "━━━━━━━━━━━━━━━━━━━━━━\n"
    help_string += "**⚙️ Informasi Mesin**\n"
    help_string += f"`Python   : {sys.version.split()[0]}`\n"
    help_string += f"`Pyrogram : {pyrogram.__version__}`\n"
    help_string += f"`PyTgCalls: {pytgcalls}`\n"
    help_string += "━━━━━━━━━━━━━━━━━━━━━━"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Close", callback_data="spc_close")]]
    )

    await client.send_message(
        message.chat.id,
        help_string,
        reply_markup=keyboard,
        reply_to_message_id=message.id
    )

@CMD.UBOT("spc")
async def _(client, message: Message):
    query = "inline_spc"
    results = await client.get_inline_bot_results("StarXCodeBot", query)
    await client.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id
    )