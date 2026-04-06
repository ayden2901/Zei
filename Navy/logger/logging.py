import logging
import os
from pyrogram.types import ChatPrivileges
import config
from pyrogram.errors import ChannelInvalid, PeerIdInvalid


class ConnectionHandler(logging.Handler):
    def emit(self, record):
        for X in ["OSErro", "TimeoutError", "socket"]:
            if X in record.getMessage():
                os.execl("/bin/bash", "bash", "start.sh")


logging.basicConfig(level=logging.INFO, format="%(name)s[%(levelname)s]: %(message)s")
logger = logging.getLogger(f"{config.BOT_NAME}")
connection_handler = ConnectionHandler()

for lib in {
    "pyrogram",
    "gunicorn",
    "flask",
    "py-tgcalls",
    "pytgcalls",
    "aiorun",
    "asyncio",
    "hydrogram",
}:
    logging.getLogger(lib).setLevel(logging.ERROR)
    logging.getLogger(lib).addHandler(connection_handler)


async def getFinish():
    emut = await navy.get_prefix(navy.me.id)
    xx = " ".join(emut)
    try:
        await bot.send_message(
            int(chat_id),
            f"""
<b>Userbot Successfully Deploy !!</b>
<b>Prefixes : {xx}</b>
""",
        )
    except (ChannelInvalid, PeerIdInvalid):
        try:
            await navy.promote_chat_member(
                int(chat_id),
                bot.me.username,
                privileges=ChatPrivileges(
                    can_change_info=True,
                    can_invite_users=True,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=True,
                    can_manage_chat=True,
                    can_manage_video_chats=True,
                ),
            )
            await bot.send_message(
                int(chat_id),
                f"""
<b>Userbot Successfully Deploy !!</b>
<b>Prefixes : {xx}</b>
""",
            )
        except:
            return