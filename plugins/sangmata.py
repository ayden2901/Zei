__MODULES__ = "sᴀɴɢᴍᴀᴛᴀ"
__HELP__ = """<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **sᴀɴɢᴍᴀᴛᴀ**</u>

<blockquote><b>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ **sᴀɴɢᴍᴀᴛᴀ**</b>
     ➢ `{0}sg` [ᴜsᴇʀɪᴅ/ᴜsᴇʀɴᴀᴍᴇ]</blockquote>

<b>   {1}</b>
"""

import asyncio

from pyrogram import raw

from Navy.helpers import CMD, Emoji


@CMD.UBOT("sg")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    try:
        if len(message.command) < 2 and not reply:
            return await message.reply(
                f"**{em.gagal}Please reply to a message or provide a username/id**"
            )
        if reply:
            user = reply.from_user.id
        else:
            target = message.text.split()[1]
            user = (await client.get_users(target)).id
        proses_ = await em.get_costum_text()
        proses = await message.reply(f"{em.proses}**{proses_[4]}**")
        sg = "@SangMata_BOT"
        try:
            a = await client.send_message(sg, user)
            await asyncio.sleep(1)
            await a.delete()
        except Exception as e:
            return await proses.edit(f"**{em.gagal}{str(e)}**")
        async for respon in client.search_messages(a.chat.id):
            if respon.text == None:
                continue
            if not respon:
                return await message.reply(f"**{em.gagal}No response from Sangmata**")
            elif respon:
                await message.reply(f"{em.sukses} {respon.text}")
                break
        await proses.delete()
        try:
            user_info = await client.resolve_peer(sg)
            return await client.invoke(
                raw.functions.messages.DeleteHistory(
                    peer=user_info, max_id=0, revoke=True
                )
            )
        except Exception:
            pass
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")
