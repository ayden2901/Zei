import wget

from Navy.helpers import CMD, Emoji, Tools
from Navy.logger import logger

processed_surah_numbers = set()


__MODULES__ = "ǫᴜʀ'ᴀɴ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ǫᴜʀ'ᴀɴ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ǫᴜʀ'ᴀɴ</b>
    ➢ `{0}surat` [ɴᴀᴍᴇ]
    ➢ `{0}listsurah`</blockquote>

<b>   {1}</b>"""


def download_audio(url, file_name):
    try:
        wget.download(url, file_name)
        return True
    except Exception as e:
        logger.error(f"Failed to download audio: {e}")
        return False


async def ambil_nama_surah(surah_name):
    response = await Tools.fetch.get("https://equran.id/api/v2/surat")
    if response.status_code == 200:
        surah_list = response.json()["data"]
        for surah_info in surah_list:
            if surah_info["namaLatin"].lower() == surah_name.lower():
                return surah_info
    return None


async def ambil_daftar_surah():
    response = await Tools.fetch.get("https://equran.id/api/v2/surat")
    surah_list = []
    if response.status_code == 200:
        data = response.json()["data"]
        for surah_info in data:
            surah_list.append(
                (
                    surah_info["nomor"],
                    surah_info["namaLatin"],
                    surah_info["jumlahAyat"],
                    surah_info["tempatTurun"],
                )
            )
    return surah_list


@CMD.UBOT("listsurah")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    message.reply_to_message or message
    msg = f"<blockquote>{em.data}<b>ɴᴀᴍᴀ sᴜʀᴀᴛ, ᴊᴜᴍʟᴀʜ sᴜʀᴀᴛ, ᴛᴇᴍᴘᴀᴛ sᴜʀᴀᴛ ᴛᴜʀᴜɴ :</b></blockquote>\n"
    for count, nama, jumlah, turun in await ambil_daftar_surah():
        msg += f"🕌 {count}. <b>{nama}</b>, <code>{jumlah}</code>, <b>{turun}</b>\n"
    return await proses.edit(msg)


@CMD.UBOT("surat|surah|quran")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses}**{proses_[4]}**")
    surah_name = (
        message.text.split(maxsplit=1)[1].strip().lower()
        if len(message.command) > 1
        else None
    )

    if not surah_name:
        return await pros.edit(f"{em.gagal}**Please provide a Surah name**")

    surah_info = await ambil_nama_surah(surah_name)
    reply = message.reply_to_message or message

    if surah_info:
        response_text = (
            f"**Nomor Surah**: `{surah_info['nomor']}`\n"
            f"**Nama Surah**: `{surah_info['nama']}`\n"
            f"**Nama Surah (Latin)**: `{surah_info['namaLatin']}`\n"
            f"**Jumlah Ayat**: `{surah_info['jumlahAyat']}`\n"
            f"**Tempat Turun**: `{surah_info['tempatTurun']}`\n"
            f"**Arti**: `{surah_info['arti']}`\n"
            f"**Deskripsi**: `{surah_info['deskripsi']}`\n"
        )

        audio_urls = surah_info["audioFull"]
        qori_name = None
        for key, url in audio_urls.items():
            if url:
                qori_name = url.split("audio-full/")[1].split("/")[0]
                break

        response_text += f"**Qori**: `{qori_name}`\n" if qori_name else ""
        audio_url = next((url for url in audio_urls.values() if url), None)
        if audio_url:
            audio_file_name = f"{surah_name.capitalize()}.mp3"
            if download_audio(audio_url, audio_file_name):
                if len(response_text) > 4096:
                    file_name = f"{surah_name.capitalize()}.txt"
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(response_text)
                    aud = await message.reply_audio(
                        audio_file_name, reply_to_message_id=reply.id
                    )
                    await message.reply_document(file_name, reply_to_message_id=aud.id)
                else:
                    await message.reply_audio(
                        audio_file_name,
                        caption=response_text,
                        reply_to_message_id=reply.id,
                    )
            else:
                await message.reply(f"{em.gagal}**Failed to download audio**")
        else:
            await message.reply(response_text, reply_to_message_id=reply.id)

        return await pros.delete()
    else:
        await message.reply(f"{em.gagal}**Surah not found**")
        return await pros.delete()
