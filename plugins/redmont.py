import traceback

from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools
from Navy.logger import logger

__MODULES__ = "ʀᴇᴅᴍᴏɴᴛ"
__HELP__ = """<blockquote>Command Help **Redmont**</blockquote>

<blockquote>**Generate image redmont art**</blockquote>
    **Generate image ai from you prompt use redmont art** 
        `{0}redmont` (prompt)

<b>   {1}</b>
"""


@CMD.UBOT("redmont")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    prompt = client.get_text(message)
    if not prompt:
        return await proses.edit(
            f"{em.gagal}**Please reply to a message containing the prompt!\n"
            f"Example: `{message.text.split()[0]} beautiful japanese girl`**"
        )
    if prompt in ["Portrait", "portrait"]:
        reso = "Portrait"
    elif prompt in ["Square", "square"]:
        reso = "Square"
    elif prompt in ["Wide", "wide"]:
        reso = "Wide"
    else:
        reso = "Wide"
    try:
        url = f"https://api.maelyn.tech/api/txt2img/redmondart?prompt={prompt}&resolution={reso}&apikey={API_MAELYN}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            data = result.json()["result"]
            command = data["info"].get("prompt")
            model = data["info"].get("model")
            image = data["image"].get("url")
            await client.send_photo(
                message.chat.id,
                photo=image,
                caption=f"**{em.sukses}**Prompt**: `{command}`\n**Model**: {model}",
            )
        else:
            await message.reply(
                f"{em.gagal}**Failed to generate: {result.status_code}**"
            )

    except Exception as e:
        logger.error(f"ERROR: {traceback.format_exc()}")
        await message.reply(f"{em.gagal}**Error: {str(e)}**")
    return await proses.delete()
