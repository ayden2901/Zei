from gpytranslate import Translator

from Navy.database import dB
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ᴛʀᴀɴsʟᴀᴛᴇ"
__HELP__ = """<blockquote>Command Help **Translate**</blockquote>

<blockquote>**Translate the message**</blockquote>
    **Translate message to other language**
        `{0}tr` (text/reply text)

<blockquote>**Change language**</blockquote>
    **Set default language for translate**
        `{0}setlang` (lang code)

<blockquote>**View lang code country**</blockquote>
    **You can view list language code country**
        `{0}lang`

<b>   {1}</b>
"""


@CMD.UBOT("tr")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    trans = Translator()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses}**{proses_}**")
    bhs = await client.get_translate()
    if message.reply_to_message:

        txt = message.reply_to_message.text or message.reply_to_message.caption
        src = await trans.detect(txt)
    else:
        if len(message.command) < 2:
            return await message.reply(
                f"{em.gagal}**Please reply to message text or give text!**"
            )
        else:
            txt = message.text.split(None, 1)[1]
            src = await trans.detect(txt)
    trsl = await trans(txt, sourcelang=src, targetlang=bhs)
    reply = f"{em.sukses} Translated:\n\n{trsl.text}"
    rep = message.reply_to_message or message
    await pros.delete()
    return await client.send_message(message.chat.id, reply, reply_to_message_id=rep.id)


@CMD.UBOT("lang")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    try:
        bhs_list = "\n".join(
            f"- **{lang}**: `{code}`" for lang, code in Tools.kode_bahasa.items()
        )
        return await message.reply(f"{em.sukses}**Language codes:**\n\n{bhs_list}")

    except Exception as e:
        return await message.reply(f"{em.gagal}**Error: {str(e)}**")


@CMD.UBOT("setlang")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses}**Processing...**")
    if len(message.command) < 2:
        return await pros.edit(
            f"{em.gagal}**Please reply to message text or give text!**"
        )

    for lang, code in Tools.kode_bahasa.items():
        kd = message.text.split(None, 1)[1]
        if kd.lower() == code.lower():
            await dB.set_var(client.me.id, "_translate", kd.lower())
            return await pros.edit(
                f"{em.sukses}**Successfully changed translate language to: {lang}-{kd}**"
            )
