from Navy import navy
from Navy.helpers import AFK_, CMD, Emoji, Tools, animate_proses
from pyrogram.enums import ParseMode

__MODULES__ = "ᴀғᴋ"
__HELP__ = """<blockquote expandable>Command Help **AFK**</blockquote>

<blockquote>**Enabe afk mode**</blockquote>
    **You can set status to AFK mode**
        `{0}afk` (reason)
    
<blockquote>**Disable afk mode**</blockquote>
    **After AFK mode on, you can set to UNAFK mode**
        `{0}unafk`

<b>   {1}</b>
"""



@CMD.NO_CMD("REP_BLOCK", navy)
async def _(client, message):
    em = Emoji(client)
    await em.get()
    return await message.reply_text(
        f"{em.block}**GAUSAH REPLY APALAGI TAG GUA, LU UDAH BLOCK GUA YA ANAK KONTOL!!!**"
    )


@CMD.UBOT("afk")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    rep = message.reply_to_message
    if not rep:
        return await message.reply(f"{emo.gagal}<b>REPLY PESAN NYA BODOH!!!</b>")
    return await AFK_.set_afk(client, message, emo)


@CMD.NO_CMD("AFK", navy)
@CMD.capture_err
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    return await AFK_.get_afk(client, message, emo)


@CMD.UBOT("unafk")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    return await AFK_.unset_afk(client, message, emo)
