__MODULES__ = "ᴛᴡɪᴛᴛᴇʀ"
__HELP__ = """<blockquote>Command Help **Twitter**</blockquote>

<blockquote>**Download media from twitter**</blockquote>
    **You can download any media from twitter**
        `{0}twdl` (url)

<b>   {1}</b>
"""
import traceback

from pyrogram.types import InputMediaPhoto, InputMediaVideo

from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools
from Navy.logger import logger


@CMD.UBOT("twdl|twitter")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    arg = client.get_text(message)

    if not arg:
        return await message.reply(
            f"{em.gagal}<b>Please give word or links!!\nExample: `{message.text.split()[0]} https://x.com/kenapanan/status/1887380401435648064/photo/1`</b>"
        )

    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    if not arg.startswith("https://"):
        return await proses.edit(
            f"{em.gagal}**Please provide link.\nExample: `{message.text.split()[0]} https://x.com/kenapanan/status/1887380401435648064/photo/1`**"
        )

    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")

    try:
        url = f"https://api.botcahx.eu.org/api/download/twitter2?url={arg}&apikey={API_BOTCHAX}"
        response = await Tools.fetch.get(url)

        if response.status_code != 200:
            return await proses.edit(
                f"{em.gagal}**Request failed with status code {response.status_code}**"
            )

        data = response.json()
        if not data.get("result"):
            return await proses.edit(f"{em.gagal}**No result data in response**")

        result = data["result"]
        media_urls = result.get("mediaURLs", [])
        caption = result.get("text", "")

        if not media_urls:
            return await proses.edit(f"{em.gagal}**No media found in the tweet**")

        await proses.edit(f"{em.proses}**Preparing media for sending...**")

        media_group = []

        for url in media_urls:
            if url.endswith((".mp4", ".MP4")):
                media = await Tools.get_media_data(url, "mp4")
                media_group.append(
                    InputMediaVideo(
                        media=media, caption=caption if len(media_group) == 0 else ""
                    )
                )
            else:
                media = await Tools.get_media_data(url, "jpg")
                media_group.append(
                    InputMediaPhoto(
                        media=media, caption=caption if len(media_group) == 0 else ""
                    )
                )

        if media_group:
            await proses.delete()
            return await client.send_media_group(
                chat_id=message.chat.id, media=media_group
            )
        else:
            return await proses.edit(
                f"{em.gagal}**Failed to prepare media for sending**"
            )

    except Exception as er:
        logger.error(f"twdl: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}")
