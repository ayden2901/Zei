import asyncio
import random
import traceback
from datetime import datetime

from pyrogram.errors import FloodWait, UserBannedInChannel

from Navy import bot, navy
from config import BLACKLIST_GCAST
from Navy.database import dB
from Navy.logger import logger

from Navy.helpers import Emoji

MAX_CONCURRENT_BROADCAST = 5
AUTOBC_STATUS = set()


async def get_auto_gcast_messages(client):
    entries = await dB.get_var(client.me.id, "AUTO_GCAST") or []
    return [await client.get_messages("me", int(e["message_id"])) for e in entries]

async def safe_send_message(selected_msg, chat_id, watermark=None):
    thread_id = await dB.get_var(chat_id, "SELECTED_TOPIC") or None
    try:
        client = selected_msg._client

        if watermark:
            text = selected_msg.text
            caption = selected_msg.caption

            if text:
                await client.send_message(
                    chat_id, f"{text}\n\n{watermark}", message_thread_id=thread_id
                )
            elif caption:
                media_types = [
                    ("photo", selected_msg.photo),
                    ("video", selected_msg.video),
                    ("animation", selected_msg.animation),
                    ("audio", selected_msg.audio),
                    ("document", selected_msg.document),
                    ("sticker", selected_msg.sticker),
                ]

                file_id = None
                for media_type, media_obj in media_types:
                    if media_obj:
                        file_id = media_obj.file_id
                        break

                if file_id:
                    await client.send_cached_media(
                        chat_id,
                        file_id,
                        caption=f"{caption}\n\n{watermark}",
                        message_thread_id=thread_id,
                    )
            else:
                # Handle media tanpa caption
                media_types = [
                    ("photo", selected_msg.photo),
                    ("video", selected_msg.video),
                    ("animation", selected_msg.animation),
                    ("audio", selected_msg.audio),
                    ("document", selected_msg.document),
                    ("sticker", selected_msg.sticker),
                ]

                file_id = None
                for media_type, media_obj in media_types:
                    if media_obj:
                        file_id = media_obj.file_id
                        break

                if file_id:
                    await client.send_cached_media(
                        chat_id, file_id, caption=watermark, message_thread_id=thread_id
                    )
        else:
            await selected_msg.copy(chat_id, message_thread_id=thread_id)

        await asyncio.sleep(0.1)
        return True

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await safe_send_message(selected_msg, chat_id, watermark)
    except UserBannedInChannel:
        return "banned"
    except Exception:
        return False


async def sending_message(client):
    try:
        messages = await get_auto_gcast_messages(client)
    except OSError:
        logger.error(f"Koneksi {client.me.id} putus")
        if client.me.id in AUTOBC_STATUS:
            AUTOBC_STATUS.remove(client.me.id)
        return
    if not messages:
        return
    while client.me.id in AUTOBC_STATUS:
        try:
            em = Emoji(client)
            await em.get()

            # Hilangkan watermark dan plan is_pro
            watermark = None

            sem = asyncio.Semaphore(MAX_CONCURRENT_BROADCAST)
            delay = await dB.get_var(client.me.id, "DELAY_GCAST") or 300
            done = await dB.get_var(client.me.id, "ROUNDS") or 0
            group, failed = 0, 0
            blacklist = set(
                await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST") or []
            ) | set(BLACKLIST_GCAST)

            selected_msg = random.choice(messages)
            peer = client._get_my_peer.get(client.me.id)
            chats = (
                peer.get("group", [])
                if peer and peer.get("group")
                else await client.get_chat_id("group")
            )

            async def send_msg(chat_id):
                nonlocal group, failed
                if chat_id in blacklist:
                    return
                async with sem:
                    result = await safe_send_message(selected_msg, chat_id, watermark)
                if result == True:
                    group += 1
                elif result == "banned":
                    failed += 1
                    await client.send_message(
                        "me",
                        "**⚠️ Your account has limited access**\nAutoBC has been disabled.",
                    )
                    await dB.remove_var(client.me.id, "AUTOBC")
                    if client.me.id in AUTOBC_STATUS:
                        AUTOBC_STATUS.remove(client.me.id)
                else:
                    failed += 1

            print(f"Running autobc for {client.me.id}")
            await asyncio.gather(*(send_msg(chat_id) for chat_id in chats))
            done += 1
            await dB.set_var(client.me.id, "ROUNDS", done)
            await dB.set_var(client.me.id, "SUCCES_GROUP", group)
            await dB.set_var(client.me.id, "LAST_TIME", datetime.utcnow().timestamp())
            summary = (
                f"<b><i>{em.warn}Autobc Done\n"
                f"{em.sukses}Berhasil : {group} Chat\n"
                f"{em.gagal}Gagal : {failed} Chat\n"
                f"{em.msg}Putaran Ke {done} Delay {delay} detik</i></b>"
            )
            try:
                await client.send_message("me", summary)
            except Exception:
                await dB.remove_var(client.me.id, "AUTOBC")
                if client.me.id in AUTOBC_STATUS:
                    AUTOBC_STATUS.remove(client.me.id)
            await asyncio.sleep(int(delay))
        except Exception:
            logger.error(traceback.format_exc())


async def AutoBC():
    logger.info("✅ AutoBC tasks started")
    while True:
        for client in navy._ubot:
            if (
                await dB.get_var(client.me.id, "AUTOBC")
                and client.me.id not in AUTOBC_STATUS
            ):
                last_time = await dB.get_var(client.me.id, "LAST_TIME") or 0
                delay = await dB.get_var(client.me.id, "DELAY_GCAST") or 300
                now = datetime.utcnow().timestamp()

                elapsed = now - last_time
                if elapsed < int(delay):
                    wait_time = int(delay) - int(elapsed)
                    logger.info(
                        f"⏳ Menunggu {wait_time} detik sebelum AutoBC {client.me.id} mulai."
                    )
                    await asyncio.sleep(wait_time)

                AUTOBC_STATUS.add(client.me.id)
                asyncio.create_task(sending_message(client))
        await asyncio.sleep(30)