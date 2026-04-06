from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools, animate_proses

__MODULES__ = "ᴀɢᴇ"
__HELP__ = """<blockquote expandable>Command Help **Age**</blockquote>

<blockquote>**Basic command** </blockquote>
    **You can get information about user from photo**
        `{0}age` (reply to photo)

<b>   {1}</b>
"""


@CMD.UBOT("age")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    proses_ = await emo.get_costum_text()
    XD = await animate_proses(message, em.proses)
    if not message.reply_to_message:
        return await XD.edit(f"{emo.gagal}**Please reply to message photo!**")
    try:
        media = await Tools.upload_media(message)
        url = f"https://api.botcahx.eu.org/api/search/agedetect?url={media}&apikey={API_BOTCHAX}"
        data = await Tools.fetch.get(url)
        data = data.json()
        if data["status"] == False:
            return await XD.edit(f"{emo.gagal}**{data['message']}**")
        result = data["result"]
        caption = f"""
<blockquote expandable>**Age Detect AI**
- **Score**: {result['score']}
- **Age**: {result['age']}
- **Gender**: {result['gender']}
- **Expression**: {result['expression']}
- **Face Shape**: {result['faceShape']}</blockquote>"""
        return await XD.edit(caption)
    except Exception as exc:
        return await XD.edit(f"{emo.gagal}**{exc}**")
