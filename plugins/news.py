__MODULES__ = "ɴᴇᴡs"
__HELP__ = """<blockquote>Command Help **News**</blockquote>

<blockquote>**Basic Commands**</blockquote>
    **You can get news from CNN Indonesia**
        `{0}cnn`
    **You can get news from Detik**
        `{0}detik`
        
<b>   {1}</b>
"""

from uuid import uuid4

import config
from Navy import bot
from Navy.database import state
from Navy.helpers import CMD, ButtonUtils, Tools


@CMD.UBOT("detik|cnn")
async def _(_, message):
    query = message.command[0]
    if query == "cnn":
        url = f"https://api.botcahx.eu.org/api/news/cnn?apikey={config.API_BOTCHAX}"
    elif query == "detik":
        url = f"https://api.botcahx.eu.org/api/news/detik?apikey={config.API_BOTCHAX}"
    response = await Tools.fetch.get(url)
    if response.status_code == 200:
        data = response.json()["result"]
        uniq = f"{str(uuid4())}"
        state.set(uniq.split("-")[0], uniq.split("-")[0], data)
        try:
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                message.chat.id,
                bot.me.username,
                f"inline_news {uniq.split('-')[0]}",
            )
            if inline:
                return await message.delete()
        except Exception as er:
            return await message.reply(f"**ERROR**: {str(er)}")
    else:
        return await message.reply(f"**Error with status `{response.status_code}`**")
