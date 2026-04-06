import asyncio
import random
import sys
import traceback
from datetime import datetime
from gc import get_objects
from time import time
from uuid import uuid4
import pytz
import platform, psutil, pyrogram
from pyrogram import Client
import requests
from bot.cache import (
    absen_data,
    inline_mapping,
    inline_msg_cache,
    active_absen_inline_ids,
    active_absen_messages,
    absen_owners
)
from plugins.calculator import inline_calculator
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
import asyncio
import os
import random
import traceback
from datetime import datetime
from gc import get_objects
from time import time
from uuid import uuid4

import requests
from pyrogram import enums, raw
from pyrogram.errors import UserNotParticipant
from pyrogram.helpers import ikb
from pyrogram.raw.functions import Ping
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.types import (Chat, InlineKeyboardButton, InlineKeyboardMarkup,
                            InlineQueryResultAnimation,
                            InlineQueryResultArticle,
                            InlineQueryResultCachedAnimation,
                            InlineQueryResultCachedAudio,
                            InlineQueryResultCachedDocument,
                            InlineQueryResultCachedPhoto,
                            InlineQueryResultCachedSticker,
                            InlineQueryResultCachedVideo,
                            InlineQueryResultCachedVoice,
                            InlineQueryResultPhoto, InlineQueryResultVideo,
                            InputTextMessageContent, InlineQuery, CallbackQuery, User)

from config import (API_MAELYN, BOT_ID, BOT_NAME, HELPABLE, SUDO_OWNERS, URL_LOGO, ALIVE_PIC)
from assistant.stats import get_absen_list
from Navy import bot, navy
from Navy.database import dB, state
from Navy.helpers import (CMD, ButtonUtils, Message, Tools, get_time,
                          paginate_modules, query_fonts, start_time, Emoji)
from Navy.logger import logger
from plugins.pmpermit import DEFAULT_TEXT, LIMIT


@CMD.INLINE()
async def _(client, inline_query):
    try:
        text = inline_query.query.strip().lower()
        if not text:
            return
        if len(text.split()) == 0:
            return
        answers = []
        if text.split()[0] == "help":
            answerss = await get_inline_help(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id, results=answerss, cache_time=0
            )
        elif text.split()[0] == "alive":
            answerss = await alive_inline(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_send":
            tuju = text.split()[1]
            answerss = await send_inline(answers, inline_query, int(tuju))
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_copy":
            tuju = text.split()[1]
            answerss = await copy_inline(answers, inline_query, int(tuju))
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "make_button":
            tuju = text.split()[1]
            answerss = await button_inline(answers, inline_query, int(tuju))
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "pmpermit_inline":
            answerss = await pmpermit_inline(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "copy_inline":
            answerss = await copy_inline_msg(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "user_info":
            answerss = await user_inline(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "gc_info":
            answerss = await gc_inline(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "get_note":
            answerss = await get_inline_note(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )

        elif text.split()[0] in ["calculator", "calc", "kalkulator"]:
            answerss = await inline_calculator(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )

        elif text.split()[0] == "inline_eval":
            answerss = await inline_eval(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_font":
            answerss = await inline_font(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_cat":
            answerss = await inline_cat(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_autobc":
            answerss = await inline_autobc(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_bola":
            answerss = await inline_bola(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "get_users":
            answerss = await get_navy_user(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_textpro":
            answerss = await inline_textpro(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_ttsearch":
            answerss = await inline_ttsearch(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_ttdownload":
            answerss = await inline_ttdownload(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_spotify":
            answerss = await inline_spotify(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_pinsearch":
            answerss = await inline_pinsearch(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_news":
            answerss = await inline_news(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
            )
        elif text.split()[0] == "inline_spc":
            answerss = await inline_spc(answers, inline_query)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0
            )
        elif text.split()[0] == "absen":
            answerss = await inline_absen(answers, inline_query)
            parts = text.split()
            if len(parts) <2:
                return await client.answer_inline_query(
                    inline_query.id,
                    results=answerss,
                    cache_time=0,
                    is_personal=True
                ) 
            try:
                chat_id = int(parts[1])
            except ValueError:
                return await client.answer_inline_query(
                    inline_query.id,
                    results=answerss,
                    cache_time=0,
                    is_personal=True
                )  
            answerss = await inline_absen(inline_query, chat_id)
            return await client.answer_inline_query(
                inline_query.id,
                results=answerss,
                cache_time=0,
                is_personal=False
            ) 

        
    except Exception:
        logger.error(f"{traceback.format_exc()}")


async def inline_news(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    try:
        buttons = ikb([[("➡️ Next", f"news_1_{uniq}")]])
        date = data[0].get("berita_diupload", "-")
        foto = data[0]["berita_thumb"]
        judul = f"**Title:** {data[0]['berita']}\n**Link:** {data[0]['berita_url']}\n**Uploaded:** {date}"
        results.append(
            InlineQueryResultPhoto(
                photo_url=foto,
                thumb_url=foto,
                caption=judul,
                title="Inline News",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline news: {traceback.format_exc()}")


async def inline_pinsearch(results, inline):
    uniq = str(inline.query.split()[1])
    data = state.get(uniq, uniq)
    try:
        buttons = ikb([[("➡️ Next", f"nxpinsearch_1_{uniq}")]])
        results.append(
            InlineQueryResultPhoto(
                photo_url=data[0],
                title="Inline Pinterest",
                reply_markup=buttons,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline result pindl: {traceback.format_exc()}")


async def inline_ttdownload(results, inline):
    userid = inline.from_user.id
    keyboard = ikb(
        [
            [
                ("Download Video", f"cqtiktok_videodl_{userid}"),
                ("Download Audio", f"cqtiktok_audiodl_{userid}"),
            ]
        ]
    )
    results.append(
        InlineQueryResultArticle(
            title="Tiktok Inline Download!",
            reply_markup=keyboard,
            input_message_content=InputTextMessageContent(
                "<blockquote><b>Please select the button below you want to download!</b></blockquote>"
            ),
        )
    )
    return results


async def inline_spotify(results, inline):
    userid = inline.from_user.id
    uniq = str(inline.query.split()[1])
    data = state.get(userid, uniq)
    state.set(userid, "fordlspotify", data[0]["url"])
    try:
        for audio in data:
            caption = f"""
<blockquote>🎶 **Title:** {audio['title']}
👥 **Popularity:** {audio['popularity']}
⏳ **Duration:** {audio['duration']}
🖇️ **Spotify URL:** <a href='{audio['url']}'>here</a></blockquote>"""
            buttons = ikb(
                [
                    [("Download audio", f"dlspot_{userid}_{uniq}")],
                    [("Next audio", f"nxtspotify_1_{userid}_{uniq}")],
                ]
            )
            results.append(
                InlineQueryResultArticle(
                    title="Tiktok Inline Download!",
                    reply_markup=buttons,
                    input_message_content=InputTextMessageContent(
                        caption, disable_web_page_preview=True
                    ),
                )
            )
        return results
    except Exception:
        logger.error(f"Inline result spotify: {traceback.format_exc()}")


async def inline_ttsearch(results, inline):
    userid = inline.from_user.id
    uniq = str(inline.query.split()[1])
    data = state.get(userid, uniq)
    try:
        for video in data:
            title = video["title"] or "-"
            video_link = video["play"]
            buttons = ikb([[("Next video", f"nxttsearch_1_{userid}_{uniq}")]])
            caption = f"<blockquote>{title}</blockquote>"
            results.append(
                InlineQueryResultVideo(
                    thumb_url=video_link,
                    video_url=video_link,
                    title=title,
                    caption=caption,
                    reply_markup=buttons,
                )
            )
        return results
    except Exception:
        logger.error(f"Inline result ttdl: {traceback.format_exc()}")


async def inline_bola(resultss, inline_query):
    url = f"https://api.maelyn.tech/api/jadwalbola?apikey={API_MAELYN}"
    result = await Tools.fetch.get(url)
    uniq = f"{str(uuid4())}"
    if result.status_code == 200:
        data = result.json()
        if data["status"] == "Success":
            buttons = []
            temp_row = []
            state.set(uniq.split("-")[0], uniq.split("-")[0], data["result"])
            for liga_date in data["result"]:
                button = InlineKeyboardButton(
                    text=liga_date["LigaDate"],
                    callback_data=f"bola_matches {uniq.split('-')[0]} {liga_date['LigaDate']}",
                )
                temp_row.append(button)

                if len(temp_row) == 3:
                    buttons.append(temp_row)
                    temp_row = []

            if temp_row:
                buttons.append(temp_row)
            last_row = [
                InlineKeyboardButton(
                    text="« Back", callback_data=f"bola_date {uniq.split('-')[0]}"
                ),
                InlineKeyboardButton(text="Close", callback_data="close inline_bola"),
            ]
            buttons.append(last_row)
            keyboard = InlineKeyboardMarkup(buttons)

            resultss.append(
                InlineQueryResultArticle(
                    title="Football Schedule",
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        "<b>Select a date to view football matches:</b>"
                    ),
                )
            )
    return resultss


async def get_navy_user(result, inline_query):
    try:
        msg = await Message.userbot(0)
        buttons = ButtonUtils.userbot(navy._ubot[0].me.id, 0)
        result.append(
            InlineQueryResultArticle(
                title="get user Inline!",
                reply_markup=buttons,
                input_message_content=InputTextMessageContent(msg),
            )
        )

        return result
    except Exception:
        logger.error(f"Line 209:\n {traceback.format_exc()}")


async def inline_textpro(result, inline):
    try:
        userid = inline.from_user.id
        text = state.get(userid, "TEXT_PRO")
        image_data = await Tools.gen_text_pro(text, "water-color")
        keyboard = ButtonUtils.create_buttons_textpro(
            Tools.query_textpro[0], userid, current_batch=0
        )
        state.set(userid, "page_textpro", 0)
        buttons = InlineKeyboardMarkup(keyboard)
        result.append(
            InlineQueryResultPhoto(
                photo_url=image_data,
                title="Text Pro Inline!",
                reply_markup=buttons,
                caption=f"<blockquote>**Costum text:**\n\n{text}</blockquote>",
            )
        )

        return result
    except Exception:
        logger.error(f"Line 180:\n {traceback.format_exc()}")


async def inline_cat(result, inline_query):
    buttons = ikb([[("Refresh cat", "refresh_cat")], [("Close", "close inline_cat")]])
    r = requests.get("https://api.thecatapi.com/v1/images/search")
    if r.status_code == 200:
        data = r.json()
        cat_url = data[0]["url"]
        if cat_url.endswith(".gif"):
            result.append(
                InlineQueryResultAnimation(
                    animation_url=cat_url,
                    title="cat Inline!",
                    reply_markup=buttons,
                    caption="<blockquote><b>Meow 😽</b></blockquote>",
                )
            )
        else:
            result.append(
                InlineQueryResultPhoto(
                    photo_url=cat_url,
                    title="cat Inline!",
                    reply_markup=buttons,
                    caption="<blockquote><b>Meow 😽</b></blockquote>",
                )
            )

    return result


async def inline_font(result, inline_query):
    get_id = inline_query.from_user.id

    keyboard = ButtonUtils.create_font_keyboard(query_fonts[0], get_id, current_batch=0)

    buttons = InlineKeyboardMarkup(keyboard)
    result.append(
        InlineQueryResultArticle(
            title="Font Inline!",
            reply_markup=buttons,
            input_message_content=InputTextMessageContent(
                "<blockquote><b>Please choice fonts:</b></blockquote>"
            ),
        )
    )
    return result


async def inline_eval(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    data = state.get(BOT_ID, uniq)
    if len(data) == 1:
        msg = data["time"]
        button = ikb([[("Close", f"close inline_eval {uniq}")]])
    else:
        msg = data["time"]
        button = ikb([[("Output", f"{data['url']}", "url")]])
    result.append(
        InlineQueryResultArticle(
            title="Inline Eval",
            input_message_content=InputTextMessageContent(
                msg, disable_web_page_preview=True
            ),
            reply_markup=button,
        )
    )
    return result


async def gc_inline(result, inline_query):
    ids = inline_query.from_user.id
    data = state.get(ids, "gc_info")
    state.set(BOT_ID, "gc_info", data)
    usr = data["username"]
    if usr is None:
        keyb = ikb([[("Desc", f"cb_desc {data['id']}", "callback_data")]])
    else:
        keyb = ikb(
            [
                [
                    ("Chat", f"https://t.me/{usr}", "url"),
                    ("Desc", f"cb_desc {data['id']}", "callback_data"),
                ]
            ]
        )
    msg = f"""
<blockquote><b>ChatInfo:</b>
   <b>name:</b> <b>{data['name']}</b>
      <b>id:</b> <code>{data['id']}</code>
      <b>type:</b> <b>{data['type']}</b>
      <b>dc_id:</b> <b>{data['dc_id']}</b>
      <b>username:</b> <b>@{data['username']}</b>
      <b>member:</b> <b>{data['member']}</b>
      <b>protect:</b> <b>{data['protect']}</b>
      <b>is_creator:</b> <b>{data['is_creator']}</b>
      <b>is_admin:</b> <b>{data['is_admin']}</b>
      <b>is_restricted:</b> <b>{data['is_restricted']}</b></blockquote>
"""
    result.append(
        InlineQueryResultArticle(
            title="gc info!",
            input_message_content=InputTextMessageContent(
                msg, disable_web_page_preview=True
            ),
            reply_markup=keyb,
        )
    )
    return result


async def user_inline(result, inline_query):
    ids = inline_query.from_user.id
    data = state.get(ids, "user_info")
    try:
        org = await bot.get_users(int(data["id"]))
        keyb = ikb([[("User", f"{org.id}", "user_id")]])
    except Exception:
        org = f"tg://openmessage?user_id={int(data['id'])}"
        keyb = ikb([[("User", f"{org}", "url")]])
    msg = f"""
<blockquote><b>UserInfo:</b>
   <b>name:</b> <b>{data['name']}</b>
      <b>id:</b> <code>{data['id']}</code>
      <b>created:</b> <code>{data['create']}</code>
      <b>is_contact:</b> <b>{data['contact']}</b>
      <b>is_premium:</b> <b>{data['premium']}</b>
      <b>is_deleted:</b> <b>{data['deleted']}</b>
      <b>is_bot:</b> <b>{data['isbot']}</b>
      <b>is_gbanned:</b> <b>{data['gbanned']}</b>
      <b>dc_id:</b> <b>{data['dc_id']}</b></blockquote>
"""
    result.append(
        InlineQueryResultArticle(
            title="user info!",
            input_message_content=InputTextMessageContent(
                msg, disable_web_page_preview=True
            ),
            reply_markup=keyb,
        )
    )
    return result


async def pmpermit_inline(result, inline_query):
    him = int(inline_query.query.split()[1])
    mee = inline_query.from_user.id
    gtext = await dB.get_var(mee, "PMTEXT")
    pm_text = gtext if gtext else DEFAULT_TEXT
    pm_warns = await dB.get_var(mee, "PMLIMIT") or LIMIT
    Flood = state.get(mee, him)
    teks, button = ButtonUtils.parse_msg_buttons(pm_text)
    button = ButtonUtils.create_inline_keyboard(button, mee)
    def_button = ikb(
        [
            [
                ("Approve", f"cb_pm ok {mee} {him}", "callback_data"),
                ("Disapprove", f"cb_pm no {mee} {him}", "callback_data"),
            ],
            [
                (
                    f"You have a warning {Flood} of {pm_warns} !!",
                    f"cb_pm warn {mee} {him}",
                    "callback_data",
                )
            ],
        ]
    )
    if button:
        for row in def_button.inline_keyboard:
            button.inline_keyboard.append(row)
    else:
        button = def_button
    tekss = await Tools.escape_tag(bot, him, teks, Tools.parse_words)
    media = await dB.get_var(mee, "PMMEDIA")
    if media:
        filem = (
            InlineQueryResultCachedVideo
            if media["type"] == "video"
            else InlineQueryResultCachedPhoto
        )
        url_ling = (
            {"video_file_id": media["file_id"]}
            if media["type"] == "video"
            else {"photo_file_id": media["file_id"]}
        )
        result.append(
            filem(
                **url_ling,
                title="PMPermit Media1",
                caption=tekss,
                reply_markup=button,
            )
        )
    else:
        result.append(
            InlineQueryResultArticle(
                title="PMPermit NOn-Media",
                input_message_content=InputTextMessageContent(
                    tekss,
                    disable_web_page_preview=True,
                ),
                reply_markup=button,
            )
        )
    return result


async def copy_inline(result, inline_query, user_id):
    try:
        _id = state.get(user_id, "inline_copy")
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if message:
            button = message.reply_to_message.reply_markup
            caption = (
                message.reply_to_message.text or message.reply_to_message.caption or ""
            )
            entities = (
                message.reply_to_message.entities
                or message.reply_to_message.caption_entities
                or ""
            )
            if message.reply_to_message.media:
                client = message._client
                reply = message.reply_to_message
                copy = await reply.copy(bot.me.username)
                sent = await client.send_message(
                    bot.me.username, "/id copy_media", reply_to_message_id=copy.id
                )
                await asyncio.sleep(1)
                await sent.delete()
                await copy.delete()
                data = state.get(user_id, "copy_media")
                file_id = str(data["file_id"])
                type = str(data["type"])
                type_mapping = {
                    "photo": InlineQueryResultCachedPhoto,
                    "video": InlineQueryResultCachedVideo,
                    "animation": InlineQueryResultCachedAnimation,
                    "audio": InlineQueryResultCachedAudio,
                    "document": InlineQueryResultCachedDocument,
                    "sticker": InlineQueryResultCachedSticker,
                    "voice": InlineQueryResultCachedVoice,
                }
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": caption,
                    "caption_entities": entities,
                    "reply_markup": button,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update(
                        {"video_file_id": file_id, "title": "Video with Button"}
                    )
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs["audio_file_id"] = file_id
                elif type == "document":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update(
                        {"voice_file_id": file_id, "title": "Voice with Button"}
                    )

                result.append(result_class(**kwargs))
            else:
                result.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Send Inline!",
                        reply_markup=button,
                        input_message_content=InputTextMessageContent(
                            caption,
                            entities=entities,
                        ),
                    )
                )
        return result
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")

async def inline_autobc(results, inline):
    chat = int(inline.query.split()[1])
    _id = inline.query.split()[2]
    try:
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if not message:
            return results
        client = message._client
        per_page = 50
        page = 0
        keyboard = []
        row = []
        title, data = await client.parse_topic(chat)
        print(f"Title: {title}")
        print(f"Data: {data}")
        try:
            sliced = data[page * per_page : (page + 1) * per_page]
            caption = f"<blockquote expandable><b>List Topic {title}\nSilahkan pilih topic untuk diatur:\n</b>"
            for idx, topic in enumerate(sliced):
                caption += f"<b>{idx + 1}. {topic['title']}</b>\n"
                button = InlineKeyboardButton(
                    text=str(idx + 1),
                    callback_data=f"selectedtopic_{chat}_{topic['id']}_{topic['title']}",
                )
                row.append(button)
                if (idx + 1) % 5 == 0:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(keyboard)
            caption += "</blockquote>"
        except Exception:
            logger.error(f"Inline autobc: {traceback.format_exc()}")
            return None
        results.append(
            InlineQueryResultArticle(
                title="Select Topic",
                input_message_content=InputTextMessageContent(caption),
                reply_markup=reply_markup,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline autobc: {traceback.format_exc()}")
        return None

async def send_inline(result, inline_query, user_id):
    try:
        _id = state.get(user_id, "inline_send")
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if message:
            button = message.reply_to_message.reply_markup
            caption = (
                message.reply_to_message.text or message.reply_to_message.caption or ""
            )
            entities = (
                message.reply_to_message.entities
                or message.reply_to_message.caption_entities
                or ""
            )
            if message.reply_to_message.media:
                client = message._client
                reply = message.reply_to_message
                copy = await reply.copy(bot.me.username)
                sent = await client.send_message(
                    bot.me.username, "/id send_media", reply_to_message_id=copy.id
                )
                await asyncio.sleep(1)
                await sent.delete()
                await copy.delete()
                data = state.get(user_id, "send_media")
                file_id = str(data["file_id"])
                type = str(data["type"])
                type_mapping = {
                    "photo": InlineQueryResultCachedPhoto,
                    "video": InlineQueryResultCachedVideo,
                    "animation": InlineQueryResultCachedAnimation,
                    "audio": InlineQueryResultCachedAudio,
                    "document": InlineQueryResultCachedDocument,
                    "sticker": InlineQueryResultCachedSticker,
                    "voice": InlineQueryResultCachedVoice,
                }
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": caption,
                    "reply_markup": button,
                    "caption_entities": entities,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update(
                        {"video_file_id": file_id, "title": "Video with Button"}
                    )
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs["audio_file_id"] = file_id
                elif type == "document":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update(
                        {"voice_file_id": file_id, "title": "Voice with Button"}
                    )

                result.append(result_class(**kwargs))
            else:
                result.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Send Inline!",
                        reply_markup=button,
                        input_message_content=InputTextMessageContent(
                            caption, entities=entities
                        ),
                    )
                )
        return result
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")


async def button_inline(result, inline_query, user_id):
    try:
        data = state.get(user_id, "button")
        text, button = ButtonUtils.parse_msg_buttons(data)
        if button:
            button = ButtonUtils.create_inline_keyboard(button, user_id)

        data2 = state.get(user_id, "button_media")
        if not data2:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Text Button!",
                    input_message_content=InputTextMessageContent(
                        text, disable_web_page_preview=True
                    ),
                    reply_markup=button,
                )
            )
        else:
            file_id = str(data2["file_id"])
            type = str(data2["type"])
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedAudio,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }

            if type in type_mapping:
                result_class = type_mapping[type]
                kwargs = {
                    "id": str(uuid4()),
                    "caption": text,
                    "reply_markup": button,
                }

                if type == "photo":
                    kwargs["photo_file_id"] = file_id
                elif type == "video":
                    kwargs.update(
                        {"video_file_id": file_id, "title": "Video with Button"}
                    )
                elif type == "animation":
                    kwargs["animation_file_id"] = file_id
                elif type == "audio":
                    kwargs["audio_file_id"] = file_id
                elif type == "document":
                    kwargs.update(
                        {"document_file_id": file_id, "title": "Document with Button"}
                    )
                elif type == "sticker":
                    kwargs["sticker_file_id"] = file_id
                elif type == "voice":
                    kwargs.update(
                        {"voice_file_id": file_id, "title": "Voice with Button"}
                    )

                result.append(result_class(**kwargs))

        return result
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")


async def copy_inline_msg(result, inline_query):
    result.append(
        InlineQueryResultArticle(
            title="Copy Inline!",
            reply_markup=ikb(
                [
                    [
                        (
                            "🔐 Unlock Message 🔐",
                            f"copymsg_{int(inline_query.query.split()[1])}",
                            "callback_data",
                        )
                    ]
                ]
            ),
            input_message_content=InputTextMessageContent(
                "<b>🔒 This is private content</b>"
            ),
        )
    )
    return result


async def get_inline_help(result, inline_query):
    user_id = inline_query.from_user.id
    prefix = navy.get_prefix(user_id)
    text_help = (
        await dB.get_var(user_id, "text_help") or f"{bot.me.mention}</b>"
    )
    full = f"<a href=tg://user?id={inline_query.from_user.id}>{inline_query.from_user.first_name} {inline_query.from_user.last_name or ''}</a>"
    msg = """
❏ <b>ᴍᴇɴᴜ ɪɴʟɪɴᴇ</b>
├ <b>ᴘʀᴇғɪx ➟</b> <code>{}</code>
├ <b>ᴍᴏᴅᴜʟᴇs ➟</b> <code>{}</code>
├ <b>ᴏᴡɴᴇʀ ➟</b> {}
╰ <b>ᴜʙᴏᴛ ➟</b> {}""".format(
        " ".join(prefix),
        len(HELPABLE),
        full,
        text_help,
    )
    result.append(
        InlineQueryResultArticle(
            title="Help Menu!",
            description=" Command Help",
            thumb_url=URL_LOGO,
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return result


async def alive_inline(result, inline_query):
    self = inline_query.from_user.id
    pmper = None
    status = None
    start = datetime.now()
    ping = (datetime.now() - start).microseconds / 1000
    upnya = await get_time((time() - start_time))
    me = next((x for x in navy._ubot), None)
    try:
        peer = navy._get_my_peer[self]
        users = len(peer["pm"])
        group = len(peer["gc"])
    except Exception:
        users = random.randrange(await me.get_dialogs_count())
        group = random.randrange(await me.get_dialogs_count())
    await me.invoke(Ping(ping_id=0))
    seles = await dB.get_list_from_var(bot.me.id, "SELLER")
    if self in SUDO_OWNERS:
        status = "DEVELOPER"
    elif self in seles:
        status = "SELLER"
    else:
        status = "CUSTOMER"
    cekpr = await dB.get_var(self, "PMPERMIT")
    if cekpr:
        pmper = "enable"
    else:
        pmper = "disable"
    get_exp = await dB.get_expired_date(self)
    exp = get_exp.strftime("%d-%m-%Y")
    txt = f"""ㅤㅤㅤㅤ<b>꧁ {BOT_NAME} ꧂ㅤㅤㅤ</b>\n\n<b>酸 ── 𝗦𝗧𝗔𝗧𝗨𝗦 :</b> <code>{status}</code>\n<b>酸 ── 𝗗𝗖_𝗜𝗗 :</b> <code>{me.me.dc_id}</code>\n<b>酸 ── 𝗣𝗜𝗡𝗚_𝗗𝗖 :</b> <code>{str(ping).replace('.', ',')}ms</code>\n<b>酸 ── 𝗣𝗠_𝗣𝗘𝗥𝗠𝗜𝗧 :</b> <code>{pmper}</code>\n<b>酸 ── 𝗣𝗘𝗘𝗥_𝗨𝗦𝗘𝗥𝗦 :</b> <code>{users} 𝗨𝗦𝗘𝗥𝗦</code>\n<b>酸 ── 𝗣𝗘𝗘𝗥_𝗚𝗥𝗢𝗨𝗣 :</b> <code>{group} 𝗚𝗥𝗢𝗨𝗣𝗦</code>\n<b>酸 ── 𝗣𝗘𝗘𝗥_𝗨𝗕𝗢𝗧 :</b> <code>{len(navy._ubot)} 𝗨𝗕𝗢𝗧</code>\n<b>酸 ── 𝗨𝗣𝗧𝗜𝗠𝗘 :</b> <code>{upnya}</code>\n<b>酸 ── 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 :</b> <code>{exp}</code>
"""
    msge = f"{txt}"
    button = ikb([[("Close", "close alive")]])
    cekpic = "https://files.catbox.moe/rwz2pd.jpg"
    if not cekpic or cekpic == "none":
        # fallback ke InlineQueryResultArticle
        result.append(
            InlineQueryResultArticle(
                title=BOT_NAME,
                description="Get Alive Of Bot.", input_message_content=InputTextMessageContent(msge),
                thumb_url=URL_LOGO,
                reply_markup=button,
            )
        )
    else:
        media = (
            InlineQueryResultVideo
            if cekpic.endswith(".mp4")
            else InlineQueryResultPhoto
        )
        url_ling = (
            {"video_url": cekpic, "thumb_url": cekpic}
            if cekpic.endswith(".mp4")
            else {"photo_url": cekpic}
        )
        logger.info(f"send InlineMedia : {media} with URL {cekpic}")
        result.append(
            media(
                **url_ling,
                title=BOT_NAME,
                description="Get Alive Of Bot.",
                thumb_url=URL_LOGO,
                caption=msge,
                reply_markup=button,
            )
        )
    return result

async def get_inline_note(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    note = str(inline_query.query.split()[2])
    logger.info(f"Data notes: {note}")
    gw = inline_query.from_user.id
    _id = state.get(gw, "in_notes")
    message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
    noteval = await dB.get_var(gw, note, "notes")
    if not noteval:
        return
    btn_close = ikb([[("Close", f"close get_note {uniq} {note}")]])
    state.set("close_notes", "get_note", btn_close)
    try:
        tks = noteval["result"].get("text")
        type = noteval["type"]
        file_id = noteval["file_id"]
        note, button = ButtonUtils.parse_msg_buttons(tks)
        teks = await Tools.escape_filter(message, note, Tools.parse_words)
        button = await ButtonUtils.create_inline_keyboard(button, gw)
        for row in btn_close.inline_keyboard:
            button.inline_keyboard.append(row)
        if type != "text":
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": teks,
                "reply_markup": button,
                "parse_mode": enums.ParseMode.HTML,
            }

            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "document":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "sticker":
                kwargs["sticker_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Send Inline!",
                    reply_markup=button,
                    input_message_content=InputTextMessageContent(
                        teks,
                        parse_mode=enums.ParseMode.HTML,
                    ),
                )
            )
        return result
    except Exception:
        logger.error(f"Error notes: {traceback.format_exc()}")

async def inline_absen(result, inline_query, chat_id=None):
    try:
        user_id = inline_query.from_user.id
        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        hari = now.strftime("%A")
        tanggal = now.strftime("%d-%m-%Y")

        user = inline_query.from_user
        fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        mention = f'<a href="tg://user?id={user.id}">{fullname}</a>'

        teks = (
            f"<blockquote>"
            f"📋 <b><u>DAFTAR ABSENSI HARIAN<u></b>\n\n"
            f"Hari : {hari}\n"
            f"Tanggal : {tanggal}\n\n"
            f"Di Absensi oleh : {mention}"
            f"</blockquote>"
            f"<b>Belum Ada Yang Absen Hari Ini</b>"
        )

        content = InputTextMessageContent(teks, parse_mode=ParseMode.HTML)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Absen Sekarang", callback_data="absen_tap")],
            [InlineKeyboardButton("❌ Tutup", callback_data="absen_close")]
        ])

        result_article = InlineQueryResultArticle(
            title="📌 Kirim Daftar Absen",
            input_message_content=content,
            reply_markup=markup
        )

        if chat_id is not None:
            active_absen_inline_ids[chat_id] = result_article.id
            absen_owners[chat_id] = inline_query.from_user.id

        return [result_article]

    except Exception:
        logger.error(traceback.format_exc())
        return []

async def inline_spc(answers, inline_query):
    user_id = inline_query.from_user.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Ketuk untuk lihat spesifikasi", callback_data=f"spc_show:{user_id}")]
    ])

    answers.append(
        InlineQueryResultArticle(
            title="🖥️ Informasi Sistem",
            description="Klik untuk melihat detail spesifikasi",
            input_message_content=InputTextMessageContent(
                "Klik tombol di bawah untuk melihat spesifikasi."
            ),
            reply_markup=keyboard
        )
    )

    return answers

"""
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