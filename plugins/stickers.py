import asyncio

from Navy import bot
from Navy.helpers import CMD, Emoji

__MODULES__ = "sᴛɪᴄᴋᴇʀ"
__HELP__ = """<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **sᴛɪᴄᴋᴇʀ**</u>

<blockquote><b>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ sᴛɪᴄᴋᴇʀ</b>
     ➢ `{0}kang` [ʀᴇᴘʟʏ sᴛɪᴄᴋᴇʀ]
     ➢ `{0}unkang` [ʀᴇᴘʟʏ sᴛɪᴄᴋᴇʀ]
<b>❖ ᴍᴇɴᴄᴀʀɪ ɪɴғᴏ sᴛɪᴄᴋᴇʀ</b>
     ➢ `{0}gstik` [ʀᴇᴘʟʏ sᴛɪᴄᴋᴇʀ]</blockquote>
    
<b>   {1}</b>
"""


async def download_and_reply(client, message, stick, file_extension):
    em = Emoji(client)
    await em.get()
    pat = await client.download_media(
        stick, file_name=f"{stick.set_name}.{file_extension}"
    )
    await message.reply_to_message.reply_document(
        document=pat,
        caption=f"📂 **File Name:** `{stick.set_name}.{file_extension}`\n📦 **File Size:** `{stick.file_size}`\n📆 **File Date:** `{stick.date}`\n📤 **File ID:** `{stick.file_id}`",
    )


@CMD.UBOT("gstik|getstiker|getsticker")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    if reply and reply.sticker:
        stick = reply.sticker
        if stick.is_video:
            return await download_and_reply(client, message, stick, "mp4")
        elif stick.is_animated:
            return await message.reply(
                f"{em.gagal} Animated stickers are not supported."
            )
        else:
            return await download_and_reply(client, message, stick, "png")
    else:
        return await message.reply(
            f"{em.gagal} Reply to a sticker to get its information."
        )


@CMD.UBOT("unkang")
async def _(self, message):
    em = Emoji(self)
    await em.get()
    reply = message.reply_to_message
    await self.unblock_user(bot.me.username)
    if not reply or not reply.sticker:
        return await message.reply(f"{em.gagal} Reply to a sticker to remove")

    pros = await message.reply(f"{em.proses} Removing sticker from your")
    ai = await self.forward_messages(
        bot.me.username, message.chat.id, message_ids=reply.id
    )
    await self.send_message(bot.me.username, "/unkang", reply_to_message_id=ai.id)
    await asyncio.sleep(0.5)

    if await resleting(self, message) == "Stiker berhasil dihapus dari paket Anda.":
        return await pros.edit(f"{em.sukses} Sticker removed from your pack.")
    else:
        return await pros.edit(f"{em.gagal} Failed to remove sticker from your pack.")


@CMD.UBOT("kang")
async def _(self, message):
    em = Emoji(self)
    await em.get()
    reply = message.reply_to_message
    cekemo = self.get_arg(message)
    await self.unblock_user(bot.me.username)
    if not reply:
        return await message.reply(f"{em.gagal} Reply to a sticker to add")

    pros = await message.reply(f"{em.proses} Adding sticker to your")
    await self.send_message(bot.me.username, "/kang")
    try:
        ai = await self.forward_messages(
            bot.me.username, message.chat.id, message_ids=reply.id
        )
    except Exception:
        bh = await self.get_messages(message.chat.id, reply.id)
        ai = await bh.copy(bot.me.username)
    if len(message.command) == 2:
        await self.send_message(
            bot.me.username, f"/kang {cekemo}", reply_to_message_id=ai.id
        )
    else:
        await self.send_message(bot.me.username, "/kang", reply_to_message_id=ai.id)

    await asyncio.sleep(5)
    async for tai in self.search_messages(
        bot.me.username, query="Sticker Anda Berhasil Dibuat!", limit=1
    ):
        await asyncio.sleep(5)
        await tai.copy(message.chat.id)

    await ai.delete()
    await pros.delete()


async def resleting(self, message):
    return [x async for x in self.get_chat_history(bot.me.username, limit=1)][0].text
