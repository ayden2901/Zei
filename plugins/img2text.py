__MODULES__ = "ɪᴍɢ2ᴛᴇxᴛ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ɪᴍɢ𝟸ᴛᴇxᴛ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ɪᴍɢ𝟸ᴛᴇxᴛ</b>
    ➢ `{0}img2text` [ʀᴇᴘʟʏ ɪᴍᴀɢᴇ]</blockquote>

<b>   {1}</b>
"""


from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools


@CMD.UBOT("img2text")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    rep = message.reply_to_message or message
    if len(message.command) < 2 and not rep:
        return await prs.edit(f"{em.gagal}**Please reply to image or give link.!!**")
    if rep and rep.media:
        arg = await Tools.upload_media(message)
    else:
        arg = client.get_text(message)
        if not arg.startswith("https://"):
            return await prs.edit(f"{em.gagal}**Please give valid link**")
    url = f"https://api.botcahx.eu.org/api/tools/img2prompt?url={arg}&apikey={API_BOTCHAX}"
    respon = await Tools.fetch.get(url)
    await prs.edit(f"{em.proses}**Scanning of image...**")
    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.delete()
            return await message.reply(
                f"{em.sukses}**Media:** <a href='{rep.link}'>Here</a>\n**Result:** `{data}`",
                disable_web_page_preview=True,
            )
        except Exception as er:
            await prs.delete()
            return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
    else:
        return await prs.edit(f"**{em.gagal}Please try again: {respon.status_code}!**")
