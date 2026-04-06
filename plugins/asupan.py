import asyncio
import random
from random import choice

from pyrogram import enums, types

from Navy.helpers import CMD, Emoji

__MODULES__ = "ᴀsᴜᴘᴀɴ"
__HELP__ = """<blockquote>Command Help **Asupan**</blockquote>
    
<blockquote>**Get videos**</blockquote>
    **Get random asupan video**
        `{0}asupan`
    
<b>   {1}</b>
"""


@CMD.UBOT("asupan")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    y = await message.reply(f"<b>{em.proses}{proses_[4]}...</b>")
    await asyncio.sleep(3)
    try:
        asupannya = []
        async for asupan in client.search_messages(
            "@AsupanNyaSaiki", filter=enums.MessagesFilter.VIDEO
        ):
            asupannya.append(asupan)
        video = random.choice(asupannya)
        await video.copy(
            message.chat.id,
            caption=f"{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b>",
            reply_to_message_id=message.id,
        )
        return await y.delete()
    except Exception:
        return await y.edit(f"{em.gagal}<b>Try a gain!</b>")
