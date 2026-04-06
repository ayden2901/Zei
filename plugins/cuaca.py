__MODULES__ = "ᴄᴜᴀᴄᴀ"
__HELP__ = """<blockquote>Command Help **Cuaca** </blockquote>

<blockquote>**Get status country weather**</blockquote>
    **Get weather information of the country**
        `{0}cuaca` (country)

<b>   {1}</b>
"""


from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools


@CMD.UBOT("cuaca")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    rep = message.reply_to_message
    if len(message.command) < 2 and not rep:
        return await prs.edit(
            f"{em.gagal}**Please give country!!\nExample: `{message.text.split()[0]} jakarta`**"
        )
    arg = client.get_text(message)
    url = f"https://api.maelyn.tech/api/cuaca?q={arg}&apikey={API_MAELYN}"
    msg = ""
    respon = await Tools.fetch.get(url)
    if respon.status_code == 200:
        data = respon.json()
        fileds = {
            "Kota": data["result"].get("city", "-"),
            "Garis Bujur": data["result"].get("longitude", "-"),
            "Lintang": data["result"].get("latitude", "-"),
            "Suhu": data["result"].get("temperature", "-"),
            "Angin": data["result"].get("wind", "-"),
            "Kelembaban": data["result"].get("humidity", "-"),
            "Cuaca": data["result"].get("weather", "-"),
            "Keterangan": data["result"].get("description", "-"),
            "Tekanan": data["result"].get("pressure", "-"),
        }
        msg = "\n".join([f"{key}: {value}" for key, value in fileds.items()])
        try:
            await prs.delete()
            return await message.reply(f"<blockquote><b>{msg}</b></blockquote>")
        except Exception:
            await prs.delete()
            konten = str(msg)
            link = await Tools.paste(konten)
            return await message.reply(
                f"{em.sukses}**[Click here]({link}) to view weather of today.**",
                disable_web_page_preview=True,
            )
    else:
        return await prs.edit(f"**{em.gagal}Please try again: {respon.status_code}!**")
