import os
import re
import time
import traceback
from datetime import timedelta

import wget

from Navy import bot
from Navy.helpers import CMD, Emoji, YoutubeSearch, youtube
from Navy.logger import logger

__MODULES__ = "ʏᴏᴜᴛᴜʙᴇ"
__HELP__ = """<blockquote>Command Help **Youtube**</blockquote>

<blockquote>**Download the audio**</blockquote>
    **Download audio from youtube, you can use title or url**
        `{0}song` (url/title)
        
<blockquote>**Download the video**</blockquote>
    **Download video from youtube, you can use title or url**
        `{0}video` (url/title)
    
<b>   {1}</b>
"""


def clean_yt_url(url: str):
    if not url:
        return url
    match = re.search(r"(https://www\.youtube\.com/watch\?v=[\w-]+)", url)
    return match.group(1) if match else url


@CMD.UBOT("vsong|video|song")
async def _(client, message):
    try:
        em = Emoji(client)
        await em.get()
        pref = client.get_prefix(client.me.id)
        x = next(iter(pref))
        cmd = message.command[0].lower()
        if cmd in ["video", "vsong"]:
            as_video = True
        else:
            as_video = False
        now = time.time()
        proses_ = await em.get_costum_text()
        if len(message.command) < 2 and not message.reply_to_message:
            return await message.reply_text(
                f"{em.gagal}<b>Please give query or link:\n\nExample <code>{x}{cmd}</code> [title or link]</b>",
            )
        pros = await message.reply_text(f"{em.proses}<b>{proses_[4]}</b>")
        kueri = client.get_text(message)
        if re.match(r"^https?://", kueri):
            link = clean_yt_url(kueri)
        else:
            try:
                yt_search = YoutubeSearch(kueri, max_results=1)
                await yt_search.fetch_results()
                link = clean_yt_url(yt_search.get_link())
                logger.info(f"Clean Link: {link}")
            except Exception as error:
                return await pros.edit(
                    f"{em.gagal}<b>ERROR:</b><code>{str(error)}</code>"
                )
        
        pros = await pros.edit(
            f"{em.proses}<b>Try to downloading {'video' if as_video else 'audio'}...</b>"
        )
        user_mention = message.from_user.mention if message.from_user else client.me.mention
        try:
            (
                file_name,
                inpoh,
                title,
                duration,
                views,
                channel,
                url,
                thumb,
                data_ytp,
            ) = await youtube.download(link, client, as_video=as_video, user_mention=user_mention)

            if not as_video and not file_name.endswith(".mp3"):
                new_name = file_name.rsplit(".", 1)[0] + ".mp3"
                os.rename(file_name, new_name)
                file_name = new_name

            if isinstance(duration, str):
                duration = duration.replace(".", "")
            duration = int(duration)

        except Exception as error:
            return await pros.edit(f"{em.gagal}<b>ERROR:</b><code>{str(error)}</code>")

        thumbnail = wget.download(thumb)
        kontol = user_mention or client.me.mention
        kapten = data_ytp.format(
            inpoh,
            title,
            timedelta(seconds=duration),
            views,
            channel,
            url,
            bot.me.mention,
            kontol,
        )

        if as_video:
            await client.send_video(
                message.chat.id,
                video=file_name,
                thumb=thumbnail,
                file_name=title,
                duration=duration,
                supports_streaming=True,
                caption=f"{kapten}",
                progress=youtube.progress,
                progress_args=(
                    pros,
                    now,
                    f"{em.proses}<b>Trying to upload...</b>",
                    f"{file_name}",
                ),
                reply_to_message_id=message.id,
            )
        else:
            await client.send_audio(
                message.chat.id,
                audio=file_name,
                thumb=thumbnail,
                file_name=title,
                performer=channel,
                duration=duration,
                caption=f"{kapten}",
                progress=youtube.progress,
                progress_args=(
                    pros,
                    now,
                    f"{em.proses}<b>Trying to upload...</b>",
                    f"{file_name}",
                    client
                ),
                reply_to_message_id=message.id,
            )
        await pros.delete()
        if os.path.exists(thumbnail):
            os.remove(thumbnail)
        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as er:
        logger.error(f"Error: {traceback.format_exc()}")