from Navy import bot
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools, animate_proses
from config import (API_MAELYN, BOT_ID, BOT_NAME, HELPABLE, SUDO_OWNERS, URL_LOGO, ALIVE_PIC)


@CMD.UBOT("alive")
@CMD.DEV_CMD("alive")
@CMD.FAKEDEV("alive")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    query = "alive"
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            return await message.delete()
    except Exception as error:
        return await message.reply(f"{em.gagal}Error: {str(error)}")
