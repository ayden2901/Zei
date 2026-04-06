__MODULES__ = "ᴋʙʙɪ"
__HELP__ = """<blockquote>Command Help **Kbbi**</blockquote>

<blockquote>**Get word from kbbi**</blockquote>
    **Search words from KBBI**
        `{0}kbbi` (text/reply text)

<b>   {1}</b>
"""


from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools


@CMD.UBOT("kbbi")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    prompt = client.get_text(message)
    if not prompt:
        return await proses.edit(
            f"{em.gagal}**Please reply to a message containing the prompt!\n"
            f"Example: `{message.text.split()[0]} pohon`**"
        )

    url = f"https://api.maelyn.tech/api/kbbi?q={prompt}&apikey={API_MAELYN}"
    response = await Tools.fetch.get(url)
    if response.status_code == 200:
        data = response.json()["result"]
        result = "**KBBI Result:**\n\n"

        if "description" in data:
            result += "**Deskripsi:**\n"
            result += f"- {data.get('description')}\n\n"

        if "relatedWords" in data:
            result += "**Kata Dasar Lain:**\n"
            result += ", ".join(data.get("relatedWords")) + "\n\n"

        if "baseWord" in data:
            result += "**baseWord:**\n"
            result += f"- **{data['baseWord']}\n"

        return await proses.edit(result)
    else:
        return await proses.edit(f"{em.gagal}**Failed to fetch data from KBBI API!**")
