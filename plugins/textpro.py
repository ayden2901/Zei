from Navy import bot
from Navy.database import state
from Navy.helpers import CMD, ButtonUtils, Emoji

__MODULES__ = "ᴛᴇxᴛᴘʀᴏ"
__HELP__ = """<blockquote>Command Help **Text Pro**</blockquote>

<blockquote>**Make custom text**</blockquote>
    **Generate text image from command**
        `{0}textpro` (text/reply text)

<b>   {1}</b>
"""


@CMD.UBOT("textpro")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"{emo.gagal}<b>Please give text or reply to text:\n\nExample: <code>{message.text.split()[0]}</code> [text or reply to text]</b>"
        )
    proses_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_[4]}</b>")
    query = f"inline_textpro"
    state.set(client.me.id, "TEXT_PRO", text)
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            await pros.delete()
            return await message.delete()
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{str(error)}</code>")
