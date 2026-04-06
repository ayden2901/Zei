import asyncio
from pyrogram.enums import ParseMode
from Navy import bot, navy
from .emoji_logs import Emoji
from Navy.database import dB
from .tools import Tools


class AFK_:
    @staticmethod
    async def set_afk(client, message, emo):
        try:
            rep = message.reply_to_message
            if not rep:
                return await message.reply(f"{emo.gagal} Reply pesan untuk set AFK.")

            text = rep.text or rep.caption or ""
            entities = rep.entities or rep.caption_entities
            if rep.media:
                media = Tools.get_file_id(rep)
                extract = Tools.dump_entity(text, entities)
                value = {
                    "type": media["message_type"],
                    "file_id": media["file_id"],
                    "result": extract,
                }
            else:
                extract = Tools.dump_entity(text, entities)
                value = {"type": "text", "file_id": "", "result": extract}

            if value:
                await dB.set_var(client.me.id, "AFK", value)

            afk_set_text = f"<blockquote>{emo.sukses}**INI PESAN AFK LU ➟ [PESAN AFK]({rep.link})</blockquote>"
            try:
                return await message.reply(afk_set_text, disable_web_page_preview=True)
            except (FloodWait, ChatWriteForbidden):
                return
        except Exception as er:
            try:
                return await message.reply(f"{emo.gagal}**ERROR**: `{str(er)}`", disable_web_page_preview=True)
            except:
                return

    @staticmethod
    async def get_afk(client, message, emo):
        try:
            data = await dB.get_var(client.me.id, "AFK")
            if not data:
                return

            type_ = data["type"]
            file_id = data["file_id"]

            if type_ == "text":
                entities = [
                    Tools.convert_entity(asu)
                    for asu in data["result"].get("entities", [])
                ]
                try:
                    return await message.reply(
                        data["result"].get("text"),
                        entities=entities,
                        reply_to_message_id=message.id,
                        disable_web_page_preview=True,
                    )
                except (FloodWait, ChatWriteForbidden):
                    return
            elif type_ == "sticker":
                try:
                    return await message.reply_sticker(
                        file_id,
                        reply_to_message_id=message.id,
                    )
                except:
                    return
            elif type_ == "video_note":
                try:
                    return await message.reply_video_note(
                        file_id,
                        reply_to_message_id=message.id,
                    )
                except:
                    return
            else:
                kwargs = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                }

                if type_ in kwargs:
                    entities = [
                        Tools.convert_entity(asu)
                        for asu in data["result"].get("entities", [])
                    ]
                    try:
                        return await kwargs[type_](
                            file_id,
                            caption=data["result"].get("text"),
                            caption_entities=entities,
                            reply_to_message_id=message.id,
                            disable_web_page_preview=True if type_ == "text" else False,
                        )
                    except:
                        return
        except Exception as er:
            try:
                return await message.reply(f"{emo.gagal}**ERROR**: `{str(er)}`", disable_web_page_preview=True)
            except:
                return

    @staticmethod
    async def unset_afk(client, message, emo):
        vars_ = await dB.get_var(client.me.id, "AFK")
        if vars_:
            await dB.remove_var(client.me.id, "AFK")
            afk_text = f"<blockquote><b>{emo.sukses}I'm Comeback!!</b></blockquote>"
            try:
                ae = await message.reply(afk_text, disable_web_page_preview=True)
                await asyncio.sleep(3)
                try:
                    await ae.delete()
                except:
                    pass
                return
            except:
                return