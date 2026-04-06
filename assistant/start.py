import asyncio

from config import LOG_SELLER, SUDO_OWNERS, BOT_ID
from Navy import bot
from Navy.database import state, dB
from Navy.helpers import CMD, FILTERS, ButtonUtils, Message, Tools
from pyrogram.helpers import ikb, kb
from Navy.logger import logger

from pyrogram.types import ChatMemberUpdated

from pyrogram import filters


@CMD.BOT("start", FILTERS.PRIVATE)
@CMD.DB_BROADCAST
async def start_home(client, message):
    data = "CAACAgQAAyEFAASMNRIdAAILO2gAAb0JcVFM0T9CH4I98BOSudI08wAC0AsAAmCiMFCyj6GosflqdR4E"
    nikol = await message.reply_sticker(data)
    try:
        user = message.from_user
        await dB.add_to_var(BOT_ID, "BROADCAST", user.id)
        if user.id in SUDO_OWNERS:
            buttons = ButtonUtils.start_menu(is_admin=True)
        else:
            buttons = ButtonUtils.start_menu(is_admin=False)
            sender_id = message.from_user.id
            sender_mention = message.from_user.mention
            sender_name = message.from_user.first_name
            await client.send_message(
                LOG_SELLER,
                f"<b>User: {sender_mention}\nID: `{sender_id}`\nName: {sender_name}\nHas started your bot.</b>",
            )
        text = Message.welcome_message(client, message)
        await asyncio.sleep(2)
        await nikol.delete()
        return await message.reply_text(
            text, reply_markup=buttons, disable_web_page_preview=True
        )
    except Exception as er:
        logger.error(f"{str(er)}")


@CMD.BOT("button")
async def _(client, message):
    link = message.text.split(None, 1)[1]
    tujuan, _id = Tools.extract_ids_from_link(link)
    txt = state.get(message.from_user.id, "edit_reply_markup")
    teks, button = ButtonUtils.parse_msg_buttons(txt)
    if button:
        button = await ButtonUtils.create_inline_keyboard(button)
    return await client.edit_message_reply_markup(
        chat_id=tujuan, message_id=_id, reply_markup=button
    )


@CMD.BOT("id")
async def _(client, message):
    if len(message.command) < 2:
        return
    query = message.text.split()[1]
    try:
        reply = message.reply_to_message
        media = Tools.get_file_id(reply)
        data = {"file_id": media["file_id"], "type": media["message_type"]}
        state.set(message.from_user.id, query, data)
        return
    except Exception as er:
        logger.error(f"{str(er)}")

@CMD.BOT("joinseller", FILTERS.PRIVATE)
async def join_seller(client, message):
    userid = message.from_user.id
    mention = message.from_user.mention
    keyboard = kb([["🛑 Canceled"]], resize_keyboard=True, one_time_keyboard=True)
    await message.reply(
            f"<blockquote expandable>**Rules For Reseller!**\n"
            f"- Memiliki basic dasar untuk berjualan.\n- Bertanggung jawab.\n- Tidak menjual(Seller) Userbot ditempat lain Only ◖sтαя ꭙ ꝛσʙσᴛ◗.\n- Dilarang keras melakukan penipuan mengatas namakan StarXCodeBot.\n- Memiliki Bank / E-wallet untuk transaksi.\n\nKeuntungan Reseller:\n- Mendapatkan harga seller yang lebih murah yaitu Rp.50.000 - Rp.75.000 dan anda bisa menjual Userbot di harga Rp.15.000 - Rp.25.000.\n- Diberi akses seller Userbot jadi tidak perlu ribet menunggu owner Userbot untuk memberi akses pembeli.\n- Diajari cara kerja Userbot ini digrup khusus seller jika anda belum mengerti.\n- Dalam grup tidak hanya menjual Userbot & Ankes saja banyak bot lain lain dan jajanan telegram yang bisa kalian sharing antara seller Userbot.\n\nUntuk pendafta pemula dikenakan tarif regristasi sebesar Rp.15.000 dan sudah free pemasangan userbot selama anda masih aktif menjual userbot.\n\nJika Setuju dengan seluruh rules\nHubungi contact untuk mendaftar\nContact : @starbotdevs**</blockquote>",
                reply_markup=keyboard,
        )
