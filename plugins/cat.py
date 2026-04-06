__MODULES__ = "ᴄᴀᴛ"
__HELP__ = """<blockquote>Command Help **Cat**</blockquote>

<blockquote>**Get random cats image**</blockquote>
    **You can get random image cute cats**
        `{0}cats`
    
<b>   {1}</b>
"""


from Navy import bot
from Navy.helpers import CMD, ButtonUtils


@CMD.UBOT("cats")
async def _(_, message):
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, "inline_cat"
        )
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"**ERROR**: {str(er)}")
