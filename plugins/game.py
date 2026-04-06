import random

from Navy.helpers import CMD, Emoji

__MODULES__ = "ɢᴀᴍᴇ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ɢᴀᴍᴇ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ɢᴀᴍᴇ</b>
    ➢ `{0}game`</blockquote>
    
<b>   {1}</b>
"""

@CMD.UBOT("game")
async def _(client, message):
    try:
        x = await client.get_inline_bot_results("gamee")
        msg = message.reply_to_message or message
        random_index = random.randint(0, len(x.results) - 1)
        await client.send_inline_bot_result(
            message.chat.id,
            x.query_id,
            x.results[random_index].id,
            reply_to_message_id=msg.id,
        )
    except Exception as error:
        await message.reply(error)
