__MODULES__ = "ʙᴏʟᴀ"
__HELP__ = """<blockquote>Command Help **Bola**</blockquote>

<blockquote>**Get today's football matches**</blockquote>
    **Get news schedule football today's**
        `{0}bola`

<b>   {1}</b>
"""

from Navy import bot
from Navy.helpers import CMD, ButtonUtils


@CMD.UBOT("bola")
async def _(_, message):
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, "inline_bola"
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")
