__MODULES__ = "ᴘɪɴᴛᴇʀᴇsᴛ"
__HELP__ = """<blockquote>Command Help **Pindl**</blockquote>

<blockquote>**Search media from pinterest** </blockquote>
    **You can download media from pinterest from title or url**
        `{0}pindl` (title/url)

<b>   {1}</b>
"""

import traceback
from uuid import uuid4

from config import API_BOTCHAX
from Navy import bot
from Navy.database import state
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools
from Navy.logger import logger

MAX_MEDIA_PER_BATCH = 7


@CMD.UBOT("pinterest|pindl")
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

    try:
        if prompt.startswith("https"):
            url = f"https://api.botcahx.eu.org/api/download/pinterest?url={prompt}&apikey={API_BOTCHAX}"
            response = await Tools.fetch.get(url)

            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {}).get("data", {})

                if result.get("media_type") == "image":
                    await message.reply_photo(
                        result["image"], caption=result["title"] or ""
                    )
                elif result.get("media_type") == "video/mp4":
                    await message.reply_video(
                        result["video"], caption=result["title"] or ""
                    )

                return await proses.delete()
            else:
                return await proses.edit(
                    f"{em.gagal}**Failed to download from the provided URL.**"
                )

        else:
            url = f"https://api.botcahx.eu.org/api/search/pinterest?text1={prompt}&apikey={API_BOTCHAX}"
            response = await Tools.fetch.get(url)

            if response.status_code == 200:
                data = response.json()
                uniq = f"{str(uuid4())}"
                state.set(uniq.split("-")[0], uniq.split("-")[0], data["result"])

                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    message.chat.id,
                    bot.me.username,
                    f"inline_pinsearch {uniq.split('-')[0]}",
                )
                if inline:
                    return await proses.delete()

            return await proses.edit(
                f"{em.gagal}**No images were found for these keywords!**"
            )

    except Exception as er:
        logger.error(f"Pinteres: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}")
