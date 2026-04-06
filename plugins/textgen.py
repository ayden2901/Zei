__MODULES__ = "ᴛᴇxᴛɢᴇɴ"
__HELP__ = """<blockquote>Command Help **Text Generator**</blockquote>

<blockquote>**Generate prompt for AI**</blockquote>
    **Get help prompt command for generate image ai for maximal result**
        `{0}textgen`

<b>   {1}</b>
"""


from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools


@CMD.UBOT("textgen")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    prompt = client.get_text(message)

    if not prompt:
        return await prs.edit(
            f"{em.gagal}<b>Give the query you want to generate prompt!\n\nExample: \n<code>{message.text.split()[0]} cat on the beach</code></b>"
        )
    url = f"https://api.maelyn.tech/api/generator/prompt?q={prompt}&apikey={API_MAELYN}"
    respon = await Tools.fetch.get(url)
    await prs.edit(f"{em.proses}**Please wait...**")
    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.edit(f"`{data}`")
        except Exception as er:
            await prs.delete()
            return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
    else:
        return await prs.edit(f"**{em.gagal}Please try again: {respon.status_code}!**")
