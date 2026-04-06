import asyncio

from config import BOT_NAME, HELPABLE
from Navy import bot, dB
from Navy.helpers import (CMD, Emoji, Tools, Basic_Effect, Premium_Effect, animate_proses, ButtonUtils, FILTERS)
from assistant.help import cek_plugins


@CMD.UBOT("set_helpsticker")
@CMD.DEV_CMD("set_helpsticker")
async def set_help_sticker(client, message):
    em = Emoji(client)
    await em.get()
    msg = await animate_proses(message, em.proses)

    arg = client.get_arg(message)

    # hapus help sticker
    if arg and arg.lower() == "none":
        data = await dB.get_var(client.me.id, "help_sticker")

        if not data:
            return await msg.edit(
                f"{em.gagal}<b>Belum ada data help sticker.</b>"
            )

        await dB.remove_var(client.me.id, "help_sticker")
        return await msg.edit(
            f"{em.sukses}<b>Help sticker berhasil dihapus.</b>"
        )

    if not message.reply_to_message:
        return await msg.edit(
            f"{em.gagal}<b>Reply sticker untuk mengubah help sticker.</b>\n"
            f"<code>.set_helpsticker none</code> untuk menghapus."
        )

    media = Tools.get_file_id(message.reply_to_message)

    if not media:
        return await msg.edit(
            f"{em.gagal}<b>Media sticker tidak ditemukan.</b>"
        )

    if media["message_type"] != "sticker":
        return await msg.edit(
            f"{em.gagal}<b>Media yang kamu atur bukan <code>sticker</code>.</b>"
        )

    await dB.set_var(client.me.id, "help_sticker", media["file_id"])

    await msg.edit(
        f"{em.sukses}<b>Help sticker berhasil di setting.</b>"
    )

@CMD.BOT("help", filter=FILTERS.PRIVATE)
async def _(client, message):
    return await cek_plugins(client, message)
@CMD.UBOT("help")
@CMD.DEV_CMD("help")
@CMD.FAKEDEV("help")
async def _(client, message):
    data = await dB.get_var(client.me.id, "help_sticker") or "CAACAgQAAyEFAASMNRIdAAIKbWgAAbLyEVLRB9aSOj1axZi1fjPldAAC3A8AAgXMuFNjeFLGHbr_mh4E"
    sticker = await message.reply_sticker(data)
    em = Emoji(client)
    await em.get()
    if not client.get_arg(message):
        query = "help"
        chat_id = (
            message.chat.id if len(message.command) < 2 else message.text.split()[1]
        )
        try:
            await asyncio.sleep(2)
            await sticker.delete()
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                chat_id,
                bot.me.username,
                query,
            )
            if inline:
                return await message.delete()
        except Exception as error:
            return await message.reply(f"{em.gagal}Error: {str(error)}")
    else:
        nama = f"{client.get_arg(message)}"
        pref = client.get_prefix(client.me.id)
        x = next(iter(pref))
        text_help2 = f"<blockquote><b>{bot.me.mention}\n{em.pin} ᴄʀᴇᴀᴛᴇᴅ ʙʏ ➟</b> <a href=tg://user?id=347422710>#1↻￴`sтαя⋆</a></blockquote>"
        await asyncio.sleep(2)
        await sticker.delete()
        if nama in HELPABLE:
            return await message.reply(
                f"{HELPABLE[nama]['module'].__HELP__.format(x, text_help2)}",
            )
        else:
            return await message.reply(
                f"{em.gagal}<b>Tidak ada modul bernama <code>{nama}</code></b>"
            )
