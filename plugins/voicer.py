import os
import subprocess

import gtts
import speech_recognition as sr

from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ᴠᴏɪᴄᴇ"
__HELP__ = """<blockquote>Command Help **Voice**</blockquote>

<blockquote>**Send text to voice**</blockquote>
    **You can convert text to voice**
        `{0}tts` (text/reply text)

<blockquote>**Get text from voice**</blockquote>
    **You can convert text from voice**
        `{0}stt` (reply audio)

<blockquote>**Extract instruments**</blockquote>
    **You can extract instruments from media**
        `{0}vremover` (reply audio)

<b>   {1}</b>
"""


@CMD.UBOT("vremover")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    rep = message.reply_to_message or message
    if not rep or not (rep.audio, rep.video):
        return await prs.edit(f"{em.gagal}**Please reply to audio or video!!**")
    arg = await Tools.upload_media(message)
    url = f"https://api.botcahx.eu.org/api/tools/voiceremover?url={arg}&apikey={API_BOTCHAX}"
    respon = await Tools.fetch.get(url)
    ex = await message.reply(f"{em.proses}**Try to extract of instruments...**")

    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.delete()
            voice = data["vocal_path"]
            audio = data["instrumental_path"]
            send_voice = await client.send_audio(
                message.chat.id, voice, caption=f"<b>Vocal</b>"
            )
            send_audio = await client.send_audio(
                message.chat.id, audio, caption=f"<b>Instruments</b>"
            )
            await ex.delete()
            return await message.reply(
                f"{em.sukses}<blockquote>**Status error:** {data['error']}\n**Status message:** {data['message']}\n**Vocal of the <a href='{rep.link}'>media</a>:** <a href='{send_voice.link}'>here</a>\n**Instruments of the <a href='{rep.link}'>media</a>:** <a href='{send_audio.link}'>here</a></blockquote>",
                disable_web_page_preview=True,
            )
        except Exception as er:
            await ex.delete()

            return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
    else:
        return await message.reply(
            f"**{em.gagal}Please try again: {respon.status_code}!**"
        )


@CMD.UBOT("tts")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()

    pros = await message.reply(f"{em.proses}**{proses_[4]}**")
    bhs = await client.get_translate()
    if message.reply_to_message:
        kata = message.reply_to_message.text or message.reply_to_message.caption
    else:
        if len(message.command) < 2:
            return await pros.edit(
                f"{em.gagal}**Please reply to message text or give text!**"
            )
        else:
            kata = message.text.split(None, 1)[1]
    gts = gtts.gTTS(kata, lang=bhs)
    gts.save("trs.oog")
    rep = message.reply_to_message or message
    try:
        await client.send_voice(
            chat_id=message.chat.id,
            voice="trs.oog",
            reply_to_message_id=rep.id,
        )
        await pros.delete()
        os.remove("trs.oog")
        return
    except Exception as er:
        return await pros.edit(f"{em.gagal}**Error: {str(er)}**")

    except FileNotFoundError:
        return


@CMD.UBOT("stt")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    reply = message.reply_to_message
    if not reply:
        return await proses.edit(f"{em.gagal}**Please reply to message**")

    try:
        file_path = await reply.download()
        wav_path = file_path + ".wav"
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                file_path,
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                wav_path,
            ],
            check=True,
        )

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="id-ID")
                await proses.edit(
                    f"{em.sukses}**Converted [message]({reply.link}):**\n{text}",
                    disable_web_page_preview=True,
                )
            except sr.UnknownValueError:
                return await proses.edit(
                    f"{em.gagal}**Sorry, I can't recognize the sound.**"
                )
            except sr.RequestError:
                return await proses.edit(
                    f"{em.gagal}**Sorry, there is a problem with the voice recognition service.**"
                )

            finally:
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

    except subprocess.CalledProcessError:
        return await proses.edit(f"{em.gagal}**Failed to convert audio files.**")
