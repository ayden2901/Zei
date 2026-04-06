__MODULES__ = "ɢᴇᴍᴘᴀ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ɢᴇᴍᴘᴀ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ɢᴇᴍᴘᴀ</b>
    ➢ `{0}gempa`</blockquote>

<b>   {1}</b>
"""


from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools


@CMD.UBOT("gempa")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    msg = ""
    try:
        url = f"https://api.botcahx.eu.org/api/search/gempa?apikey={API_BOTCHAX}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            data = result.json()["result"]
            try:
                fields = {
                    "Tanggal": data["result"].get("tanggal", "-"),
                    "Jam": data["result"].get("jam", "-"),
                    "Lintang": data["result"].get("Lintang", "-"),
                    "Bujur": data["result"].get("Bujur", "-"),
                    "Magnitudo": data["result"].get("Magnitudo", "-"),
                    "Kedalaman": data["result"].get("Kedalaman", "-"),
                    "Potensi": data["result"].get("Potensi", "-"),
                    "Wilayah": data["result"].get("Wilayah", "-"),
                    "Map": data["result"].get("Map", "-"),
                    "Waktu": data["result"].get("waktu", "-"),
                }

                msg = "\n".join([f"{key}: {value}" for key, value in fields.items()])

                if data["result"].get("image"):
                    img = data["result"]["image"]
                    await message.reply_photo(
                        img, caption=f"<blockquote><b>{msg}</blockquote></b>"
                    )
                else:
                    await message.reply(f"<blockquote><b>{msg}</blockquote></b>")

            except Exception as er:
                await message.reply(f"{em.gagal}**ERROR**: {str(er)}")
        else:
            await message.reply(f"{em.gagal}**ERROR fetching data!**")
    except Exception as er:
        await message.reply(f"{em.gagal}**ERROR**: {str(er)}")
    return await proses.delete()
