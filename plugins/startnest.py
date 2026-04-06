from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "sᴛᴀʀɴᴇsᴛ"
__HELP__ = """<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>sᴛᴀʀɴᴇsᴛ</b></u>

<blockquote>❖ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>sᴛᴀʀɴᴇsᴛ</b>
    ➢ `{0}starnest` [ᴘʀᴏᴍᴘᴛ]</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("starnest")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"{em.gagal} **Please reply to message text or give message!\nExample: `{message.text.split()[0]} beautiful girl`.**"
        )
    proses_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses}**{proses_[4]}**")
    try:
        url = f"https://api.maelyn.tech/api/txt2img/startnest?prompt={text}&apikey={API_MAELYN}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            image = result.json()["result"].get("url")
            await message.reply_photo(image)
            return await pros.delete()
        else:
            return await pros.edit(f"{em.gagal}**ERROR:**{result.status_code}")
    except Exception as e:
        await message.reply(f"{em.gagal}**ERROR:** {str(e)}")
        return await pros.delete()
