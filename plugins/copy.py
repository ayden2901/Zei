__MODULES__ = "ᴄᴏᴘʏ"
__HELP__ = """<blockquote>Command Help **Copy**</blockquote>

<blockquote>**Get messages from other chat**</blockquote>
    **You can steal or get the message from other chat to this chat**
        `{0}copy` (url)
        
<blockquote>**Get messages with count**</blockquote>
    **This command can steal or get message media only with message count**
        `{0}copyall` (url) (count)

<blockquote>**Note**: For command `copyall` only support media.</blockquote>

<b>   {1}</b>
"""

import asyncio
import os
import traceback

from pyrogram import enums
from pyrogram.errors import FloodWait, RPCError

from config import COPY_ID
from Navy import bot
from Navy.database import state
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools
from Navy.logger import logger


async def safe_download(client, msg):
    try:
        return await client.download_media(msg)
    except FloodWait as fw:
        await asyncio.sleep(fw.value)
        return await client.download_media(msg)


async def get_thumb(client, thumbs):
    if thumbs:
        try:
            return await client.download_media(thumbs[-1])
        except Exception:
            return None
    return None


def get_link(link):
    chatid, msgid = None, None
    if "https://t.me/" not in link:
        return None, None
    try:
        datas = link.split("/")
        if len(datas) == 4:
            chatid = datas[3]
            msgid = None
            return chatid, msgid
        if len(datas) >= 5:
            if "https://t.me/c/" in link:
                chatid = int("-100" + datas[-2])
                msgid = int(datas[-1].split("?")[0])
            else:
                chatid = datas[-2]
                msgid = int(datas[-1].split("?")[0])
    except (ValueError, IndexError) as e:
        return None, None
    return chatid, msgid


async def cleanup_media(media_path):
    try:
        if media_path and os.path.exists(media_path):
            os.remove(media_path)
    except Exception as e:
        logger.error(f"Error deleting media: {e}")


@CMD.UBOT("copyall")
async def _(client, message):
    args = message.command[1:]

    if len(args) < 2:
        return await message.reply(
            f"**Please give link**\nExample: `{message.text.split()[0]} https://t.me/nikolnewversion/1745 5`"
        )

    chat_id = message.chat.id
    message_link = args[0]
    total = int(args[1])

    chats, links = get_link(message_link)
    if chats is None or links is None:
        return await message.reply(
            f"**Invalid link**\nExample: `{message.text.split()[0]} https://t.me/nikolnewversion/1745 5`"
        )

    imsg = await message.reply("<b>Copying messages...</b>")

    try:
        async for msg in client.get_chat_history(chats, limit=1):
            lastnih = msg.id
            break
        else:
            return await message.reply("<b>No messages found in the chat!</b>")

        logger.info(f"Last message ID: {lastnih}")

        counter = 0
        successful_copies = 0
        skipped_messages = 0

        for message_id in range(links, min(total + links, lastnih + 1)):
            try:
                msg = await client.get_messages(chats, message_id)

                if not msg:
                    skipped_messages += 1
                    continue
                if msg.text:
                    continue
                if msg.media in [
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.PHOTO,
                ]:
                    try:
                        await msg.copy(chat_id)
                    except FloodWait as wet:
                        await asyncio.sleep(wet.value)
                        await msg.copy(chat_id)
                    except Exception:
                        cnt = await message.reply(
                            "<b>Cant copy message, try to downloading...</b>"
                        )
                        await Tools.download_media(msg, client, cnt, message)

                    successful_copies += 1
                    counter += 1

            except FloodWait as flood:
                logger.error(f"FloodWait: Waiting for {flood.value} seconds")
                await asyncio.sleep(flood.value)
            except RPCError as rpc_error:
                logger.error(f"RPC Error for message {message_id}: {rpc_error}")
                continue
            except Exception as er:
                logger.error(
                    f"Error copying message {message_id}: {traceback.format_exc()}"
                )
                continue

        await imsg.delete()
        return await message.reply(
            f"<b>Copying completed.\n"
            f"Total messages attempted: {total}\n"
            f"Successfully copied: {successful_copies}\n"
            f"Skipped messages: {skipped_messages}</b>"
        )

    except Exception as e:
        logger.error(f"Overall process error: {traceback.format_exc()}")
        return await message.reply(f"An unexpected error occurred: {str(e)}")


@CMD.UBOT("copyall2")
async def _(client, message):
    args = message.command[1:]

    if len(args) < 2:
        await message.reply(
            f"**Please give link**\nExample: `{message.text.split()[0]} https://t.me/nikolnewversion/1745 5`"
        )
        return

    chat_id = message.chat.id
    message_link = args[0]
    total = int(args[1])

    chats, links = get_link(message_link)
    if chats is None or links is None:
        await message.reply(
            f"**Invalid link**\nExample: `{message.text.split()[0]} https://t.me/nikolnewversion/1745 5`"
        )
        return

    imsg = await message.reply("<b>Copying messages...</b>")

    try:
        messages = []
        async for msg in client.get_chat_history(chats, limit=total):
            messages.append(msg)
            if len(messages) >= total:
                break

        messages = list(reversed(messages))

        for msg in messages:
            try:
                caption = msg.caption or msg.text or ""
                markup = msg.reply_markup

                media_types = {
                    "video": client.send_video,
                    "photo": client.send_photo,
                    "animation": client.send_animation,
                    "voice": client.send_voice,
                    "audio": client.send_audio,
                    "document": client.send_document,
                    "sticker": client.send_sticker,
                }

                for media_type, send_method in media_types.items():
                    media_attr = getattr(msg, media_type, None)
                    if media_attr:
                        try:
                            media = await safe_download(client, msg)
                            if media:
                                send_args = {
                                    "chat_id": chat_id,
                                    media_type: media,
                                    "caption": caption,
                                    "reply_markup": markup,
                                }

                                if media_type in ["video", "audio"]:
                                    send_args.update(
                                        {
                                            "duration": media_attr.duration,
                                            "width": getattr(media_attr, "width", None),
                                            "height": getattr(
                                                media_attr, "height", None
                                            ),
                                        }
                                    )

                                await send_method(
                                    **{
                                        k: v
                                        for k, v in send_args.items()
                                        if v is not None
                                    }
                                )
                                break
                            if media:
                                await cleanup_media(media)
                        except Exception as media_err:
                            logger.error(f"Error sending {media_type}: {media_err}")
                            return await message.reply(
                                f"An error occurred: {str(media_err)}"
                            )
                else:
                    await client.copy_message(
                        chat_id, msg.chat.id, msg.id, reply_markup=markup
                    )

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error copying message: {e}")
                return await message.reply(f"An error occurred: {str(e)}")

        await imsg.delete()
        return await message.reply("<b>Copying completed!</b>")

    except Exception as e:
        logger.error(f"Copyall error: {traceback.format_exc()}")
        return await message.reply(f"An error occurred: {str(e)}")


@CMD.UBOT("copy")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    if reply:
        chat_id = (
            message.chat.id if len(message.command) < 2 else message.text.split()[1]
        )
        if reply.reply_markup:
            try:
                state.set(client.me.id, "inline_copy", id(message))
                query = f"inline_copy {client.me.id}"
                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    chat_id,
                    bot.me.username,
                    query,
                )
                if inline:
                    return await proses.delete()
            except Exception as e:
                return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")
        else:
            await reply.copy(chat_id)
            return await proses.delete()
    else:
        if len(message.command) < 2:
            return await proses.edit(
                f"{em.gagal}<b>Please give link!!</\n\nExample: `{message.text.split()[0]} https://t.me/nikolnewversion/1745 </b>"
            )
        chat_id = message.command[2] if len(message.command) > 2 else message.chat.id
        link = message.command[1]
        if "?single" in link:
            link = link.replace("?single", "")
        if "?single" in link:
            link = link.replace("?single", "")

        if link.startswith(("https", "t.me")):
            if "?comment=" in link:
                link_parts = link.split("?comment=")
                msg_id = int(link_parts[0].split("/")[-1])
                target = int(link_parts[1].split("/")[-1])
                chid = str(link.split("/")[-2])
                chat = await client.get_discussion_message(chid, msg_id)
                try:
                    get_msg = await client.get_messages(chat.chat.id, target)
                    try:
                        await get_msg.copy(chat_id)
                        return await proses.delete()
                    except Exception:
                        return await Tools.download_media(
                            get_msg, client, proses, message
                        )
                except Exception as e:
                    return await proses.edit(str(e))
            msg_id = int(link.split("/")[-1])
            if "t.me/c/" in link:
                chat = int("-100" + str(link.split("/")[-2]))
                try:
                    get_msg = await client.get_messages(chat, msg_id)
                    try:
                        await get_msg.copy(chat_id)
                        return await proses.delete()
                    except Exception:
                        return await Tools.download_media(
                            get_msg, client, proses, message
                        )
                except Exception as e:
                    return await proses.edit(str(e))
            else:
                get_chat = str(link.split("/")[-2])
                try:
                    chat = await client.get_chat(get_chat)
                    get_msg = await client.get_messages(chat.id, msg_id)
                    await get_msg.copy(chat_id)
                    return await proses.delete()
                except Exception:
                    try:
                        query = f"copy_inline {id(message)}"
                        await ButtonUtils.send_inline_bot_result(
                            message, chat_id, bot.me.username, query
                        )
                        xx = state.get(client.me.id, query)
                        COPY_ID[client.me.id] = int(xx["_id"])
                        return await proses.delete()
                    except Exception as error:
                        return await proses.edit(f"{em.gagal}**ERROR:** {str(error)}")
        else:
            return await proses.edit(f"{em.gagal}<b>Please give link!!</b>")
