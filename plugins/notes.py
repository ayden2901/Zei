import asyncio
import traceback
from uuid import uuid4
from pyrogram.enums import ParseMode
from pyrogram import enums
from Navy import bot
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, Emoji, Message, Tools, animate_proses
from Navy.logger import logger

__MODULES__ = "ɴᴏᴛᴇs"
__HELP__ = """<blockquote>Command Help **Notes**</blockquote>

<blockquote>**Save the notes** </blockquote>
    **You can save message with this command**
        `{0}save` (note name) (reply message)

<blockquote>**Get the notes** </blockquote>
    **Get saved message you are**
        `{0}get` (note name)

<blockquote>**List the notes** </blockquote>
    **View all saved note**
        `{0}notes`

<blockquote>**Clear the notes**</blockquote> 
    **You can clear or delete the one note or many note**
        `{0}clear` (note name) or (name1, name2, name2)

<blockquote>**Clear all notes**</blockquote>
    **For this command you can delete all saved note**
        `{0}clear all`
    
<b>   {1}</b>
"""


@CMD.UBOT("addcb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    args = message.text.split()
    if len(args) < 2 or not message.reply_to_message:
        return await xx.edit(f"{em.gagal}**Reply ke pesan dan beri nama callback!**")
    
    nama = args[1]
    rep = message.reply_to_message
    text = rep.text or rep.caption or ""
    entities = rep.entities or rep.caption_entities
    extract = Tools.dump_entity(text, entities)
    value = {"text": text, "entities": extract["entities"]}

    await dB.set_var(client.me.id, nama, value, "callback")
    return await xx.edit(f"{em.sukses}**Callback `{nama}` berhasil disimpan!**")

@CMD.UBOT("listcb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    data = await dB.all_var(client.me.id, "callback")
    if not data:
        return await xx.edit(f"{em.gagal}**Tidak ada callback yang disimpan.**")
    
    teks = f"{em.msg}**Daftar Callback:**\n\n"
    for key in data:
        teks += f"• `{key}`\n"
    return await xx.edit(teks)

@CMD.UBOT("clearcb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    args = message.text.split()

    if len(args) < 2:
        return await xx.edit(f"{em.gagal}**Tentukan nama callback atau gunakan `clearcb all`!**")
    
    if args[1] == "all":
        for nama in await dB.all_var(client.me.id, "callback"):
            await dB.remove_var(client.me.id, nama, "callback")
        return await xx.edit(f"{em.sukses}**Semua callback berhasil dihapus!**")
    
    nama = args[1]
    data = await dB.get_var(client.me.id, nama, "callback")
    if not data:
        return await xx.edit(f"{em.gagal}**Callback `{nama}` tidak ditemukan!**")
    
    await dB.remove_var(client.me.id, nama, "callback")
    return await xx.edit(f"{em.sukses}**Callback `{nama}` berhasil dihapus!**")

@CMD.UBOT("save")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = (
        await em.get_costum_text()
    )

    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    rep = message.reply_to_message
    if len(message.command) < 2 or not rep:
        return await xx.edit(
            f"{em.gagal}**Please reply message and give note name**"
        )

    nama = message.text.split()[1]
    getnotes = await dB.get_var(client.me.id, nama, "notes")

    if getnotes:
        return await xx.edit(f"{em.gagal}**Note {nama} already exist!**")

    value = None
    text = rep.text or rep.caption
    entities = rep.entities or rep.caption_entities

    if rep.media and rep.media != enums.MessageMediaType.WEB_PAGE_PREVIEW:
        copy = await rep.copy(bot.me.username)

        sent = await client.send_message(
            bot.me.username,
            f"/id {nama}",
            reply_to_message_id=copy.id,
        )

        await asyncio.sleep(1)
        await sent.delete()
        await copy.delete()

        extract = Tools.dump_entity(text, entities)
        type = state.get(client.me.id, nama)

        value = {
            "type": type["type"],
            "file_id": type["file_id"],
            "result": extract,
        }

    elif text:
        extract = Tools.dump_entity(text, entities)
        value = {
            "type": "text",
            "file_id": "",
            "result": extract,
        }

    if value:
        await dB.set_var(client.me.id, nama, value, "notes")
        return await xx.edit(f"{em.sukses}**Saved {nama} note!!**")

    return await xx.edit(
        f"{em.gagal}**Please reply message and give note name**"
    )


@CMD.UBOT("get")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = (
        await em.get_costum_text()
    )

    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    try:
        parts = message.text.split()

        if len(parts) == 2:
            note = parts[1]
            data = await dB.get_var(client.me.id, note, "notes")

            if not data:
                return await xx.edit(
                    f"{em.gagal}**Note {note} not found!**"
                )

            return await getnotes_(client, message, xx, note, data)

        elif len(parts) == 3 and parts[2] in ["noformat", "raw"]:
            note = parts[1]
            data = await dB.get_var(client.me.id, note, "notes")

            if not data:
                return await xx.edit(
                    f"{em.gagal}**Note {note} not found!**"
                )

            return await get_raw_note(client, message, xx, note, data)

        return await xx.edit(f"{em.gagal}**Please give note name!**")

    except Exception as e:
        return await xx.edit(f"{em.gagal}**ERROR**: {str(e)}")


async def getnotes_(client, message, xx, note, data):
    em = Emoji(client)
    await em.get()

    thetext = data["result"].get("text")
    uniq = str(uuid4())

    if thetext is not None:
        teks_unformat, button = ButtonUtils.parse_msg_buttons(thetext)

        if button:
            state.set(client.me.id, "in_notes", id(message))

            try:
                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    message.chat.id,
                    bot.me.username,
                    f"get_note {uniq.split('-')[0]} {note}",
                    reply_to_message_id=Message.ReplyCheck(message),
                )

                if inline:
                    return await xx.delete()

            except Exception as e:
                return await xx.edit(f"{em.gagal}**ERROR:** {str(e)}")

        else:
            type = data["type"]
            file_id = data["file_id"]

            teks_formatted = await Tools.escape_filter(
                message,
                teks_unformat,
                Tools.parse_words,
            )

            if type == "text":
                entities = [
                    Tools.convert_entity(ent)
                    for ent in data["result"].get("entities", [])
                ]

                await message.reply(
                    teks_formatted,
                    entities=entities,
                    reply_to_message_id=Message.ReplyCheck(message),
                )

                return await xx.delete()

            else:
                pre_senders = {
                    "photo": bot.send_photo,
                    "voice": bot.send_voice,
                    "audio": bot.send_audio,
                    "video": bot.send_video,
                    "animation": bot.send_animation,
                    "document": bot.send_document,
                    "sticker": bot.send_sticker,
                    "video_note": bot.send_video_note,
                }

                reply_senders = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                    "sticker": message.reply_sticker,
                    "video_note": message.reply_video_note,
                }

                file_attrs = {
                    "photo": "photo",
                    "voice": "voice",
                    "audio": "audio",
                    "video": "video",
                    "animation": "animation",
                    "document": "document",
                    "sticker": "sticker",
                    "video_note": "video_note",
                }

                try:
                    didel = await pre_senders[type](client.me.id, file_id)

                    async for media in client.search_messages(
                        bot.username,
                        limit=1,
                    ):
                        media_obj = getattr(media, file_attrs[type], None)
                        new_fileid = (
                            getattr(media_obj, "file_id", None)
                            if media_obj
                            else None
                        )
                        break
                    else:
                        new_fileid = None

                    if not new_fileid:
                        return await message.reply(
                            f"{em.gagal}**Error!! data not found.**"
                        )

                    await bot.delete_messages(bot.username, didel.id)

                    kwargs = {
                        "reply_to_message_id": Message.ReplyCheck(message)
                    }

                    if type not in ["sticker", "video_note"]:
                        kwargs["caption"] = teks_formatted
                        kwargs["caption_entities"] = [
                            Tools.convert_entity(ent)
                            for ent in data["result"].get("entities", [])
                        ]

                    await reply_senders[type](new_fileid, **kwargs)

                except Exception as e:
                    await message.reply(
                        f"{em.gagal}**Send failed:** `{e}`"
                    )

    else:
        type = data["type"]
        file_id = data["file_id"]

        pre_senders = {
            "photo": bot.send_photo,
            "voice": bot.send_voice,
            "audio": bot.send_audio,
            "video": bot.send_video,
            "animation": bot.send_animation,
            "document": bot.send_document,
            "sticker": bot.send_sticker,
            "video_note": bot.send_video_note,
        }

        reply_senders = {
            "photo": message.reply_photo,
            "voice": message.reply_voice,
            "audio": message.reply_audio,
            "video": message.reply_video,
            "animation": message.reply_animation,
            "document": message.reply_document,
            "sticker": message.reply_sticker,
            "video_note": message.reply_video_note,
        }

        file_attrs = {
            "photo": "photo",
            "voice": "voice",
            "audio": "audio",
            "video": "video",
            "animation": "animation",
            "document": "document",
            "sticker": "sticker",
            "video_note": "video_note",
        }

        try:
            didel = await pre_senders[type](client.me.id, file_id)

            async for media in client.search_messages(
                bot.username,
                limit=1,
            ):
                media_obj = getattr(media, file_attrs[type], None)
                new_fileid = (
                    getattr(media_obj, "file_id", None)
                    if media_obj
                    else None
                )
                break
            else:
                new_fileid = None

            if not new_fileid:
                return await message.reply(
                    f"{em.gagal}**Error!! data not found.**"
                )

            await bot.delete_messages(bot.username, didel.id)

            kwargs = {
                "reply_to_message_id": Message.ReplyCheck(message)
            }

            await reply_senders[type](new_fileid, **kwargs)

        except Exception as e:
            await message.reply(
                f"{em.gagal}**Send failed:** `{e}`"
            )

        return await xx.delete()

async def get_raw_note(client, message, xx, note, data):
    em = Emoji(client)
    await em.get()

    thetext = data["result"].get("text")
    _, button = ButtonUtils.parse_msg_buttons(thetext)

    try:
        if button:
            type = data["type"]
            file_id = data["file_id"]

            if type == "text":
                await message.reply(
                    data["result"].get("text"),
                    parse_mode=enums.ParseMode.DISABLED,
                    reply_to_message_id=Message.ReplyCheck(message),
                )

            else:
                send_map = {
                    "photo": bot.send_photo,
                    "voice": bot.send_voice,
                    "audio": bot.send_audio,
                    "video": bot.send_video,
                    "animation": bot.send_animation,
                    "document": bot.send_document,
                }

                if type in send_map:
                    disend = await send_map[type](
                        client.me.id,
                        file_id,
                        caption=data["result"].get("text"),
                        parse_mode=enums.ParseMode.DISABLED,
                    )

                    async for copy_msg in client.search_messages(
                        bot.id,
                        limit=1,
                    ):
                        await copy_msg.copy(message.chat.id)
                        break

                    await disend.delete()

        else:
            type = data["type"]
            file_id = data["file_id"]

            if type == "text":
                await message.reply(
                    data["result"].get("text"),
                    parse_mode=enums.ParseMode.DISABLED,
                    reply_to_message_id=Message.ReplyCheck(message),
                )

            else:
                pre_senders = {
                    "photo": bot.send_photo,
                    "voice": bot.send_voice,
                    "audio": bot.send_audio,
                    "video": bot.send_video,
                    "animation": bot.send_animation,
                    "document": bot.send_document,
                    "sticker": bot.send_sticker,
                    "video_note": bot.send_video_note,
                }

                reply_senders = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                    "sticker": message.reply_sticker,
                    "video_note": message.reply_video_note,
                }

                file_attrs = {
                    "photo": "photo",
                    "voice": "voice",
                    "audio": "audio",
                    "video": "video",
                    "animation": "animation",
                    "document": "document",
                    "sticker": "sticker",
                    "video_note": "video_note",
                }

                try:
                    didel = await pre_senders[type](
                        client.me.id,
                        file_id,
                    )

                    async for media in client.search_messages(
                        bot.username,
                        limit=1,
                    ):
                        media_obj = getattr(
                            media,
                            file_attrs[type],
                            None,
                        )
                        new_fileid = (
                            getattr(media_obj, "file_id", None)
                            if media_obj
                            else None
                        )
                        break
                    else:
                        new_fileid = None

                    if not new_fileid:
                        return await message.reply(
                            f"{em.gagal}**Error!! data not found.**"
                        )

                    await bot.delete_messages(bot.username, didel.id)

                    kwargs = {
                        "reply_to_message_id": Message.ReplyCheck(message)
                    }

                    if type not in ["sticker", "video_note"]:
                        kwargs["caption"] = thetext
                        kwargs["parse_mode"] = enums.ParseMode.DISABLED
                        kwargs["caption_entities"] = [
                            Tools.convert_entity(ent)
                            for ent in data["result"].get("entities", [])
                        ]

                    await reply_senders[type](new_fileid, **kwargs)

                except Exception as e:
                    await message.reply(
                        f"{em.gagal}**Send failed:** `{e}`"
                    )

    except Exception as er:
        logger.info(f"ERROR: {traceback.format_exc()}")
        await message.reply(
            f"{em.gagal}**ERROR**: {str(er)}"
        )

    return await xx.delete()


@CMD.UBOT("notes")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = (
        await em.get_costum_text()
    )

    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    getnotes = await dB.all_var(client.me.id, "notes")

    if not getnotes:
        return await xx.edit(
            f"{em.gagal}**You dont have any notes!**"
        )

    rply = f"{em.msg}**List of Notes:**\n\n"

    for x, data in getnotes.items():
        type = await dB.get_var(client.me.id, x, "notes")
        rply += (
            f"**• Name: `{x}` | Type: `{type['type']}`**\n"
        )

    return await xx.edit(rply)


@CMD.UBOT("clear")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    args = client.get_arg(message).split(",")

    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = (
        await em.get_costum_text()
    )

    xx = await animate_proses(message, em.proses)
    if not xx:
        return

    if len(args) == 0 or (
        len(args) == 1 and args[0].strip() == ""
    ):
        return await xx.edit(
            f"{em.gagal}**Which note do you want to delete?**"
        )

    if message.command[1] == "all":
        for nama in await dB.all_var(client.me.id, "notes"):
            await dB.remove_var(
                client.me.id,
                nama,
                "notes",
            )

        return await xx.edit(
            f"{em.sukses}**Succesfully deleted all notes!**"
        )

    gagal_list = []
    sukses_list = []

    for arg in args:
        arg = arg.strip()

        if not arg:
            continue

        data = await dB.get_var(
            client.me.id,
            arg,
            "notes",
        )

        if not data:
            gagal_list.append(arg)
        else:
            await dB.remove_var(
                client.me.id,
                arg,
                "notes",
            )
            sukses_list.append(arg)

    if sukses_list:
        return await xx.edit(
            f"{em.sukses}**Note `{', '.join(sukses_list)}` successfully deleted.**"
        )

    if gagal_list:
        return await xx.edit(
            f"{em.gagal}**Note `{', '.join(gagal_list)}` not found!**"
        )