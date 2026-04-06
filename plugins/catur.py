import random

from Navy.helpers import CMD, Emoji

__MODULES__ = "ᴄᴀᴛᴜʀ"
__HELP__ = """<blockquote>Command Help **Catur**</blockquote>

<blockquote>**Send inline game**</blockquote>
    **You can send inline catur game to chat**
        `{0}catur`
    
<b>   {1}</b>
"""


@CMD.UBOT("catur")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    try:
        x = await client.get_inline_bot_results("GameFactoryBot")
        msg = message.reply_to_message or message
        await client.send_inline_bot_result(
            message.chat.id,
            x.query_id,
            x.results[0].id,
            reply_to_message_id=msg.id,
        )
    except Exception as error:
        return await message.reply(f"{em.gagal}Error: {str(error)}")

