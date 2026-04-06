
import asyncio
import html
from Navy import bot, navy
from Navy.helpers import CMD, Emoji
from pyrogram.enums import ParseMode
from pyrogram.types import Message

__MODULES__ = "ᴢᴏᴍʙɪᴇs"
__HELP__ = """
<blockquote expandable><b>ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ ᴢᴏᴍʙɪᴇs

• Perintah: <code>{0}zombies</code>
• Penjelasan: Untuk mengeluarkan akun depresi digrup anda.</b></blockquote>
<b>   {1}</b>
"""

@CMD.UBOT("zombies")
async def _(client, message):
    await zombies_cmd(client, message)

async def zombies_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_}**")
    chat_id = message.chat.id
    deleted_users = []
    banned_users = 0
    Tm = await message.reply(f"{em.proses}Prosessing")
    async for i in client.get_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if len(deleted_users) > 0:
        for deleted_user in deleted_users:
            try:
                banned_users += 1
                await message.chat.ban_member(deleted_user)
            except Exception:
                pass
        await Tm.edit(f"{em.sukses}<b>Berhasil mengeluarkan {banned_users} akun terhapus</b>")
    else:
        await Tm.edit("{warn}<b>Tidak ada akun terhapus disini.</b>")