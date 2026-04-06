import os
import asyncio
import pytz
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from Navy import bot, navy
from Navy.database import dB, state
from Navy.helpers import CMD, Emoji, Tools, task
from config import API_BOTCHAX


__MODULES__ = "ᴡᴀᴋᴛᴜ sʜᴏʟᴀᴛ"
__HELP__ = """<blockquote>Command Help **Waktu Sholat**</blockquote>

<blockquote><b>Auto notifikasi waktu sholat</b></blockquote>

    <code>{0}waktusholat jakarta on</code>
    <code>{0}waktusholat jakarta off</code>

Bot akan mengirim notifikasi saat waktu sholat tiba.

<b>{1}</b>
"""

# ===========================
# GLOBAL CONFIG
# ===========================
TZ = pytz.timezone("Asia/Jakarta")

GLOBAL_SHOLAT_RUNNING = False
GLOBAL_SHOLAT_TASK = None

JADWAL_CACHE = {}
LAST_CACHE_RESET = None


# ===========================
# Database Helpers
# ===========================
async def get_active_chats():
    result = []
    rows = await dB.fetchall("SELECT _id FROM variabel")

    for (user_id,) in rows:
        try:
            status = await dB.get_var(user_id, "sholat_status")
            chats = await dB.get_var(user_id, "sholat_chats")

            if status and chats:
                for chat_id in chats:
                    result.append((user_id, chat_id))
        except:
            continue

    return result


async def get_jadwal_sholat(kota):
    """Ambil jadwal sholat dari API / cache"""
    if kota in JADWAL_CACHE:
        return JADWAL_CACHE[kota]["timings"], JADWAL_CACHE[kota]["date"]

    url = f"https://api.botcahx.eu.org/api/tools/jadwalshalat?apikey={API_BOTCHAX}&kota={kota}"

    try:
        resp = await Tools.fetch.get(url, timeout=10)
        data = resp.json()

        if "result" not in data:
            return None, None

        today_data = data["result"]["data"][0]
        timings = today_data["timings"]
        api_date = today_data["date"]["gregorian"]["date"]

        JADWAL_CACHE[kota] = {
            "date": api_date,
            "timings": timings
        }

        return timings, api_date

    except:
        return None, None


# ===========================
# Command ON / OFF
# ===========================
@CMD.UBOT("waktusholat")
async def waktusholat_cmd(client: Client, message: Message):
    em = Emoji(client)
    await em.get()

    if len(message.command) < 3:
        return await message.reply(
            f"{em.gagal} Format:\n{message.text.split()[0]} [kota] on/off"
        )

    kota = message.command[1].lower()
    status = message.command[2].lower()

    user_id = client.me.id

    chat_list = await dB.get_var(user_id, "sholat_chats") or []
    old_kota = await dB.get_var(user_id, "sholat_kota")
    old_status = await dB.get_var(user_id, "sholat_status")

    # ======================
    # ON
    # ======================
    if status == "on":

        # Sudah aktif di chat ini
        if message.chat.id in chat_list:
            return await message.reply(
                f"{em.gagal} Notifikasi sudah aktif di chat ini\nKota: <b>{old_kota}</b>",
                parse_mode=ParseMode.HTML
            )

        chat_list.append(message.chat.id)

        await dB.set_var(user_id, "sholat_kota", kota)
        await dB.set_var(user_id, "sholat_status", True)
        await dB.set_var(user_id, "sholat_chats", chat_list)
        await dB.set_var(user_id, "last_sholat", None)

        await message.reply(
            f"{em.sukses} Notifikasi sholat aktif\nKota: <b>{kota}</b>",
            parse_mode=ParseMode.HTML
        )

        # Start scheduler jika belum jalan
        global GLOBAL_SHOLAT_RUNNING, GLOBAL_SHOLAT_TASK
        if not GLOBAL_SHOLAT_RUNNING:
            GLOBAL_SHOLAT_RUNNING = True
            GLOBAL_SHOLAT_TASK = asyncio.create_task(global_sholat_scheduler())
            print("[SYSTEM] Scheduler global dimulai")

    # ======================
    # OFF
    # ======================
    elif status == "off":

        if message.chat.id not in chat_list:
            return await message.reply(
                f"{em.gagal} Notifikasi tidak aktif di chat ini"
            )

        chat_list.remove(message.chat.id)
        await dB.set_var(user_id, "sholat_chats", chat_list)

        # Jika tidak ada chat tersisa → matikan global
        if not chat_list:
            await dB.set_var(user_id, "sholat_status", False)

        await message.reply(f"{em.sukses} Notifikasi dimatikan")

    else:
        await message.reply("Gunakan: on / off")


# ===========================
# GLOBAL SCHEDULER REVISI
# ===========================
async def global_sholat_scheduler():
    global GLOBAL_SHOLAT_RUNNING, GLOBAL_SHOLAT_TASK, LAST_CACHE_RESET

    print("[SHOLAT] Global scheduler running (PRODUCTION)")

    jadwal_map = {
        "Fajr": "Subuh",
        "Dhuhr": "Dzuhur",
        "Asr": "Ashar",
        "Maghrib": "Maghrib",
        "Isha": "Isya"
    }

    try:
        while True:
            now = datetime.now(TZ)
            today_str = now.strftime("%d-%m-%Y")

            # Reset cache harian
            if LAST_CACHE_RESET != today_str:
                JADWAL_CACHE.clear()
                LAST_CACHE_RESET = today_str
                print("[SHOLAT] Cache reset")

            users = await get_active_chats()

            if not users:
                await asyncio.sleep(60)
                continue

            nearest_event = None

            # Cari event terdekat untuk semua chat aktif user
            for user_id, chat_id in users:

                # cek user on/off
                sholat_status = await dB.get_var(user_id, "sholat_status")
                if not sholat_status:
                    continue

                client = next((c for c in navy._ubot if c.me.id == user_id), None)
                if not client or not client.is_connected:
                    continue

                kota = await dB.get_var(user_id, "sholat_kota")
                last_key = await dB.get_var(user_id, "last_sholat")
                timings, api_date = await get_jadwal_sholat(kota)
                if not timings:
                    continue

                for api_name, nama in jadwal_map.items():
                    try:
                        waktu_str = timings[api_name][:5]
                        waktu_dt = TZ.localize(
                            datetime.strptime(f"{today_str} {waktu_str}", "%d-%m-%Y %H:%M")
                        )
                    except:
                        continue

                    # BEFORE 1 menit
                    before_key = f"{nama}-{api_date}-{chat_id}-before"
                    if before_key != last_key:
                        delta = (waktu_dt - now).total_seconds() - 60  # 1 menit sebelum
                        if delta > 0:
                            if not nearest_event or delta < nearest_event["delta"]:
                                nearest_event = {
                                    "delta": delta,
                                    "client": client,
                                    "chat_id": chat_id,
                                    "user_id": user_id,
                                    "nama": nama,
                                    "type": "before",
                                    "key": before_key
                                }

                    # ON TIME
                    on_key = f"{nama}-{api_date}-{chat_id}-on"
                    if on_key != last_key:
                        delta = (waktu_dt - now).total_seconds()
                        if delta > 0:
                            if not nearest_event or delta < nearest_event["delta"]:
                                nearest_event = {
                                    "delta": delta,
                                    "client": client,
                                    "chat_id": chat_id,
                                    "user_id": user_id,
                                    "nama": nama,
                                    "type": "on",
                                    "key": on_key
                                }

            # ======================
            # Eksekusi event terdekat
            # ======================
            if nearest_event:
                sleep_time = max(int(nearest_event["delta"]), 1)
                print(f"[SHOLAT] Sleep {sleep_time}s -> {nearest_event['nama']} ({nearest_event['type']})")

                await asyncio.sleep(sleep_time)

                client = nearest_event["client"]
                chat_id = nearest_event["chat_id"]
                user_id = nearest_event["user_id"]
                nama = nearest_event["nama"]
                event_type = nearest_event["type"]

                if not client.is_connected:
                    continue

                em = Emoji(client)
                await em.get()

                before_dict = await dB.get_var(user_id, "before_msg_id") or {}

                # BEFORE 1 MENIT
                if event_type == "before":
                    try:
                        msg = await client.send_message(
                            chat_id,
                            f"{em.net} 1 menit lagi masuk waktu sholat <b>{nama}</b>\nPersiapkan diri untuk beribadah.",
                            parse_mode=ParseMode.HTML
                        )
                        before_dict[str(chat_id)] = msg.id
                    except Exception as e:
                        print(f"[SHOLAT ERROR] BEFORE {nama} chat {chat_id}: {e}")

                # ON TIME
                else:
                    text = f"{em.net} Sudah masuk waktu sholat <b>{nama}</b>\nSegera tunaikan ibadah."
                    msg_id = before_dict.get(str(chat_id))
                    try:
                        if msg_id:
                            await client.edit_message_text(chat_id, msg_id, text, parse_mode=ParseMode.HTML)
                            before_dict.pop(str(chat_id), None)
                        else:
                            await client.send_message(chat_id, text, parse_mode=ParseMode.HTML)
                    except Exception as e:
                        print(f"[SHOLAT ERROR] ON {nama} chat {chat_id}: {e}")

                await dB.set_var(user_id, "before_msg_id", before_dict)
                await dB.set_var(user_id, "last_sholat", nearest_event["key"])

                print(f"[SHOLAT] Sent -> {nama} ({event_type})")
            else:
                await asyncio.sleep(30)

    except asyncio.CancelledError:
        GLOBAL_SHOLAT_RUNNING = False
        GLOBAL_SHOLAT_TASK = None
        print("[SHOLAT] Scheduler stopped")