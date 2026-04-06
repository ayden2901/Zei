from Navy import bot
from Navy.database import state
from Navy.helpers import CMD, ButtonUtils, Emoji

__MODULES__ = "ғᴏɴᴛ"
__HELP__ = """<blockquote>Command Help **Fonts**</blockquote>

<blockquote>**Generate costum font**</blockquote>
    **You can make text to awesome from this command**
        `{0}font` (text/reply text)

<b>   {1}</b>
"""


@CMD.UBOT("font")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"{emo.gagal}<b>Please give text or reply to text:\n\nExample: <code>{x}font</code> [text or reply to text]</b>"
        )
    proses_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_[4]}</b>")
    query = f"inline_font"
    state.set(client.me.id, "FONT", text)
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            await pros.delete()
            return await message.delete()
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{str(error)}</code>")
