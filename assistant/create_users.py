import asyncio
import importlib
from datetime import datetime

import hydrogram
from dateutil.relativedelta import relativedelta
from pyrogram.helpers import ikb, kb
from pyrogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                            ReplyKeyboardRemove)
from pytz import timezone

from config import API_HASH, API_ID, LOG_SELLER, MAX_BOT
from Navy import AKSES_DEPLOY, BOT_ID, UserBot, bot, dB, navy
from Navy.helpers import CMD, ButtonUtils, Message, no_trigger
from Navy.logger import logger
from plugins import PLUGINS


async def setExpiredUser(user_id):
    seles = await dB.get_list_from_var(BOT_ID, "SELLER")
    if user_id in seles:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=12)
        await dB.set_expired_date(user_id, expired)
    else:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=1)
        await dB.set_expired_date(user_id, expired)


async def mari_buat_userbot(client, message):
    user_id = message.from_user.id
    if user_id in navy._get_my_id:
        return await client.send_message(
            user_id,
            "<b><blockquote>Anda telah memasang userbot</blockquote></b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    if len(navy._ubot) == MAX_BOT:
        buttons = kb(
            [["💬 Hubungi Admins"]], resize_keyboard=True, one_time_keyboard=True
        )
        return await message.reply(
            f"""
<b>❌ Tidak dapat membuat Userbot !</b>

<b>📚 Karena Telah Mencapai Yang Telah Di Tentukan : {len(navy._ubot)}</b>

<b>👮‍♂ Silakan Hubungi Admins . </b>
""",
            reply_markup=buttons,
        )
    if user_id not in AKSES_DEPLOY:
        buttons = ikb([[("📃 Saya Setuju", "go_payment")], [("❌ Tutup", "closed")]])
        text = f"<blockquote>{await Message.policy_message()}</blockquote>"
        return await message.reply(
            text,
            disable_web_page_preview=True,
            reply_markup=buttons,
        )
    else:
        return await create_userbots(client, message)

async def create_userbots(client, message):
    try:
        user_id = message.from_user.id
        tutor = "<b><a href='https://my.telegram.org/auth'>Klik disini untuk membuat API ID dan API HASH</a></b>"
        if API_ID and API_HASH:
            api_id = API_ID
            api_hash = API_HASH
        else:
            try:
                api_id_msg = await client.ask(
                    user_id,
                    f"<blockquote expandable><b>Silahkan kirim API ID kamu untuk melanjutkan.</b></blockquote>\n\n{tutor}\n\n<b>Ads: {await Message._ads()}</b>",
                    timeout=300,
                    disable_web_page_preview=True,
                )
            except asyncio.TimeoutError:
                return await client.send_message(
                    user_id, "<blockquote>**Waktu habis, Silahkan memulai ulang.**</blockquote>",
                )
            if api_id_msg.text in no_trigger:
                return await bot.send_message(
                    user_id,
                    "<blockquote><b>Proses di batalkan.</b></blockquote>",

reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            api_id = int(api_id_msg.text)

            try:
                api_hash_msg = await client.ask(
                    user_id,
                    f"<blockquote expandable><b>Silahkan kirim API HASH kamu untuk melanjutkan.</b></blockquote>\n\n{tutor}\n\n<b>Ads: {await Message._ads()}</b>",
                    timeout=300,
                    disable_web_page_preview=True,
                )
            except asyncio.TimeoutError:
                return await client.send_message(
                    user_id, "<blockquote>**Waktu habis, Silahkan memulai ulang.**</blockquote>",
                )
            if api_hash_msg.text in no_trigger:
                return await bot.send_message(
                    user_id,
                    "<blockquote><b>Proses di batalkan.</b></blockquote>",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            api_hash = int(api_hash_msg.text)
        anu = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text="Kontak Saya", request_contact=True)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        anu = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text="Kontak Saya", request_contact=True)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            phone = await client.ask(
                user_id,
                f"<blockquote expandable><b>Silahkan klik tombol <u>Kontak Saya</u> untuk mengirimkan Nomor Telepon Telegram Anda.</b></blockquote>\n<b>Ads: {await Message._ads()}</b>",
                reply_markup=anu,
            )
            phone_number = phone.contact.phone_number
        except AttributeError:
            try:
                phone = await client.ask(
                    user_id,
                    f"<blockquote expandable><b>Silahkan klik tombol <u>Kontak Saya</u> untuk mengirimkan Nomor Telepon Telegram Anda.</b></blockquote>\n<b>Ads: {await Message._ads()}</b>",
                    reply_markup=anu,
                )
                phone_number = phone.contact.phone_number
            except Exception:
                return await bot.send_message(
                    user_id,
                    "<blockquote><b>PEA, punya mata dipake buat baca!! jangan BOKEP mulu.</b></blockquote>",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
        new_client = hydrogram.Client(
            name=str(user_id),
            api_id=api_id,
            api_hash=api_hash,
            in_memory=True,
        )
        await asyncio.sleep(2)
        get_otp = await client.send_message(
            user_id,
            f"<b><blockquote>Sedang Mengirim Kode OTP...</blockquote></b>\n<b>Ads: {await Message._ads()}</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
        await new_client.connect()
        try:
            code = await new_client.send_code(phone_number.strip())
        except hydrogram.errors.exceptions.bad_request_400.ApiIdInvalid as AID:
            await get_otp.delete()
            return await client.send_message(user_id, AID)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberInvalid as PNI:
            await get_otp.delete()
            return await client.send_message(user_id, PNI)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberFlood as PNF:
            await get_otp.delete()
            return await client.send_message(user_id, PNF)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberBanned as PNB:
            await get_otp.delete()
            return await client.send_message(user_id, PNB)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberUnoccupied as PNU:
            await get_otp.delete()
            return await client.send_message(user_id, PNU)
        except Exception as error:
            await get_otp.delete()
            return await client.send_message(
                user_id,
                f"<b>ERROR:</b> {error}",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )
        await get_otp.delete()
        otp = await client.ask(
            user_id,
            f"<b><blockquote expandable>Silakan Periksa Kode OTP dari <a href=tg://openmessage?user_id=777000>Akun Telegram</a> Resmi. Kirim Kode OTP ke sini setelah membaca Format di bawah ini.</b>\n\nJika Kode OTP adalah <code>12345</code> Tolong <b>[ TAMBAHKAN SPASI ]</b> kirimkan Seperti ini <code>1 2 3 4 5</code>.</blockquote></b>\n<b>Ads: {await Message._ads()}</b>",
        )
        if otp.text in no_trigger:
            return await client.send_message(
                user_id,
                f"<blockquote><b>Proses di batalkan.</b></blockquote>\n<b>Ads: {await Message._ads()}</b>",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )
        otp_code = otp.text
        try:
            await new_client.sign_in(
                phone_number.strip(),
                code.phone_code_hash,
                phone_code=" ".join(str(otp_code)),
            )
        except hydrogram.errors.exceptions.bad_request_400.PhoneCodeInvalid as PCI:
            return await client.send_message(user_id, PCI)
        except hydrogram.errors.exceptions.bad_request_400.PhoneCodeExpired as PCE:
            return await client.send_message(user_id, PCE)
        except hydrogram.errors.exceptions.bad_request_400.BadRequest as error:
            return await client.send_message(
                user_id,
                f"<b>ERROR:</b> {error}",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )
        except hydrogram.errors.exceptions.unauthorized_401.SessionPasswordNeeded:
            two_step_code = await client.ask(
                user_id,
                f"<b><blockquote expandable>Akun anda Telah mengaktifkan Verifikasi Dua Langkah. Silahkan Kirimkan Passwordnya.</blockquote></b>\n<b>Ads: {await Message._ads()}</b>",
            )
            if two_step_code.text in no_trigger:
                return await client.send_message(
                    user_id,
                    f"<blockquote><b>Proses di batalkan.</b></blockquote>\n<b>Ads: {await Message._ads()}</b>",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            new_code = two_step_code.text
            try:
                await new_client.check_password(new_code)
                await dB.set_var(user_id, "PASSWORD", new_code)
            except Exception as error:
                return await client.send_message(
                    user_id,
                    f"<b>ERROR:</b> {error}",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
        session_string = await new_client.export_session_string()
        await new_client.disconnect()
        new_client.storage.session_string = session_string
        new_client.in_memory = False
        bot_msg = await client.send_message(
            user_id,
            f"<b><blockquote expandable>Tunggu proses selama 1-5 menit...\nKami sedang menghidupkan Userbot Anda.</blockquote></b>\n<b>Ads: {await Message._ads()}</b>",
            disable_web_page_preview=True,
        )
        await asyncio.sleep(2)
        kn_client = UserBot(
            name=str(user_id),
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            in_memory=True,
        )
        try:
            await kn_client.start()
        except Exception as e:
            logger.error(f"Error Client: {str(e)}")
        if not await dB.get_expired_date(kn_client.me.id):
            await setExpiredUser(kn_client.me.id)
        await dB.add_ubot(
            user_id=int(kn_client.me.id),
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
        )
        # logger.info(f"User: {user_id}\nClient: {kn_client.me.id}")
        if not user_id == kn_client.me.id:
            navy._ubot.remove(kn_client)
            await dB.remove_ubot(kn_client.me.id)
            await kn_client.log_out()
            return await bot_msg.edit(
                f"<blockquote><b>Gunakan akun anda sendiri, bukan orang lain!!</b></blockquote>\n<b>Ads: {await Message._ads()}</b>"
            )
        # Emoji.set_emotes(kn_client, kn_client.me.is_premium)
        await asyncio.sleep(1)
        for mod in PLUGINS:
            importlib.reload(importlib.import_module(f"plugins.{mod}"))
        seles = await dB.get_list_from_var(BOT_ID, "SELLER")
        if kn_client.me.id not in seles:
            try:
                AKSES_DEPLOY.remove(kn_client.me.id)
            except Exception:
                pass
        try:
            await kn_client.join_chat ("https://t.me/zeisupport")
            await kn_client.join_chat("https://t.me/storezeii")
            await kn_client.join_chat("https://t.me/carisleepcall_telegram")
            await kn_client.join_chat("https://t.me/+UlAijlU394k3YWI9")
            await kn_client.join_chat("https://t.me/StarNightNih")
        except Exception:
            pass
        prefix = navy.get_prefix(kn_client.me.id)
        # logger.info(f"Prefix: {prefix}")
        keyb = ButtonUtils.start_menu(is_admin=False)
        # logger.info(f"Button: {keyb}")
        exp = await dB.get_expired_date(kn_client.me.id)
        # logger.info(f"Expired: {exp}")
        expir = exp.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        # logger.info(f"Prefix Parses: {expir}")
        text_done = f"""
    <blockquote expandable><b>🔥 {bot.me.mention} Berhasil Di Aktifkan
    ➡️ Akun: <a href=tg://openmessage?user_id={kn_client.me.id}>{kn_client.me.first_name} {kn_client.me.last_name or ''}</a>
    ➡️ ID: <code>{kn_client.me.id}</code>
    ➡️ Prefixes: {' '.join(prefix)}
    ➡️ Masa Aktif: {expir}</b></blockquote>
    <b>Ads: {await Message._ads()}</b>"""
        await bot_msg.edit(text_done, disable_web_page_preview=True, reply_markup=keyb)
        return await client.send_message(
            LOG_SELLER,
            f"""
    <b>❏ Notifikasi Userbot Aktif</b>
    <b> ├ Akun :</b> <a href=tg://user?id={kn_client.me.id}>{kn_client.me.first_name} {kn_client.me.last_name or ''}</a> 
    <b> ╰ ID :</b> <code>{kn_client.me.id}</code>
    """,
            reply_markup=ikb(
                [
                    [
                        (
                            "Cek Kadaluarsa",
                            f"cek_masa_aktif {kn_client.me.id}",
                            "callback_data",
                        )
                    ]
                ]
            ),
            disable_web_page_preview=True,
        )
    except Exception as er:
        logger.error(f"{str(er)}")


@CMD.CALLBACK("^cek_masa_aktif")
async def _(client, cq):
    user_id = int(cq.data.split()[1])
    try:
        expired = await dB.get_expired_date(user_id)
        habis = expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        return await cq.answer(f"⏳ Waktu: {habis}", True)
    except Exception:
        return await cq.answer("✅ Sudah tidak aktif", True)


@CMD.CALLBACK("^closed")
async def _(client, cq):
    await cq.answer()
    return await cq.message.delete()
