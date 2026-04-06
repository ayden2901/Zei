import asyncio
import random
from pyrogram.enums import ChatType
from Navy.helpers.tasks import TaskManager
from Navy.database import dB, state
from pyrogram.types import ChatMemberUpdated, ChatPrivileges
from pyrogram import enums, errors
from pyrogram.errors import (ChannelPrivate, FloodWait, PeerIdInvalid, FloodWait,
                             UserBannedInChannel, ChannelInvalid,)
from pyrogram.raw.functions.messages import ReadMentions

from Navy.logger import logging

import time
import traceback
import os
import json
from config import API_BOTCHAX, BLACKLIST_KATA, BOT_ID
from urllib.parse import quote_plus 
import httpx

import config
from config import BOT_ID
from Navy import bot, navy

from Navy.helpers import (MessageFilter, Tools, get_cached_list, reply_same_type,
                     url_mmk)
import pytz
from pyrogram.enums import ParseMode
from datetime import datetime, timedelta
from Navy.helpers import CMD, Emoji, Tools, task



async def dasar_laknat():
    logger.info("Check whether this account is a burden or not...")
    try:
        async for bb in navy.get_dialogs():
            try:
                if bb.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    try:
                        await navy.get_chat(bb.chat.id)
                        await navy.read_chat_history(bb.chat.id, max_id=0)
                    except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                        continue
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        try:
                            await navy.read_chat_history(bb.chat.id, max_id=0)
                        except Exception:
                            continue
            except Exception as e:
                logger.error(f"An error occurred while processing dialog: {e}")
    except Exception as e:
        logger.error(f"An error occurred while fetching dialogs: {e}")

    logger.info("Finished Read Message..")
    # sys.exit(1)


async def autor_gc(client):
    if not dB.get_var(client.me.id, "read_gc"):
        return
    while not await asyncio.sleep(3600):
        logger.info("Running Autoread For Group...")
        try:
            async for bb in client.get_dialogs(limit=500):
                try:
                    if bb.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                        try:
                            await client.read_chat_history(bb.chat.id, max_id=0)
                        except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                            continue
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            try:
                                await client.read_chat_history(bb.chat.id, max_id=0)
                            except Exception:
                                continue
                except Exception as e:
                    logger.error(f"An error occurred while processing dialog: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fetching dialogs: {e}")

        logger.info("Finished Read Message...")


async def autor_mention(client):
    if not dB.get_var(client.me.id, "read_mention"):
        return
    while not await asyncio.sleep(3600):
        logger.info("Running Autoread For Mention...")
        try:
            async for bb in client.get_dialogs(limit=500):
                try:
                    if bb.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                        try:
                            await client.invoke(
                                ReadMentions(peer=await client.resolve_peer(bb.chat.id))
                            )
                        except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                            continue
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            try:
                                await client.invoke(
                                    ReadMentions(
                                        peer=await client.resolve_peer(bb.chat.id)
                                    )
                                )
                            except Exception:
                                continue
                except Exception as e:
                    logger.error(f"An error occurred while processing dialog: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fetching dialogs: {e}")

        logger.info("Finished Read Mention...")


async def autor_ch(client):
    if not dB.get_var(client.me.id, "read_ch"):
        return
    while not await asyncio.sleep(3600):
        logger.info("Running Autoread For Channel...")
        try:
            async for bb in client.get_dialogs(limit=500):
                try:
                    if bb.chat.type == ChatType.CHANNEL:
                        try:
                            await client.read_chat_history(bb.chat.id, max_id=0)
                        except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                            continue
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            try:
                                await client.read_chat_history(bb.chat.id, max_id=0)
                            except Exception:
                                continue
                except Exception as e:
                    logger.error(f"An error occurred while processing dialog: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fetching dialogs: {e}")

        logger.info("Finished Read Message...")


async def autor_us(client):
    if not dB.get_var(client.me.id, "read_us"):
        return
    while not await asyncio.sleep(3600):
        logger.info("Running Autoread For Users...")
        try:
            async for bb in client.get_dialogs(limit=500):
                try:
                    if bb.chat.type == ChatType.PRIVATE:
                        try:
                            await client.read_chat_history(bb.chat.id, max_id=0)
                        except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                            continue
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            try:
                                await client.read_chat_history(bb.chat.id, max_id=0)
                            except Exception:
                                continue
                except Exception as e:
                    logger.error(f"An error occurred while processing dialog: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fetching dialogs: {e}")

        logger.info("Finished Read Message...")


async def autor_bot(client):
    if not dB.get_var(client.me.id, "read_bot"):
        return
    while not await asyncio.sleep(3600):
        logger.info("Running Autoread For Bots...")
        try:
            async for bb in client.get_dialogs(limit=500):
                try:
                    if bb.chat.type == ChatType.BOT:
                        try:
                            await client.read_chat_history(bb.chat.id, max_id=0)
                        except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                            continue
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            try:
                                await client.read_chat_history(bb.chat.id, max_id=0)
                            except Exception:
                                continue
                except Exception as e:
                    logger.error(f"An error occurred while processing dialog: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fetching dialogs: {e}")

        logger.info("Finished Read Message...")


async def autor_all(client):
    if not dB.get_var(client.me.id, "read_all"):
        return
    while not await asyncio.sleep(3600):
        logger.info("Running Autoread For All...")
        try:
            async for bb in client.get_dialogs(limit=500):
                try:
                    if bb.chat.type in [
                        ChatType.GROUP,
                        ChatType.SUPERGROUP,
                        ChatType.CHANNEL,
                        ChatType.PRIVATE,
                        ChatType.BOT,
                    ]:
                        try:
                            await client.read_chat_history(bb.chat.id, max_id=0)
                        except (ChannelPrivate, PeerIdInvalid, UserBannedInChannel):
                            pass
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            try:
                                await client.read_chat_history(bb.chat.id, max_id=0)
                            except Exception:
                                continue
                except Exception as e:
                    logger.error(f"An error occurred while processing dialog: {e}")
        except Exception as e:
            logger.error(f"An error occurred while getting dialogs: {e}")

        logger.info("Finished Read Message...")


# CHATBOT ==========

TEXT_ROLE = """lu adalah manusia dengan karakter toxic. serta balaslah pesan menggunakan huruf kecil disemua teks dan balaslah pesan 1 patah, 2 patah atau 3 patah kata saja."""

userbot_ids = set()
blacklisted_chats = set()
validator = MessageFilter()
SEMAPHORE = asyncio.Semaphore(10)
last_msg_cache = {}
message_queue = {}
processed_messages = set()

DEFAULT_ROLE = """lu adalah manusia dengan karakter toxic. serta balaslah pesan menggunakan huruf kecil disemua teks dan balaslah pesan satu patah, dua patah, tiga patah sampai empat patah kata saja.

aturan khusus:
kalau ada yang ngomong "ubot" atau "userbot" atau "yubot"
balas:
"ubot gacor ga? ubot yang gacor cuma di @starbotdevs"

kalau ada yang ngomong "bot"
balas:
"bot pala lu" atau "bukan bot ka" atau "najis bgt"

kalau ada yang ngomong "uno"
balas:
"kayak jago aja."

kalau ada yang ngomong "mole" atau "emel"
balas:
"lu aja nub lol"

kalau ada yang ngomong "demus"
balas:
"lonli bgt demus di tele"

kalau ada yang ngomong "sfs" atau "espies" atau "esfies"
balas:
"nihh subs ch orang ganteng @quotedamn"

kalau ada yang ngomong "os"
balas:
"os disini aja njir"

kalau ada yang ngomong "opmin"
balas:
"disini juga opmin 😎"

kalau ada ngomong "wen" atau "when ya" atau "wen ya" atau "wen ia"
balas :
"wen wen"

selain dari itu balaslah pesan se toxic mungkin satu patah, dua patah atau tiga patah kata saja.
"""

async def gen_text(client, message):
    text = (message.text or message.caption).strip()
    if not text:
        return

    role = await dB.get_var(client.me.id, "ROLE_CHATBOT") or DEFAULT_ROLE

    from urllib.parse import quote
    text = quote(f"{role}\n\nuser: {text}")

    API_URL = f"https://api.botcahx.eu.org/api/search/gpt?text={text}&apikey={API_BOTCHAX}"

    try:
        res = await Tools.fetch.get(API_URL)
        if res.status_code == 200:
            result = res.json().get("message")
            if not result:
                return None
            return result
    except Exception:
        return None


async def get_random_text():
    # Hapus dulu CHATBOT_TEXT
    await dB.remove_var(BOT_ID, "CHATBOT_TEXT")

    # Baru ambil ulang dari DB
    return await dB.get_var(BOT_ID, "CHATBOT_TEXT") or []


async def add_auto_text(text):
    auto_text = await get_random_text()
    auto_text.append(text)
    await dB.set_var(BOT_ID, "CHATBOT_TEXT", auto_text)

async def chatbot_trigger(client, message):

    if not message.from_user or not message.chat:
        return

    # ✅ skip SEMUA userbot (diri sendiri & userbot lain)
    if message.from_user.id in client._get_my_id:
        return

    # ✅ Jangan balas pesan yang sama dua kali
    key = (message.chat.id, message.id)
    if key in processed_messages:
        return

    processed_messages.add(key)

    # biar gak numpuk memory
    if len(processed_messages) > 500:
        processed_messages.clear()

    # ✅ cek grup aktif chatbot
    if message.chat.id not in await dB.get_list_from_var(client.me.id, "CHATBOT"):
        return

    # ✅ ignore user tertentu
    if message.from_user.id in await dB.get_list_from_var(
        client.me.id, "CHATBOT_IGNORE"
    ):
        return

    # ✅ ignore admin kalau setting aktif
    if await dB.get_var(client.me.id, "CHATBOT_ADMIN"):
        if message.from_user.id in await client.admin_list(message):
            return

    text = message.text or message.caption
    if not text:
        return

    # ✅ filter blacklist kata
    for word in BLACKLIST_KATA:
        if word in text:
            return

    # ✅ filter link + spam text abnormal
    if url_mmk(text) or validator.is_text_abnormal(text):
        return

    # mulai ngetik
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

    response = await gen_text(client, message)

    if response:
        try:
            await message.reply(response)
            await add_auto_text(response)

        except errors.FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply(response)
            await add_auto_text(response)

    else:
        fallback = await get_random_text()
        if fallback:
            await message.reply(random.choice(fallback))

    return await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)


async def get_last_message(client, chat_id, ttl=1):
    key = (client.me.id, chat_id)
    if key in last_msg_cache and time.time() - last_msg_cache[key][0] < ttl:
        return last_msg_cache[key][1]
    async for msg in client.get_chat_history(chat_id, limit=1):
        last_msg_cache[key] = (time.time(), msg)
        return msg


async def safe_send(client, message, text):
    try:
        await message.reply(text)
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply(text)


async def limited_chatbot_trigger(client, msg):
    async with SEMAPHORE:
        await chatbot_trigger(client, msg)


async def queue_message(client, message):
    q = message_queue.setdefault(client.me.id, asyncio.Queue())
    await q.put(message)
    if q.qsize() == 1:
        asyncio.create_task(process_queue(client, q))


async def process_queue(client, q):
    while not q.empty():
        msg = await q.get()
        await limited_chatbot_trigger(client, msg)
        # await asyncio.sleep(0.5)

async def ChatbotTask():
    while True:
        try:
            for client in navy._ubot:
                chats = await get_cached_list(
                    dB.get_list_from_var, client.me.id, "CHATBOT"
                )

                for chat_id in chats:
                    if chat_id in blacklisted_chats:
                        continue

                    try:
                        msg = await get_last_message(client, chat_id)

                        if not msg or not msg.text:
                            continue

                        await queue_message(client, msg)

                    except (errors.ChatWriteForbidden, errors.ChannelInvalid):
                        print(
                            f"Access issue {client.me.id} in {chat_id}, deleted."
                        )
                        await dB.remove_from_var(client.me.id, "CHATBOT", chat_id)
                        continue

                    except Exception as e:
                        print(
                            f"Error handling {client.me.id} chat {chat_id}: {e}"
                        )
                        await asyncio.sleep(1)
                        continue

            await asyncio.sleep(1)

        except Exception:
            print(f"error: {traceback.format_exc()}")


"""
async def WaktuSholatTask():
    Background task untuk cek user aktif dan jalankan scheduler
    print("[TASK] WaktuSholatTask started")

    while True:
        try:
            active_users = await sholat.get_active_users()
            if active_users:
                if not sholat.GLOBAL_SHOLAT_RUNNING:
                    sholat.GLOBAL_SHOLAT_RUNNING = True
                    sholat.GLOBAL_SHOLAT_TASK = asyncio.create_task(
                        sholat.global_sholat_scheduler()
                    )
                elif sholat.GLOBAL_SHOLAT_TASK and sholat.GLOBAL_SHOLAT_TASK.done():
                    sholat.GLOBAL_SHOLAT_TASK = asyncio.create_task(
                        sholat.global_sholat_scheduler()
                    )
            else:
                if sholat.GLOBAL_SHOLAT_RUNNING:
                    sholat.GLOBAL_SHOLAT_RUNNING = False
                    if sholat.GLOBAL_SHOLAT_TASK:
                        sholat.GLOBAL_SHOLAT_TASK.cancel()
                        sholat.GLOBAL_SHOLAT_TASK = None
        except Exception as e:
            print(f"[TASK ERROR] {e}")

        await asyncio.sleep(30)

"""