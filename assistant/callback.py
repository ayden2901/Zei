import asyncio
import os
import sys
import traceback
from gc import get_objects
from uuid import uuid4
import pytz
from pyrogram import Client
import logging
import platform
import psutil
import pyrogram
import requests
from pyrogram.errors import FloodWait, MessageNotModified
from datetime import datetime
from pyrogram.enums import ParseMode
from pyrogram.helpers import ikb
from pyrogram.types import InlineKeyboardButton as Ikb
from pyrogram.types import (InlineKeyboardMarkup, InputMediaAnimation,
                            InputMediaAudio, InputMediaDocument,
                            InputMediaPhoto, InputMediaVideo, CallbackQuery, InlineKeyboardButton)
from pyrogram.utils import unpack_inline_message_id


from config import COPY_ID, SUDO_OWNERS, DEVS, OWNER_ID, FAKE_DEVS
from Navy import bot, navy
from Navy.database import dB, state
from Navy.helpers import (CMD, ButtonUtils, Tools, gens_font, query_fonts,
                          trigger)
from Navy.logger import logger
from bot.cache import (
    absen_data,
    inline_mapping,
    inline_msg_cache,
    active_absen_inline_ids,
    active_absen_messages,
    absen_owners
)
from bot.cache import (
    save_inline_mapping_file,
    load_inline_mapping_file,
    get_today,
    get_absen_file_by_inline,
    load_absen_file,
    save_absen_file,
    save_inline_mapping,
    get_inline_mapping,
    save_inline_meta_file,
    load_inline_meta_file
)
from plugins.pmpermit import LIMIT

from .create_users import mari_buat_userbot
from .eval import eval_tasks, update_kode
from .help import cek_plugins
from .restart import (reset_costum_text, reset_emoji, reset_prefix,
                      restart_userbot)
from .start import start_home, join_seller
from .status import cek_status_akun
from .support import pengguna_nanya

MESSAGE_DICT = {}


@CMD.REGEX(trigger)
async def _(client, message):
    try:
        text = message.text
        if text in [
            "✨ Mulai Buat Userbot",
            "✨ Pembuatan Ulang Userbot",
            "✅ Lanjutkan Buat Userbot",
        ]:
            return await mari_buat_userbot(client, message)
        elif text == "❓ Status Akun":
            return await cek_status_akun(client, message)
        elif text.startswith("🔄 Reset"):
            data = text.split(" ")[2]
            if data == "Emoji":
                return await reset_emoji(client, message)
            elif data == "Prefix":
                return await reset_prefix(client, message)
            elif data == "Text":
                return await reset_costum_text(client, message)
        elif text == "🔄 Restart Userbot":
            return await restart_userbot(client, message)
        elif text == "🚀 Updates":
            return await update_kode(client, message)
        elif text == "🛠️ Cek Fitur":
            return await cek_plugins(client, message)
        elif text == "🤔 Pertanyaan":
            return await pengguna_nanya(client, message)
        elif text == "💬 Hubungi Admins":
            return await contact_admins(client, message)
        elif text == "↩️ Beranda":
            return await join_seller(client, message)
        elif text == "🛑 Canceled":
            return await start_home(client, message)

    except Exception as er:
        logger.error(f"Terjadi error: {str(er)}")


@CMD.CALLBACK("^Canceleval")
async def _(_, callback_query):
    await callback_query.answer()
    reply_message_id = callback_query.message.reply_to_message_id
    if not reply_message_id:
        return

    def cancel_task(task_id) -> bool:
        task = eval_tasks.get(task_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False

    canceled = cancel_task(reply_message_id)
    if not canceled:
        return


async def contact_admins(client, message):
    new_msg = """
<b>Dibawah ini adalah Admins Saya. Kamu dapat menghubungi salah satu dari mereka.</b>"""
    tombol = []
    row = []
    for admin in SUDO_OWNERS:
        try:
            try:
                user = await client.get_users(admin)
            except Exception:
                continue
            owner_name = user.first_name
            row.append(Ikb(owner_name, user_id=f"{user.id}"))
            if len(row) == 2:
                tombol.append(row)
                row = []
        except Exception as e:
            continue
    if row:
        tombol.append(row)
    last_row = [
        Ikb(text="❌ Tutup", callback_data="closed"),
    ]
    tombol.append(last_row)

    markup = InlineKeyboardMarkup(tombol)
    return await message.reply(new_msg, reply_markup=markup)


@CMD.CALLBACK("^close_menu")
async def close_menu_handler(client, cq):
    await cq.answer()
    try:
        await cq.message.delete()
    except Exception:
        await cq.answer("Gagal menutup pesan.", show_alert=True)


@CMD.CALLBACK("^close ")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        user = callback_query.from_user
        split = callback_query.data.split(maxsplit=1)[1]

        # Cek state (mode userbot)
        data = state.get(user.id, split)

        if not data:
            try:
                return await callback_query.message.delete()
            except Exception:
                return await callback_query.answer(
                    "Gagal menutup pesan.", True
                )

        message = next(
            (obj for obj in get_objects() if id(obj) == int(data["idm"])),
            None
        )

        if not message:
            return await callback_query.answer("Message not found", True)

        c = message._client
        state.clear_client(c.me.id)

        return await c.delete_messages(
            int(data["chat"]), int(data["_id"])
        )

    except Exception as er:
        logger.error(str(er))

@CMD.CALLBACK("^cb_pm")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        data = callback_query.data.split()
        user = callback_query.from_user.id
        maling = int(data[3])
        polisi = int(data[2])
        pm_ok = await dB.get_list_from_var(polisi, "PM_OKE")
        if data[1] == "ok":
            if user != polisi:
                return await callback_query.answer(
                    "This button not for you fvck!!", True
                )
            if maling not in pm_ok:
                await dB.add_to_var(polisi, "PM_OKE", maling)
                return await callback_query.edit_message_text(
                    "<b>User has been approved to send message.</b>"
                )
            else:
                return await callback_query.edit_message_text(
                    "<b>This user is already approved</b>"
                )
        elif data[1] == "no":
            if user != polisi:
                return await callback_query.answer(
                    "This button not for you fvck!!", True
                )
            if maling in pm_ok:
                await dB.remove_from_var(polisi, "PM_OKE", maling)
                return await callback_query.edit_message_text(
                    "<b>User has been disapproved to send message.</b>"
                )
            else:
                return await callback_query.edit_message_text(
                    "<b>This user is already disapproved</b>"
                )
        elif data[1] == "warn":
            Flood = state.get(polisi, maling)
            pm_warns = await dB.get_var(polisi, "PMLIMIT") or LIMIT
            return await callback_query.answer(
                f"⚠️ You have a chance {Flood}/{pm_warns} ❗\n\nIf you insist on sending messages continuously then you will be ⛔ blocked automatically and we will 📢 report your account as spam",
                True,
            )
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")


@CMD.CALLBACK("^cb_gc_info")
async def _(client, callback_query):
    await callback_query.answer()
    cek = state.get(client.me.id, "gc_info")
    state.set(client.me.id, "desc_gc", cek)
    usr = cek["username"]
    if usr is None:
        keyb = ikb([[("Desc", f"cb_desc {cek['id']}", "callback_data")]])
    else:
        keyb = ikb(
            [
                [
                    ("Chat", f"https://t.me/{usr}", "url"),
                    ("Desc", f"cb_desc {cek['id']}", "callback_data"),
                ]
            ]
        )
    cdesc = cek["desc"]
    if cdesc is None:
        pass
    else:
        pass
    msg = f"""
<b>ChatInfo:</b>
   <b>name:</b> <b>{cek['name']}</b>
      <b>id:</b> <code>{cek['id']}</code>
      <b>type:</b> <b>{cek['type']}</b>
      <b>dc_id:</b> <b>{cek['dc_id']}</b>
      <b>username:</b> <b>@{cek['username']}</b>
      <b>member:</b> <b>{cek['member']}</b>
      <b>protect:</b> <b>{cek['protect']}</b>
"""
    return await callback_query.edit_message_text(msg, reply_markup=keyb)


@CMD.CALLBACK("^cb_desc")
async def _(client, callback_query):
    await callback_query.answer()
    query = callback_query.data.split(None, 1)
    id_gc = query[1]
    data = state.get(client.me.id, "gc_info")
    if int(id_gc) == int(data["id"]):
        return await callback_query.answer(f"{data['desc']}", True)
    else:
        return await callback_query.answer("Tidak ada perasaan ini", True)


@CMD.CALLBACK("^copymsg")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        get_id = int(callback_query.data.split("_", 1)[1])
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        await message._client.unblock_user(bot.me.username)
        await callback_query.edit_message_text("<b>Proses Upload...</b>")
        copy = await message._client.send_message(
            bot.me.username, f"/kontol {message.text.split()[1]}"
        )
        msg = message.reply_to_message or message
        await asyncio.sleep(1.5)
        await copy.delete()
        async for get in message._client.search_messages(bot.me.username, limit=1):
            await message._client.copy_message(
                message.chat.id, bot.me.username, get.id, reply_to_message_id=msg.id
            )
            await message._client.delete_messages(
                message.chat.id, COPY_ID[message._client.me.id]
            )
            await get.delete()
    except Exception as error:
        await callback_query.edit_message_text(f"**ERROR:** <code>{error}</code>")


async def close_user(callback_query, user_id):
    pass


@CMD.CALLBACK("^cb")
async def _(client, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")
    btn_close = state.get("close_notes", "get_note")
    dia = callback_query.from_user
    type_mapping = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "animation": InputMediaAnimation,
        "audio": InputMediaAudio,
        "document": InputMediaDocument,
    }
    try:
        notetag = data[-2].replace("cb_", "")
        gw = data[-1]
        item = [x for x in navy._ubot if int(gw) == x.me.id]
        noteval = await dB.get_var(int(gw), notetag, "notes")

        if not noteval:
            await callback_query.answer("Catatan tidak ditemukan.", True)
            return

        full = (
            f"<a href=tg://user?id={dia.id}>{dia.first_name} {dia.last_name or ''}</a>"
        )
        await dB.add_userdata(
            dia.id,
            dia.first_name,
            dia.last_name,
            dia.username,
            dia.mention,
            full,
            dia.id,
        )

        for me in item:
            tks = noteval["result"].get("text")
            note_type = noteval["type"]
            file_id = noteval.get("file_id")
            note, button = ButtonUtils.parse_msg_buttons(tks)
            teks = await Tools.escape_tag(bot, dia.id, note, Tools.parse_words)
            button = await ButtonUtils.create_inline_keyboard(button, int(gw))
            for row in btn_close.inline_keyboard:
                button.inline_keyboard.append(row)
            try:
                if note_type == "text":
                    await callback_query.edit_message_text(
                        text=teks, reply_markup=button
                    )

                elif note_type in type_mapping and file_id:
                    InputMediaType = type_mapping[note_type]
                    media = InputMediaType(media=file_id, caption=teks)
                    await callback_query.edit_message_media(
                        media=media, reply_markup=button
                    )

                else:
                    await callback_query.edit_message_caption(
                        caption=teks, reply_markup=button
                    )

            except FloodWait as e:
                return await callback_query.answer(
                    f"FloodWait {e}, Please Waiting!!", True
                )
            except MessageNotModified:
                pass

    except Exception as e:
        print(f"Error in notes callback: {str(e)}")
        return await callback_query.answer(
            "Terjadi kesalahan saat memproses catatan.", True
        )


@CMD.CALLBACK("^get_font")
async def _(_, callback_query):
    await callback_query.answer()
    try:
        data = int(callback_query.data.split()[1])
        new = str(callback_query.data.split()[2])
        text = state.get(data, "FONT")
        get_new_font = gens_font(new, text)
        await callback_query.answer("Wait a minute!!", True)
        return await callback_query.edit_message_text(
            f"<b>Result:\n<code>{get_new_font}</code></b>"
        )
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


@CMD.CALLBACK("^prev_font")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        get_id, current_batch = map(int, callback_query.data.split()[1:])
        prev_batch = current_batch - 1

        if prev_batch < 0:
            prev_batch = len(query_fonts) - 1

        keyboard = ButtonUtils.create_font_keyboard(
            query_fonts[prev_batch], get_id, prev_batch
        )

        buttons = InlineKeyboardMarkup(keyboard)
        return await callback_query.edit_message_reply_markup(reply_markup=buttons)
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


@CMD.CALLBACK("^next_font")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        get_id, current_batch = map(int, callback_query.data.split()[1:])
        next_batch = current_batch + 1

        if next_batch >= len(query_fonts):
            next_batch = 0

        keyboard = ButtonUtils.create_font_keyboard(
            query_fonts[next_batch], get_id, next_batch
        )

        buttons = InlineKeyboardMarkup(keyboard)
        return await callback_query.edit_message_reply_markup(reply_markup=buttons)
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


@CMD.CALLBACK("^refresh_cat")
async def _(client, callback_query):

    await callback_query.answer("Please wait a minute", True)
    buttons = ikb([[("Refresh cat", "refresh_cat")], [("Close", "close inline_cat")]])
    r = requests.get("https://api.thecatapi.com/v1/images/search")
    if r.status_code == 200:
        data = r.json()
        cat_url = data[0]["url"]
        if cat_url.endswith(".gif"):
            await callback_query.edit_message_animation(
                cat_url,
                caption="<blockquote><b>Meow 😽</b></blockquote>",
                reply_markup=buttons,
            )
        else:
            await callback_query.edit_message_media(
                InputMediaPhoto(
                    media=cat_url, caption="<blockquote><b>Meow 😽</b></blockquote>"
                ),
                reply_markup=buttons,
            )
    else:
        await callback_query.edit_message_text("Failed to refresh cat picture 🙀")


@CMD.CALLBACK("^prev_textpro")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        get_id, current_batch = map(int, callback_query.data.split()[1:])
        prev_batch = current_batch - 1

        if prev_batch < 0:
            prev_batch = len(Tools.query_textpro) - 1

        keyboard = ButtonUtils.create_buttons_textpro(
            Tools.query_textpro[prev_batch], get_id, prev_batch
        )

        buttons = InlineKeyboardMarkup(keyboard)
        state.set(get_id, "page_textpro", prev_batch)
        return await callback_query.edit_message_reply_markup(reply_markup=buttons)
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


@CMD.CALLBACK("^next_textpro")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        get_id, current_batch = map(int, callback_query.data.split()[1:])
        next_batch = current_batch + 1

        if next_batch >= len(Tools.query_textpro):
            next_batch = 0

        keyboard = ButtonUtils.create_buttons_textpro(
            Tools.query_textpro[next_batch], get_id, next_batch
        )

        buttons = InlineKeyboardMarkup(keyboard)
        state.set(get_id, "page_textpro", next_batch)
        return await callback_query.edit_message_reply_markup(reply_markup=buttons)
    except Exception as error:
        return await callback_query.answer(f"❌ Error: {error}", True)


@CMD.CALLBACK("^genpro")
async def _(client, callback_query):
    await callback_query.answer()
    await callback_query.answer("Wait a minute!!", True)
    query = callback_query.data.split()
    userid = int(query[1])
    command = str(query[2])
    text = state.get(userid, "TEXT_PRO")
    result_image = await Tools.gen_text_pro(text, command)
    page = state.get(userid, "page_textpro")
    keyboard = ButtonUtils.create_buttons_textpro(
        Tools.query_textpro[0], userid, current_batch=int(page)
    )
    buttons = InlineKeyboardMarkup(keyboard)
    if not result_image.startswith("ERROR"):
        logger.info(f"Result TextPro: {result_image}")
        try:
            image = InputMediaPhoto(
                media=result_image,
                caption=f"<blockquote>**Costum text:**\n\n{text}</blockquote>",
            )
            await callback_query.edit_message_media(media=image, reply_markup=buttons)
        except Exception as e:

            logger.error(f"Line 656: {traceback.format_exc()}")
            await callback_query.edit_message_text(f"Failed to send image: {str(e)}")
    else:
        logger.error(f"Line 659: {traceback.format_exc()}")
        await callback_query.edit_message_text(
            f"Failed to generate text pro:\n{result_image}"
        )


@CMD.CALLBACK("^nxttsearch")
async def _(_, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")
    userid = int(data[2])
    page = int(data[1])
    uniq = str(data[3])
    videos = state.get(userid, uniq)
    if videos is None:
        await callback_query.answer("Tidak ada halaman berikutnya.", show_alert=True)
        return
    await callback_query.answer()
    buttons = []
    for video in videos[page * 5 : (page + 1) * 5]:
        title = video["title"]
        video_link = video["play"]
        caption = f"<blockquote>{title}</blockquote>"

    if page > 0:
        buttons.append(
            [
                Ikb(
                    "Prev video", callback_data=f"nxttsearch_{page - 1}_{userid}_{uniq}"
                ),
                Ikb(
                    "Next video", callback_data=f"nxttsearch_{page + 1}_{userid}_{uniq}"
                ),
            ]
        )
        buttons.append([Ikb("Close", callback_data=f"close inline_ttsearch {uniq}")])
    else:
        buttons.append(
            [
                Ikb(
                    "Next video", callback_data=f"nxttsearch_{page + 1}_{userid}_{uniq}"
                ),
            ]
        )
        buttons.append([Ikb("Close", callback_data=f"close inline_ttsearch {uniq}")])
    reply_markup = InlineKeyboardMarkup(buttons)
    return await callback_query.edit_message_media(
        media=InputMediaVideo(
            media=video_link,
            caption=caption,
        ),
        reply_markup=reply_markup,
    )


@CMD.CALLBACK("^cqtiktok")
async def _(client, callback_query):
    await callback_query.answer()

    try:
        data = callback_query.data.split("_")
        userid = int(data[2])
        query = str(data[1])
        results = state.get(userid, "result_ttdownload")
        get_id = state.get(userid, "idm_ttdownload")
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        name = f"{str(uuid4())}"
        if query == "videodl":
            video_link = results["video"][0]
            caption = results["title"]
            logger.info(f"Video tiktok link: {video_link}")
            await callback_query.edit_message_text(
                "**Please wait, trying to send the video...**"
            )
            video = f"downloads/{name.split('-')[1]}.mp4"
            await message._client.bash(f"curl -L {video_link} -o {video}")
            await message.reply_video(video, caption=caption)
            if os.path.exists(video):
                os.remove(video)
            await asyncio.sleep(2)
            ids = (unpack_inline_message_id(callback_query.inline_message_id)).id
            return await message._client.delete_messages(message.chat.id, ids)
        elif query == "audiodl":
            audio_link = results["audio"][0]
            caption = results["title"]
            logger.info(f"Audio tiktok link: {audio_link}")
            await callback_query.edit_message_text(
                "**Please wait, trying to send the audio...**"
            )
            audio = f"downloads/{name.split('-')[1]}.mp3"
            await message._client.bash(f"curl -L {audio_link} -o {audio}")
            await message.reply_audio(audio, caption=caption)
            await asyncio.sleep(2)
            if os.path.exists(audio):
                os.remove(audio)
            ids = (unpack_inline_message_id(callback_query.inline_message_id)).id
            return await message._client.delete_messages(message.chat.id, ids)
    except Exception as er:
        logger.error(f"Cq tiktok dl: {traceback.format_exc()}")
        return await callback_query.edit_message_text(f"**An errror:** {str(er)}")


@CMD.CALLBACK("^nxtspotify")
async def _(_, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")
    userid = int(data[2])
    page = int(data[1])
    uniq = str(data[3])
    audios = state.get(userid, uniq)
    if audios is None:
        await callback_query.answer("Tidak ada halaman berikutnya.", show_alert=True)
        return
    await callback_query.answer()
    buttons = []
    for audio in audios[page * 5 : (page + 1) * 5]:
        caption = f"""<blockquote>
🎶 **Title:** {audio['title']}
👥 **Popularity:** {audio['popularity']}
⏳ **Duration:** {audio['duration']}
🖇️ **Spotify URL:** <a href='{audio['url']}'>here</a></blockquote>"""
        state.set(userid, "fordlspotify", audio["url"])
        logger.info(f"Url line 796: {audio['url']}")
    buttons.append([Ikb("Download audio", callback_data=f"dlspot_{userid}_{uniq}")])
    if page > 0:
        buttons.append(
            [
                Ikb(
                    "Prev audio", callback_data=f"nxtspotify_{page - 1}_{userid}_{uniq}"
                ),
                Ikb(
                    "Next audio", callback_data=f"nxtspotify_{page + 1}_{userid}_{uniq}"
                ),
            ]
        )
        buttons.append([Ikb("Close", callback_data=f"close inline_spotify {uniq}")])
    else:
        buttons.append(
            [
                Ikb(
                    "Next audio", callback_data=f"nxtspotify_{page + 1}_{userid}_{uniq}"
                ),
            ]
        )
        buttons.append([Ikb("Close", callback_data=f"close inline_spotify {uniq}")])
    # state.set(userid, "fordlspotify", audio["url"])
    reply_markup = InlineKeyboardMarkup(buttons)
    return await callback_query.edit_message_text(
        caption, reply_markup=reply_markup, disable_web_page_preview=True
    )


@CMD.CALLBACK("^dlspot")
async def _(_, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")
    userid = int(data[1])
    uniq = str(data[2])
    data = state.get(userid, uniq)
    get_id = state.get(userid, "idm_spotdl")
    message = [obj for obj in get_objects() if id(obj) == get_id][0]
    link = data[0]["url"]
    audio, caption = await Tools.download_spotify(link)
    await callback_query.edit_message_text(
        "**Please wait, trying to send the audio...**"
    )
    await message.reply_audio(audio, caption=caption)
    await asyncio.sleep(2)
    ids = (unpack_inline_message_id(callback_query.inline_message_id)).id
    if os.path.exists(audio):
        os.remove(audio)
    try:
        return await message._client.delete_messages(
            message.chat.id,
            ids,
        )
    except Exception:
        logger.error(f"Cant delete inline_message_id: {traceback.format_exc()}")


@CMD.CALLBACK("^nxpinsearch")
async def _(_, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    photos = state.get(uniq, uniq)

    if not photos:
        await callback_query.answer(
            "Tidak ada foto untuk ditampilkan.", show_alert=True
        )
        return

    total_photos = len(photos)

    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return

    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            Ikb("⬅️ Prev", callback_data=f"nxpinsearch_{page - 1}_{uniq}")
        )
    if page < total_photos - 1:
        nav_buttons.append(
            Ikb("➡️ Next", callback_data=f"nxpinsearch_{page + 1}_{uniq}")
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([Ikb("❌ Close", callback_data=f"close inline_pinsearch {uniq}")])

    reply_markup = InlineKeyboardMarkup(buttons)

    await callback_query.edit_message_media(
        media=InputMediaPhoto(media=photos[page]), reply_markup=reply_markup
    )


@CMD.CALLBACK("^bola_date")
async def _(client, callback_query):
    await callback_query.answer()
    split = callback_query.data.split()
    if len(split) > 1:
        state_key = split[1]
        stored_data = state.get(state_key, state_key)

        buttons = []
        temp_row = []
        for liga_date in stored_data:
            button = Ikb(
                text=liga_date["LigaDate"],
                callback_data=f"bola_matches {state_key} {liga_date['LigaDate']}",
            )
            temp_row.append(button)

            if len(temp_row) == 3:
                buttons.append(temp_row)
                temp_row = []

        if temp_row:
            buttons.append(temp_row)

        buttons.append([Ikb(text="Close", callback_data="close inline_bola")])
        keyboard = InlineKeyboardMarkup(buttons)

        return await callback_query.edit_message_text(
            text="<b>Select a date to view football matches:</b>",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        return await callback_query.edit_message_text("No data found.")


@CMD.CALLBACK("^bola_matches")
async def _(client, callback_query):
    await callback_query.answer()
    split = callback_query.data.split()
    if len(split) > 2:
        state_key = split[1]
        selected_date = split[2]
        stored_data = state.get(state_key, state_key)

        date_matches = next(
            (
                date
                for date in stored_data
                if date["LigaDate"].split()[0] == selected_date.split()[0]
            ),
            None,
        )

        if date_matches:
            text = f"Football Matches on {selected_date}\n\n"
            for league in date_matches["LigaItem"]:
                text += f"🏆 {league['NameLiga']}\n"
                for match in league["Match"]:
                    text += f"⚽ {match['team']} at {match['time']}\n"

            buttons = [
                [Ikb(text="« Back", callback_data=f"bola_date {state_key}")],
                [Ikb(text="Close", callback_data="close inline_bola")],
            ]
            keyboard = InlineKeyboardMarkup(buttons)

            return await callback_query.edit_message_text(
                text=f"<blockquote><b>{text}</b></blockquote>",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        else:
            return await callback_query.answer("Silahkan ulangi fitur bola!!", True)


@CMD.CALLBACK("^news_")
async def _(client, callback_query):
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    berita = state.get(uniq, uniq)

    if not berita:
        await callback_query.answer(
            "Tidak ada berita untuk ditampilkan.", show_alert=True
        )
        return

    total_photos = len(berita)

    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", show_alert=True)
        return

    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(Ikb("⬅️ Prev", callback_data=f"news_{page - 1}_{uniq}"))
    if page < total_photos - 1:
        nav_buttons.append(Ikb("➡️ Next", callback_data=f"news_{page + 1}_{uniq}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([Ikb("❌ Close", callback_data=f"close inline_news {uniq}")])
    date = berita[page].get("berita_diupload", "-")
    caption = f"**Title:** {berita[page]['berita']}\n**Link:** {berita[page]['berita_url']}\n**Uploaded:** {date}"

    photo = berita[page]["berita_thumb"]
    reply_markup = InlineKeyboardMarkup(buttons)
    return await callback_query.edit_message_media(
        media=InputMediaPhoto(media=photo, caption=caption),
        reply_markup=reply_markup,
    )

from pyrogram import filters
from pyrogram.types import CallbackQuery

@bot.on_callback_query(filters.regex("spc_close"))
@CMD.CALLBACK("^spc_")
async def spc_callback(client, callback_query):
    data = callback_query.data

    if data.split(":")[0] == "spc_show":
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

        bt = datetime.fromtimestamp(psutil.boot_time())
        softw += f"`Waktu Hidup: {bt.day}/{bt.month}/{bt.year} {bt.hour}:{bt.minute}:{bt.second}`\n"

        cpu = "**🧠 Informasi CPU**\n"
        cpu += f"`Physical cores   : {psutil.cpu_count(logical=False)}`\n"
        cpu += f"`Total cores      : {psutil.cpu_count(logical=True)}`\n"
        freq = psutil.cpu_freq()
        cpu += f"`Max Frequency    : {freq.max:.2f} MHz`\n"
        cpu += f"`Min Frequency    : {freq.min:.2f} MHz`\n"
        cpu += f"`Current Frequency: {freq.current:.2f} MHz`\n"
        cpu += "**💡 CPU Usage Per Core**\n"
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
            cpu += f"`Core {i} : {percentage}%`\n"
        cpu += "**⚙️ Total CPU Usage**\n"
        cpu += f"`All Cores: {psutil.cpu_percent()}%`\n"

        mem = psutil.virtual_memory()
        memory = "**📦 Memori**\n"
        memory += f"`Total     : {get_size(mem.total)}`\n"
        memory += f"`Available : {get_size(mem.available)}`\n"
        memory += f"`Used      : {get_size(mem.used)}`\n"
        memory += f"`Percent   : {mem.percent}%`\n"

        net = psutil.net_io_counters()
        bandwidth = "**📶 Bandwidth**\n"
        bandwidth += f"`Upload   : {get_size(net.bytes_sent)}`\n"
        bandwidth += f"`Download : {get_size(net.bytes_recv)}`\n"

        pyver = "**⚙️ Python / Library**\n"
        pyver += f"`Python   : {sys.version.split()[0]}`\n"
        pyver += f"`Pyrogram : {pyrogram.__version__}`\n"
        pyver += "`PyTgCalls: [N/A]`\n"

        result_text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{softw}"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{cpu}"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{memory}"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{bandwidth}"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{pyver}"
            "━━━━━━━━━━━━━━━━━━━━"
        )

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Close", callback_data="spc_close")]]
        )

        await callback_query.edit_message_text(result_text, reply_markup=keyboard)
        await callback_query.answer()

    elif data == "spc_close":
        try:
            await callback_query.edit_message_text("✅ Ditutup oleh pengguna.")
            await callback_query.answer()
            await asyncio.sleep(5)
            await client.delete_messages(
                chat_id=callback_query.message.chat.id,
                message_ids=callback_query.message.message_id
            )
        except Exception as e:
            print(f"Gagal menghapus pesan: {e}")

@CMD.CALLBACK("^absen_")
async def absen_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    user = callback_query.from_user
    msg = callback_query.message
    inline_id = callback_query.inline_message_id

    # Tentukan key
    absen_key = f"{msg.chat.id}_{msg.id}" if msg else inline_id
    if not absen_key:
        return await callback_query.answer("❌ Gagal mengambil info pesan!", show_alert=True)

    # Header baru jika belum ada
    if absen_key not in absen_data:
        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        hari = now.strftime("%A")
        tanggal = now.strftime("%d-%m-%Y")
        fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        mention = f'<a href="tg://user?id={user.id}">{fullname}</a>'
        header = (
            f"<blockquote>"
            f"📋 <b><u>DAFTAR ABSENSI HARIAN</u></b>\n\n"
            f"Hari : {hari}\n"
            f"Tanggal : {tanggal}\n\n"
            f"Di Absensi oleh : {mention}"
            f"</blockquote>"
        )
        absen_data[absen_key] = {"header": header, "daftar": {}}
        absen_owners[absen_key] = user.id

    # Tombol absen
    if data == "absen_tap":
        waktu = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M")
        fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

        if user.id in absen_data[absen_key]["daftar"]:
            return await callback_query.answer("Kamu sudah absen hari ini!", show_alert=True)

        absen_data[absen_key]["daftar"][user.id] = (fullname, waktu)

        daftar = ""
        for i, (uid, (nama, jam)) in enumerate(absen_data[absen_key]["daftar"].items(), start=1):
            daftar += f"{i}. {nama} - {jam}\n"

        teks_baru = f"{absen_data[absen_key]['header']}\n<i>Yang sudah absen:</i>\n{daftar}"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Absen Sekarang", callback_data="absen_tap")],
            [InlineKeyboardButton("❌ Tutup", callback_data="absen_close")]
        ])

        if msg:
            await msg.edit_text(teks_baru, parse_mode=ParseMode.HTML, reply_markup=markup)
        else:
            await client.edit_inline_text(
                inline_message_id=inline_id,
                text=teks_baru,
                parse_mode=ParseMode.HTML,
                reply_markup=markup
            )

        return await callback_query.answer("✅ Berhasil absen!")

    # Tombol tutup
    elif data == "absen_close":
        pemilik = absen_owners.get(absen_key)
        if pemilik != user.id:
            return await callback_query.answer("❌ Hanya pembuat absen yang bisa menutup!", show_alert=True)

        absen_data.pop(absen_key, None)
        absen_owners.pop(absen_key, None)

        if msg:
            await msg.edit_text("✅ Absensi hari ini telah ditutup.")
        else:
            await client.edit_inline_text(
                inline_message_id=inline_id,
                text="✅ Absensi hari ini telah ditutup."
            )

        return await callback_query.answer("✅ Absen ditutup.")


# Fungsi membuat InlineQueryResultArticle
async def inline_absen(inline_query, chat_id=None):
    try:
        user = inline_query
        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        hari = now.strftime("%A")
        tanggal = now.strftime("%d-%m-%Y")
        fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        mention = f'<a href="tg://user?id={user.id}">{fullname}</a>'
        header = (
            f"<blockquote>"
            f"📋 <b><u>DAFTAR ABSENSI HARIAN</u></b>\n\n"
            f"Hari : {hari}\n"
            f"Tanggal : {tanggal}\n\n"
            f"Di Absensi oleh : {mention}"
            f"</blockquote>"
        )
        teks = header + "\n<b>Belum Ada Yang Absen Hari Ini</b>"

        content = InputTextMessageContent(teks, parse_mode=ParseMode.HTML)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Absen Sekarang", callback_data="absen_tap")],
            [InlineKeyboardButton("❌ Tutup", callback_data="absen_close")]
        ])

        result_article = InlineQueryResultArticle(
            title="📌 Kirim Daftar Absen",
            input_message_content=content,
            reply_markup=markup,
            id=f"absen_{chat_id or user.id}"  # unik
        )

        if chat_id:
            active_absen_inline_ids[chat_id] = result_article.id
            absen_owners[result_article.id] = user.id

        return [result_article]

    except Exception as e:
        import traceback, logging
        logging.error(traceback.format_exc())
        return []


@CMD.CALLBACK("^gcast_cancel")
async def gcast_cancel_callback(client, cq: CallbackQuery):
    task_id = cq.data.split(":", 1)[1]
    user_id = cq.from_user.id
    prefix = client.get_prefix(client.me.id)

    owner_task = GCAST_OWNERS.get(task_id)

    if user_id != owner_task and user_id != OWNER_ID and user_id not in FAKE_DEVS and user_id not in DEVS:
        return await cq.answer("❌ Kamu tidak punya izin membatalkan task ini", show_alert=True)

    if not task.is_active(task_id):
        return await cq.answer("⚠️ Task sudah tidak aktif", show_alert=True)

    await cq.answer("🛑 Cancelling task...")

    # Hentikan task
    task.end_task(task_id)
    GCAST_OWNERS.pop(task_id, None)

    try:
        if cq.inline_message_id:
            await client.edit_inline_text(
                inline_message_id=cq.inline_message_id,
                text=f"🛑 <b>Task #{task_id} telah dibatalkan oleh pembuatnya</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
        elif cq.message:
            await cq.message.edit(
                f"🛑 <b>Task #{task_id} telah dibatalkan oleh pembuatnya</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
    except Exception:
        pass

"""
@CMD.CALLBACK("^selectedtopic_")
async def selected_topic(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in navy._get_my_id:
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    chat_id = int(data[1])
    tread_id = int(data[2])
    title = str(data[3])
    await dB.set_var(chat_id, "SELECTED_TOPIC", tread_id)
    return await callback_query.answer(f"Changed send topic to {title}.")
"""