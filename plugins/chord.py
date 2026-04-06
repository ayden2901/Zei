from pyrogram.errors import MessageTooLong

from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ᴄʜᴏʀᴅ"
__HELP__ = """<blockquote>Command Help **Chord**</blockquote>

<blockquote>**Find chord song**</blockquote>
    **You can get chord from the songs**
        `{0}chord` (title)

<b>   {1}</b>
"""


@CMD.UBOT("chord")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    rep = message.reply_to_message
    if len(message.command) < 2 and not rep:
        return await prs.edit(f"{em.gagal}**Please give song or lyrics.!!**")
    arg = client.get_text(message)
    url = f"https://api.botcahx.eu.org/api/search/chord?song={arg}&apikey={API_BOTCHAX}"
    msg = ""
    respon = await Tools.fetch.get(url)
    if respon.status_code == 200:
        data = respon.json()
        fileds = {
            "Song title": data["result"].get("title", "-"),
            "Song chord": data["result"].get("chord", "-"),
        }
        msg = "\n".join([f"{key}: {value}" for key, value in fileds.items()])
        try:
            await prs.delete()
            return await message.reply(msg)
        except MessageTooLong:
            await prs.delete()
            konten = str(msg)
            link = await Tools.paste(konten)
            return await message.reply(
                f"{em.sukses}**[Click here]({link}) to view song of the chord.**",
                disable_web_page_preview=True,
            )
    else:
        return await prs.edit(f"**{em.gagal}Please try again: {respon.status_code}!**")
