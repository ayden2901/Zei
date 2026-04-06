import asyncio
import traceback
import html
import aiosqlite

from datetime import datetime, timedelta
from pyrogram import raw, filters
from pyrogram.errors import (FloodWait, InputUserDeactivated, PeerIdInvalid,
                             UserIsBlocked, ChannelPrivate)

from pyrogram.helpers import kb
from pyrogram.enums import ParseMode
from pytz import timezone
from pyrogram.types import Message

from assistant.create_users import setExpiredUser
from assistant.eval import cb_evalusi, cb_gitpull2, cb_shell
from config import AKSES_DEPLOY, BOT_ID, LOG_SELLER, SUDO_OWNERS, LOG_BACKUP, BLACKLIST_GCAST
from Navy import bot, navy
from Navy.database import dB
from Navy.helpers import CMD, ButtonUtils, Emoji, Message
from Navy.logger import logger
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus



@CMD.BOT("addprem")
@CMD.UBOT("addprem")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    user_id = message.from_user.id
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    if user_id not in seles:
        return
    return await add_prem_user(client, message)
async def add_prem_user(client, message):
    em = Emoji(client)
    await em.get()
    user_id, waktu_input = await client.extract_user_and_reason(message)
    if not user_id:
        msg = await message.reply(
            f"{em.gagal}<b>{message.text.split()[0]} [user_id/username/reply] [durasi]</b>\n\nContoh:\n<code>/addprem 12345 3month</code>\n<code>/addprem 12345 7</code>", parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await message.reply(str(error))

    get_id = user.id
    if get_id in AKSES_DEPLOY:
        return await message.reply(
            f"Pengguna dengan ID : <code>{get_id}</code> sudah memiliki akses!"
        )

    AKSES_DEPLOY.append(get_id)

    # Durasi default: 30 hari
    if not waktu_input:
        waktu_input = "30"

    waktu_input = str(waktu_input).lower()
    jumlah_hari = 0

    if "month" in waktu_input:
        try:
            bulan = int(waktu_input.replace("month", ""))
            jumlah_hari = bulan * 30
        except ValueError:
            msg = await message.reply("Format bulan tidak valid. Gunakan: <code>3month</code>")
            await asyncio.sleep(2)
            await msg.delete()
            await message.delete()
            return
    else:
        try:
            jumlah_hari = int(waktu_input)
        except ValueError:
            msg = await message.reply(f"{em.gagal}Format hari tidak valid. Gunakan angka. Contoh: <code>7</code>", parse_mode=ParseMode.HTML)
            await asyncio.sleep(2)
            await msg.delete()
            await message.delete()
            return
    # Set expired
    now = datetime.now(timezone("Asia/Jakarta"))
    expired = now + timedelta(days=jumlah_hari)
    await dB.set_expired_date(get_id, expired)

    tanggal = expired.strftime("%Y-%m-%d %H:%M")

    await message.reply(
        f"{em.sukses}ᴜsᴇʀ ɪᴅ ➟ <code>{get_id}</code>\nʙᴇʀʜᴀsɪʟ ᴅɪʙᴇʀɪ ᴀᴋsᴇs sᴇʟᴀᴍᴀ <b>{jumlah_hari}</b> ʜᴀʀɪ\nᴀᴋᴛɪꜰ ʜɪɴɢɢᴀ: <b>{tanggal}</b>\nSɪʟᴀʜᴋᴀɴ ᴘᴇʀɢɪ ᴋᴇ {bot.me.mention}", parse_mode=ParseMode.HTML
    )

    # Kirim log ke LOG_SELLER
    try:
        target1 = f"<a href=tg://user?id={message.from_user.id}>{message.from_user.first_name} {message.from_user.last_name or ''}</a>"
        target2 = f"<a href=tg://user?id={user.id}>{user.first_name} {user.last_name or ''}</a>"
        await bot.send_message(
            LOG_SELLER,
            f"<b>User: {target1} memberikan akses ke: {target2}</b>\nDurasi: <b>{jumlah_hari} hari</b>\nExpired: <b>{tanggal}</b>"
        )
    except Exception:
        pass

    # Kirim notifikasi ke user
    try:
        await bot.send_message(
            get_id,
            "Selamat! Akun Anda sudah memiliki akses untuk pembuatan Userbot.",
            reply_markup=kb(
                [["✅ Lanjutkan Buat Userbot"]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except Exception:
        pass


@CMD.BOT("unprem")
async def _(client, message):
    return await un_prem_user(client, message)


@CMD.UBOT("unprem")
async def _(client, message):
    user_id = message.from_user.id
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    if user_id not in seles:
        return
    return await un_prem_user(client, message)


async def un_prem_user(client, message):
    em = Emoji(client)
    await em.get()
    user_id = await client.extract_user(message)
    if not user_id:
        msg = await message.reply(f"{em.gagal}Balas pesan pengguna atau berikan user_id/username", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return
    try:
        user = await client.get_users(user_id)
    except Exception as error:
        await message.reply(str(error))
    delpremium = AKSES_DEPLOY
    if user.id not in delpremium:
        msg = await message.reply(f"{em.warn}Tidak ditemukan", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return
    AKSES_DEPLOY.remove(user.id)
    return await message.reply(f"{em.sukses}ᴍᴇɴɢʜᴀᴘᴜs ᴀᴋsᴇs ᴅᴇᴘʟᴏʏ ᴜɴᴛᴜᴋ {user.full_name}", parse_mode=ParseMode.HTML)


@CMD.BOT("listprem")
@CMD.FAKE_NLX
async def get_prem_user(client, message):
    em = Emoji(client)
    await em.get()
    text = ""
    count = 0
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    for user_id in seles:
        try:
            user = await client.get_users(user_id)
            count += 1
            userlist = f"{em.msg}{count}. <a href=tg://user?id={user.id}>{user.first_name} {user.last_name or ''}</a>\n{em.ket}User ID : <code>{user.id}</code>"
        except Exception:
            continue
        text += f"<blockquote>{userlist}</blockquote>\n"
    if not text:
        msg = await message.reply_text(f"{em.warna}Tidak ada pengguna yang ditemukan", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return
    else:
        return await message.reply_text(text)


@CMD.BOT("addseller")
@CMD.FAKE_NLX
async def _(client, message):
    return await add_seller(client, message)


@CMD.UBOT("addseller")
@CMD.FAKE_NLX
async def _(client, message):
    return await add_seller(client, message)


async def add_seller(client, message):
    em = Emoji(client)
    await em.get()
    user = None
    user_id = await client.extract_user(message)
    if not user_id:
        return await message.reply(f"{em.warn}Balas pesan pengguna atau berikan user_id/username", parse_mode=ParseMode.HTML)
    try:
        user = await client.get_users(user_id)
    except Exception as error:
        await message.reply(str(error))
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    if user.id in seles:
        return await message.reply(f"{em.sukses}Sudah menjadi reseller.", parse_mode=ParseMode.HTML)

    await dB.add_to_var(BOT_ID, "SELLER", user.id)
    return await message.reply(f"{em.sukses}{user.mention} telah menjadi reseller", parse_mode=ParseMode.HTML)


@CMD.BOT("unseller")
@CMD.FAKE_NLX
async def _(client, message):
    return await un_seller(client, message)


@CMD.UBOT("unseller")
@CMD.FAKE_NLX
async def _(client, message):
    return await un_seller(client, message)


async def un_seller(client, message):
    em = Emoji(client)
    await em.get()
    user = None
    user_id = await client.extract_user(message)
    if not user_id:
        return await message.reply(f"{em.warn}Balas pesan pengguna atau berikan user_id/username", parse_mode=ParseMode.HTML)
    try:
        user = await client.get_users(user_id)
    except Exception as error:
        await message.reply(str(error))
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    if user.id not in seles:
        return await message.reply(f"{em.gagal}Tidak ditemukan", parse_mode=ParseMode.HTML)
    await dB.remove_from_var(BOT_ID, "SELLER", user.id)
    return await message.reply(f"{em.sukses}{user.mention} berhasil dihapus", parse_mode=ParseMode.HTML)


@CMD.BOT("listseller")
@CMD.FAKE_NLX
async def get_seles_user(client, message):
    text = ""
    count = 0
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    for user_id in seles:
        try:
            user = await client.get_users(user_id)
            count += 1
            userlist = f"<blockquote>{count}. <a href=tg://user?id={user.id}>{user.first_name} {user.last_name or ''}</a>\n<code>{user.id}</code></blockquote>"
        except Exception:
            continue
        text += f"{userlist}\n"
    if not text:
        return await message.reply_text(f"{em.warn}Tidak ada pengguna yang ditemukan", parse_mode=ParseMode.HTML)
    else:
        return await message.reply_text(text)


@CMD.BOT("setexp")
@CMD.UBOT("setexp")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    user_id = message.from_user.id
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    
    # Gabungkan AKSES_DEPLOY dan SELLER
    akses = AKSES_DEPLOY + seles
    if user_id not in akses:
        msg = await message.reply(f"{em.warn}Yang bener aja, lu bukan seller pea", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return
    return await set_expired(client, message)


async def set_expired(client, message):
    em = Emoji(client)
    await em.get()
    user_id, waktu_input = await client.extract_user_and_reason(message)
    if not user_id:
        return await message.reply(f"{em.warn}{message.text.split()[0]} (user_id/username/reply) (durasi)", parse_mode=ParseMode.HTML)

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await message.reply(str(error))

    if not waktu_input:
        waktu_input = "30"  # default 30 hari jika tidak diisi

    waktu_input = str(waktu_input).lower()
    jumlah_hari = 0

    if "month" in waktu_input:
        try:
            bulan = int(waktu_input.replace("month", ""))
            jumlah_hari = bulan * 30
        except ValueError:
            return await message.reply(f"{em.warn}Format bulan tidak valid. Contoh: <code>3month</code>", parse_mode=ParseMode.HTML)
    else:
        try:
            jumlah_hari = int(waktu_input)
        except ValueError:
            return await message.reply(f"{em.warn}Format hari tidak valid. Contoh: <code>7</code>", parse_mode=ParseMode.HTML)

    now = datetime.now(timezone("Asia/Jakarta"))
    expire_date = now + timedelta(days=jumlah_hari)
    await dB.set_expired_date(user.id, expire_date)

    tanggal = expire_date.strftime("%Y-%m-%d %H:%M")
    return await message.reply(
        f"{em.sukses}<code>{user.id}</code> telah diberikan akses selama <b>{jumlah_hari}</b> hari.\nAktif hingga: <b>{tanggal}</b>", parse_mode=ParseMode.HTML
    )

@CMD.BOT("cek|cekexpired")
@CMD.UBOT("cek|cekexpired")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    # Hanya untuk AKSES_DEPLOY, SELLER, dan BOT
    sender_id = message.from_user.id
    seller = await dB.get_list_from_var(BOT_ID, "SELLER")
    akses = AKSES_DEPLOY + seller + [BOT_ID]

    if sender_id not in akses:
        msg = await message.reply(f"{em.gagal}Kamu tidak memiliki izin untuk menggunakan perintah ini.", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return
    # Ambil target user
    try:
        user_id = await client.extract_user(message)
    except TypeError:
        user_id = None

    if not user_id:
        msg = await message.reply(f"{em.warn}Pengguna tidak ditemukan. Silakan reply ke pesan pengguna atau mention mereka.", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    try:
        user = await client.get_users(user_id)
    except Exception as e:
        msg = await message.reply(f"{em.warn}Gagal mengambil informasi pengguna: {e}, parse_mode=ParseMode.HTML")
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    # Ambil tanggal expired
    expired_date = await dB.get_expired_date(user.id)
    jakarta = timezone("Asia/Jakarta")
    now = datetime.now(jakarta)

    if not expired_date:
        tanggal_exp = "-"
        status = "⛔️ TIDAK AKTIF"
    else:
        tanggal_exp = expired_date.astimezone(jakarta).strftime("%Y-%m-%d %H:%M")
        status = "✅ AKTIF" if expired_date > now else "⛔️ TIDAK AKTIF"

    teks = (
        f"<blockquote>{em.data}<b>CEK MASA AKTIF</b>\n\n"
        f"{em.owner}<b>Nama :</b> {user.first_name}\n"
        f"{em.profil}<b>User ID :</b> <code>{user.id}</code>\n"
        f"{em.uptime}<b>Username :</b> @{user.username if user.username else '-'}\n"
        f"{em.ket}<b>Status :</b> {status}\n"
        f"{em.msg}<b>Aktif hingga :</b> {tanggal_exp}</blockquote>"
    )

    teks2 = f"\n\n<blockquote>{em.warn}<b>Status kamu belum aktif.</b>\nSilakan hubungi developer atau seller untuk mengaktifkan kembali akses bot kamu.</blockquote>"

    if status == "⛔️ TIDAK AKTIF":
        await message.reply(teks + teks2, parse_mode=ParseMode.HTML)
    else:
        await message.reply(teks, parse_mode=ParseMode.HTML)

@CMD.BOT("unexpired")
async def unexpired_bot(client, message):
    em = Emoji(client)
    await em.get()
    print("🟢 Perintah /unexpired dijalankan oleh bot")
    
    DEVS = [7650122497]
    user_id = message.from_user.id if message.from_user else 0
    me = await client.get_me()

    if user_id == me.id:
        return await message.reply(f"{em.gagal}Kamu tidak memiliki izin untuk menggunakan perintah ini.", parse_mode=ParseMode.HTML)
    if user_id not in DEVS:
        print(f"🚫 Akses ditolak untuk user_id: {user_id}")
        msg = await message.reply(f"{em.gagal}Kamu tidak memiliki izin untuk menggunakan perintah ini.", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    target_id = await client.extract_user(message)
    if not target_id:
        msg = await message.reply(f"{em.warn}Pengguna tidak ditemukan.", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    try:
        user = await client.get_users(target_id)
    except Exception as error:
        msg = await message.reply(f"{em.gagal}{error}", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    await dB.rem_expired_date(user.id)
    return await message.reply(f"{em.sukses}Expired untuk <code>{user.id}</code> telah dihapus.", parse_mode=ParseMode.HTML)

@CMD.UBOT("unexpired")
async def unexpired_ubot(client, message):
    em = Emoji(client)
    await em.get()
    sender_id = message.from_user.id
    seller = await dB.get_list_from_var(BOT_ID, "SELLER")
    if sender_id not in AKSES_DEPLOY + seller:
        msg = await message.reply(f"{em.gagal}Kamu tidak memiliki izin untuk menggunakan perintah ini.", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    target_id = await client.extract_user(message)
    if not target_id:
        msg = await message.reply(f"{em.warn}Pengguna tidak ditemukan.", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    try:
        user = await client.get_users(target_id)
    except Exception as error:
        msg = await message.reply(f"{em.warn}{error}", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2)
        await msg.delete()
        await message.delete()
        return

    await dB.rem_expired_date(user.id)
    return await message.reply(f"{em.sukses}Expired untuk <code>{user.id}</code> telah dihapus.", parse_mode=ParseMode.HTML)


@CMD.BOT("broadcast")
@CMD.FAKE_NLX
@CMD.DEV_ONLY
async def _(client, message):
    if not message.reply_to_message:
        return await message.reply(
            "<b>Balas pesan yang ingin dikirim untuk broadcast.\n\nContoh:\n/broadcast cp\n/broadcast fw</b>"
        )

    args = message.text.split()
    if len(args) != 2 or args[1] not in ["cp", "fw"]:
        return await message.reply(
            "<b>Format salah!\nGunakan salah satu:\n"
            "/broadcast cp → copy pesan\n"
            "/broadcast fw → forward pesan</b>"
        )

    method = args[1]
    reply = message.reply_to_message

    users = await dB.get_list_from_var(BOT_ID, "BROADCAST") or []
    groups = await dB.get_list_from_var(BOT_ID, "GROUPS") or []
    blacklist = set(await dB.get_list_from_var(BOT_ID, "BLACKLIST_GCAST") or []) | set(BLACKLIST_GCAST)
    targets = [x for x in set(users + groups) if x not in blacklist]

    print("[DEBUG] BROADCAST:", users)
    print("[DEBUG] GROUPS:", groups)
    print("[DEBUG] BLACKLIST:", blacklist)
    print("[DEBUG] TARGETS AKHIR:", targets)

    sukses = 0
    gagal = 0

    for user_id in targets:
        try:
            if method == "cp":
                await reply.copy(user_id)
            else:
                await reply.forward(user_id)
            sukses += 1

        except FloodWait as e:
            logger.warning(f"[FloodWait] Menunggu {e.value} detik (ID: {user_id})")
            await asyncio.sleep(e.value)
            try:
                if method == "cp":
                    await reply.copy(user_id)
                else:
                    await reply.forward(user_id)
                sukses += 1
            except Exception as err:
                print(f"[Retry Error] Gagal kirim ke {user_id}: {err}")
                logger.error(f"[Retry Error] Gagal kirim ke {user_id}: {err}")
                gagal += 1

        except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated) as e:
            print(f"[Invalid User] ID {user_id} diblokir/dihapus: {e}")
            logger.warning(f"[Invalid User] ID {user_id} diblokir/dihapus: {e}")
            await dB.add_to_var(BOT_ID, "BLACKLIST_GCAST", user_id)
            await dB.remove_from_var(BOT_ID, "BROADCAST", user_id)
            await dB.remove_from_var(BOT_ID, "GROUPS", user_id)
            gagal += 1

        except Exception as err:
            print(f"[Broadcast Error] Gagal kirim ke {user_id}: {err}")
            logger.error(f"[Broadcast Error] Gagal kirim ke {user_id}: {err}")
            gagal += 1

    return await message.reply(
        f"<blockquote>"
        f"<b>📢 Broadcast selesai</b>\n"
        f"✅ Berhasil: <code>{sukses}</code>\n"
        f"❌ Gagal: <code>{gagal}</code>\n"
        f"🎯 Total target: <code>{len(targets)}</code>"
        f"</blockquote>"
    )

@bot.on_chat_member_updated()
async def on_added_to_group(client, member: ChatMemberUpdated):
    try:
        me = await client.get_me()
        bot_id = me.id

        if member.new_chat_member and member.new_chat_member.user.id == bot_id:
            new_status = member.new_chat_member.status

            # Tambahkan kembali ke GROUPS jika status bukan LEFT/BANNED
            if new_status not in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
                group_id = member.chat.id
                group_title = member.chat.title or "Tanpa Nama"

                await dB.remove_from_var(BOT_ID, "BLOCKED_GROUPS", group_id)
                await dB.add_to_var(BOT_ID, "GROUPS", group_id)

                logger.info(f"✅ Bot ditambahkan ke grup {group_id} → disimpan ke GROUPS")

                await bot.send_message(
                    LOG_BACKUP,
                    f"📌 <b>Bot berhasil masuk ke grup:</b>\n\n"
                    f"🏷️ <b>Nama:</b> {group_title}\n"
                    f"🆔 <code>{group_id}</code>"
                )

        elif member.old_chat_member and member.old_chat_member.user.id == bot_id:
            new_status = member.new_chat_member.status if member.new_chat_member else None

            # Bot keluar / dibanned
            if new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
                group_id = member.chat.id
                group_title = member.chat.title or "Tanpa Nama"

                await dB.remove_from_var(BOT_ID, "GROUPS", group_id)
                await dB.add_to_var(BOT_ID, "BLOCKED_GROUPS", group_id)

                logger.warning(f"🚫 Bot dikeluarkan dari grup {group_id} → ditandai BLOCKED")

                await bot.send_message(
                    LOG_BACKUP,
                    f"🚫 <b>Bot dikeluarkan dari grup:</b>\n\n"
                    f"🏷️ <b>Nama:</b> {group_title}\n"
                    f"🆔 <code>{group_id}</code>"
                )

    except Exception as e:
        logger.error(f"[on_added_to_group] {e}")



@CMD.BOT("cektarget")
@CMD.FAKE_NLX
@CMD.DEV_ONLY
async def cektarget_handler(client, message: Message):
    users = list(set(await dB.get_list_from_var(BOT_ID, "BROADCAST")))
    groups = list(set(await dB.get_list_from_var(BOT_ID, "GROUPS")))
    all_targets = list(set(users + groups))

    async def get_name(chat_id):
        try:
            chat = await client.get_chat(chat_id)
            if chat.type in ["group", "supergroup", "channel"]:
                return chat.title or f"ID {chat.id}"
            else:
                name = f"{chat.first_name or ''} {chat.last_name or ''}".strip()
                return name or f"ID {chat.id}"
        except PeerIdInvalid:
            return f"ID {chat_id} [PeerIdInvalid]"
        except ChannelPrivate:
            return f"ID {chat_id} [ChannelPrivate]"
        except Exception as e:
            return f"ID {chat_id} [Error: {e}]"

    debug_logs = [
        f"[DEBUG] Jumlah BROADCAST users: {len(users)}",
        f"[DEBUG] Jumlah GROUPS: {len(groups)}",
        f"[DEBUG] Total target: {len(all_targets)}",
        f"[DEBUG] Total user IDs: {len(users)}",
        f"[DEBUG] Total group IDs: {len(groups)}",
        f"[DEBUG] Hasil pengecekan:"
    ]

    debug_logs = [
        f"[DEBUG] Jumlah BROADCAST users: {len(users)}",
        f"[DEBUG] Jumlah GROUPS: {len(groups)}",
        f"[DEBUG] Total target: {len(all_targets)}",
        f"[DEBUG] Hasil pengecekan:"
    ]

    user_list = []
    for i, user_id in enumerate(users, start=1):
        try:
            user = await client.get_users(user_id)
            fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()
            user_list.append(f"{i}. {fullname or f'ID {user_id}'} [activated]")
        except Exception:
            user_list.append(f"{i}. ID {user_id} [activated]")

    group_list = []
    for i, group_id in enumerate(groups, start=1):
        try:
            chat = await client.get_chat(group_id)
            title = chat.title or f"ID {group_id}"
            username_or_id = f"@{chat.username}" if chat.username else f"{chat.id}"
            group_list.append(f"{i}. {title} [{username_or_id}] [activated]")
        except Exception:
            group_list.append(f"{i}. ID {group_id} [activated]")

    # Bangun pesan HTML dengan <blockquote> dan <b>
    text = "<blockquote>🎯 <b>Target Broadcast:</b></blockquote>\n"

    if user_list:
        text += "<blockquote>👤 <b>USER:</b>\n" + "\n".join(user_list) + "</blockquote>\n"
    if group_list:
        text += "<blockquote>👥 <b>GROUP:</b>\n" + "\n".join(group_list) + "</blockquote>\n"

    text += f"<blockquote>📊 <b>Total:</b> {len(all_targets)} target</blockquote>"

    await message.reply(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@CMD.UBOT("shell|sh")
@CMD.FAKE_NLX
async def _(client: navy, message):
    return await cb_shell(client, message)


@CMD.UBOT("eval|ev|e")
@CMD.NLX
@CMD.DEV_CMD("ceval")
async def _(client: navy, message):
    return await cb_evalusi(client, message)


@CMD.UBOT("reboot|update")
@CMD.FAKE_NLX
async def _(client: navy, message):
    return await cb_gitpull2(client, message)


@CMD.CALLBACK("^(prev_ub|next_ub)")
async def _(client, callback_query):
    await callback_query.answer()
    query = callback_query.data.split()
    count = int(query[1])
    if query[0] == "next_ub":
        if count == len(navy._ubot) - 1:
            count = 0
        else:
            count += 1
    elif query[0] == "prev_ub":
        if count == 0:
            count = len(navy._ubot) - 1
        else:
            count -= 1
    try:
        return await callback_query.edit_message_text(
            await Message.userbot(count),
            reply_markup=(ButtonUtils.userbot(navy._ubot[count].me.id, count)),
        )
    except Exception as e:
        return f"Error: {e}"


@CMD.CALLBACK("^(get_otp|get_phone|get_faktor|ub_deak|deak_akun)")
async def _(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    if user_id not in SUDO_OWNERS:
        return await callback_query.answer(
            f"<b>GAUSAH REWEL YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
            True,
        )
    X = navy._ubot[int(query[1])]
    if query[0] == "get_otp":
        async for otp in X.search_messages(777000, limit=1):
            try:
                if not otp.text:
                    await callback_query.answer("❌ Kode tidak ditemukan", True)
                else:
                    await callback_query.edit_message_text(
                        otp.text,
                        reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
                    )
                    return await X.delete_messages(X.me.id, otp.id)
            except Exception as error:
                return await callback_query.answer(error, True)
    elif query[0] == "get_phone":
        try:
            return await callback_query.edit_message_text(
                f"<b>📲 Nomer telepon <code>{X.me.id}</code> adalah <code>{X.me.phone_number}</code></b>",
                reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
            )
        except Exception as error:
            return await callback_query.answer(error, True)
    elif query[0] == "get_faktor":
        code = await dB.get_var(X.me.id, "PASSWORD")
        if code == None:
            return await callback_query.answer(
                "🔐 Kode verifikasi 2 langkah tidak ditemukan", True
            )
        else:
            return await callback_query.edit_message_text(
                f"<b>🔐 Kode verifikasi 2 langkah pengguna <code>{X.me.id}</code> adalah : <code>{code}</code></b>",
                reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
            )
    elif query[0] == "ub_deak":
        return await callback_query.edit_message_reply_markup(
            reply_markup=(ButtonUtils.deak(X.me.id, int(query[1])))
        )
    elif query[0] == "deak_akun":
        navy._ubot.remove(X)
        await X.invoke(raw.functions.account.DeleteAccount(reason="madarchod hu me"))
        return await callback_query.edit_message_text(
            Message.deak(X),
            reply_markup=(ButtonUtils.userbot(X.me.id, int(query[1]))),
        )


@CMD.UBOT("getubot")
@CMD.FAKE_NLX
async def _(client, message):
    em = Emoji(client)
    await em.get()
    query = "get_users"
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            return await message.delete()
    except Exception:
        logger.error(f"{traceback.format_exc()}")
        return await message.reply(f"{em.gagal}Error: {traceback.format_exc()}")


@CMD.CALLBACK("^del_ubot")
async def _(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    if user_id not in SUDO_OWNERS:
        return await callback_query.answer(
            f"<b>GAUSAH DIPENCET YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
            True,
        )
    await callback_query.answer()
    try:
        show = await bot.get_users(callback_query.data.split()[1])
        get_id = show.id
        get_mention = f"<a href=tg://user?id={get_id}>{show.first_name} {show.last_name or ''}</a>"
    except Exception:
        get_id = int(callback_query.data.split()[1])
        get_mention = f"<a href=tg://user?id={get_id}>Userbot</a>"
    for X in navy._ubot:
        if get_id == X.me.id:
            await X.unblock_user(bot.me.username)
            await dB.remove_ubot(X.me.id)
            await dB.rem_expired_date(X.me.id)
            navy._get_my_id.remove(X.me.id)
            navy._ubot.remove(X)
            await bot.send_message(
                LOG_SELLER,
                f"<b> ✅ {get_mention} Deleted on database</b>",
            )
            return await bot.send_message(
                X.me.id,
                f"<b>💬 Masa Aktif Anda Telah Habis</b>\n<b>Ads: {await Message._ads()}</b>",
            )
