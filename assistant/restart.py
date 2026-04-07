import asyncio
import importlib

from pyrogram.helpers import kb

from config import BOT_NAME
from Navy import UserBot, bot, navy
from Navy.database import dB
from Navy.helpers import CMD, Emoji, task
from plugins import PLUGINS


keyboard = kb([["🛑 Canceled"]], resize_keyboard=True, one_time_keyboard=True)


async def reset_costum_text(client, message):
    user_id = message.from_user.id
    proses = await message.reply("<b>Processing...</b>")
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard
        )
    try:
        await dB.set_var(user_id, "text_ping", "ᴘɪɴɢ")
        await dB.set_var(user_id, "text_uptime", "ᴜᴘᴛɪᴍᴇ")
        mmg = f"<a href=tg://user?id={message.from_user.id}>{message.from_user.first_name} {message.from_user.last_name or ''}</a>"
        await dB.set_var(user_id, "text_owner", f"<b>ᴏᴡɴᴇʀ :</b> {mmg}")
        ppq = f"<a href=tg://user?id=8771718801>{BOT_NAME}</a>"
        await dB.set_var(user_id, "text_ubot", f"{ppq}")
        await dB.set_var(user_id, "text_gcast", "ᴘʀᴏᴄᴇssɪɴɢ")
        await dB.set_var(user_id, "text_sukses", "ɢᴄᴀsᴛ sᴜᴋsᴇs")
        await dB.set_var(user_id, "text_keterangan", "ᴋᴇᴛᴇʀᴀɴɢᴀɴ")
        await asyncio.sleep(1)
        return await proses.edit(
            "<b>Your costum text has been reset</b>", reply_markup=keyboard
        )
    except Exception as er:
        return await proses.edit(f"<b>ERROR: `{str(er)}`</b>", reply_markup=keyboard)


async def reset_emoji(client, message):
    user_id = message.from_user.id
    proses = await message.reply("<b>Processing...</b>")
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard
        )
    for User in navy._ubot:
        if user_id == User.me.id:
            try:
                em = Emoji(User)
                await em.reset_emoji()
                await asyncio.sleep(1)
                return await proses.edit(
                    "<b>Your costum emoji has been reset.!!</b>", reply_markup=keyboard
                )
            except Exception as er:
                return await proses.edit(
                    f"<b>ERROR: `{str(er)}`</b>", reply_markup=keyboard
                )


async def reset_prefix(client, message):
    mepref = [".", ",", "?", "+", "!"]
    proses = await message.reply("<b>Processing...</b>")
    user_id = message.from_user.id
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard
        )
    for x in navy._ubot:
        if x.me.id == user_id:
            x.set_prefix(x.me.id, mepref)
            await dB.set_pref(x.me.id, mepref)
            return await proses.edit(
                f"<b>Your prefix has been reset to: `{' '.join(mepref)}` .</b>",
                reply_markup=keyboard,
            )


async def restart_userbot(client, message):
    proses = await message.reply("<b>Processing...</b>")
    user_id = message.from_user.id
    if user_id not in navy._get_my_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard
        )
    for X in await dB.get_userbots():
        if user_id == int(X["name"]):
            try:
                ubot = UserBot(**X)
                await ubot.start()
                for modul in PLUGINS:
                    importlib.reload(importlib.import_module(f"plugins.{modul}"))
                
                return await proses.edit(
                    f"<b>✅ Userbot has been restarted {ubot.me.first_name} {ubot.me.last_name or ''} | {ubot.me.id}.</b>",
                    reply_markup=keyboard,
                )

            except Exception as error:
                return await proses.edit(f"<b>{error}</b>", reply_markup=keyboard)

@CMD.BOT("restart")
async def _(client, message):
    return await restart_userbot(client, message)
