import os
import random

from Navy import bot
from Navy.helpers import CMD, Emoji, Message, Quotly

__MODULES__ = "ᴄᴀʀʙᴏɴ"
__HELP__ = """<blockquote>Command Help **Carbon**</blockquote>

<blockquote>**Make carbonara**</blockquote>
    **You can generate carbonara from text**
        `{0}carbon` (reply text)
    
<b>   {1}</b>
"""


@CMD.UBOT("carbon|carbonara")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if not message.reply_to_message:
        await message.reply(f"{em.gagal}**Please reply to text or document!**")
        return
    proses_ = await em.get_costum_text()
    content, content_type = await Quotly.get_message_content(message.reply_to_message)
    if not content:
        await message.reply(f"{em.gagal}**Unable to extract content from message!**")
        return

    process_msg = await message.reply(f"{em.proses}**{proses_[4]}**")

    try:
        args = message.command[1:] if len(message.command) > 1 else []

        bg_color = args[0] if len(args) >= 1 else random.choice(Quotly.loanjing)
        theme = args[1] if len(args) >= 2 else random.choice(Quotly.loanjing)
        language = args[2] if len(args) >= 3 else "python"

        carbon_image = await Quotly.make_carbonara(content, bg_color, language, theme)

        with open("carbon.png", "wb") as f:
            f.write(carbon_image.getvalue())
        try:

            await message.reply_photo(
                "carbon.png",
                caption=f"{em.sukses}**Generate by {bot.me.mention}**",
                reply_to_message_id=Message.ReplyCheck(message),
            )
        except Exception:
            await message.reply(f"{em.gagal}**Text too long!!**")

    except Exception as e:
        await message.reply(f"{em.gagal}**ERROR**: {str(e)}")

    finally:
        await process_msg.delete()
        if os.path.exists("carbon.png"):
            os.remove("carbon.png")
