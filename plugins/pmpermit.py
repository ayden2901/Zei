import asyncio

from pyrogram.enums import ChatType, ParseMode

from config import BOT_NAME, SUDO_OWNERS
from Navy import bot, navy
from Navy.database import dB, state
from Navy.helpers import CMD, ButtonUtils, Emoji, Tools
from Navy.logger import logger

__MODULES__ = "ᴘᴍᴘᴇʀᴍɪᴛ"
__HELP__ = """<blockquote>Command Help **PMPermit** </blockquote>

<blockquote>**On off pmpermit**</blockquote>
    **Set to on pmpermit**
        `{0}pmpermit set on`
    **Set to off pmpermit**
        `{0}pmpermit set off`

<blockquote>**Set media pmpermit**</blockquote>
    **You can set media to your pmpermit, media can be set photo, video**
        `{0}pmpermit media` (reply media)

<blockquote>**Set text pmpermit**</blockquote>
    **You can change costum text to your pmpermit message**
        `{0}pmpermit teks` (text/reply text)

<blockquote>**Set warn pmpermit**</blockquote>
    **You can set warning pmpermit for incoming message**
        `{0}pmpermit warn` (number) or 10

<blockquote>**Get status pmpermit**</blockquote>
    **For this command, you can get status, text, warn, and media from pmpermit or you can see example below**
        `{0}pmpermit get` (query)

<blockquote>**Approve disapprove user**</blockquote>
    **This command for approve user message**
        `{0}ok`
    **This command for disapprove user message**
        `{0}no`
    
<blockquote>**Example:**
    `{0}pmpermit get status`
    `{0}pmpermit get teks`
    `{0}pmpermit get warn`
    `{0}pmpermit get media`</blockquote>
    
<b>   {1}</b>
"""


flood = {}
flood2 = {}

DEFAULT_TEXT = "Hey {mention} 👋.  Don't spam or you'll be blocked!!"
PM_WARN = "You've got {}/{} warnings !!"
LIMIT = 5
INLINE_WARN = """<blockquote><b>{}

You've got {}/{} warnings !!</b></blockquote>"""


@CMD.UBOT("pmpermit")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"**{em.proses}{proses_}**")
    try:
        command, variable = message.command[:2]
    except ValueError:
        return await proses.delete()
    value = " ".join(message.command[2:])
    rep = message.reply_to_message
    if variable.lower() == "set":
        akt = ["on", "true"]
        mti = ["off", "false"]
        if value.lower() in akt:
            stat = await dB.get_var(client.me.id, "PMPERMIT")
            if stat:
                return await proses.edit(f"{em.sukses}**PMPermit already enable.")
            else:
                await dB.set_var(client.me.id, "PMPERMIT", value)
                return await proses.edit(f"{em.sukses}**PMPermit enable.**")
        elif value.lower() in mti:
            stat = await dB.get_var(client.me.id, "PMPERMIT")
            if stat:
                await dB.remove_var(client.me.id, "PMPERMIT")
                return await proses.edit(f"{em.gagal}**PMPermit disable.**")
            else:
                return await proses.edit(f"{em.gagal}**PMPermit already disabled.**")
        else:
            return await proses.edit(f"{em.gagal}**Please give query `on` or `off`.**")
    elif variable.lower() == "media":
        if value.lower() == "off":
            await dB.remove_var(client.me.id, "PMMEDIA")
            return await proses.edit(f"{em.sukses}**PMPermit media disabled.**")
        if not rep or not rep.media:
            return await proses.edit(f"{em.gagal}**Please reply to media**")
        copy = await rep.copy(bot.me.username)
        sent = await client.send_message(
            bot.me.username, f"/id PMMEDIA", reply_to_message_id=copy.id
        )
        await asyncio.sleep(1)
        await sent.delete()
        await copy.delete()
        file_id = state.get(client.me.id, "PMMEDIA").get("file_id")
        type = state.get(client.me.id, "PMMEDIA").get("type")
        media = {"type": type, "file_id": file_id}
        await dB.set_var(client.me.id, "PMMEDIA", media)
        return await proses.edit(
            f"{em.sukses}**PMPermit media set to: [this media]({rep.link})",
            disable_web_page_preview=True,
        )

    elif variable.lower() == "teks":
        if value.lower() == "reset":
            await dB.remove_var(client.me.id, "PMTEXT")
            return await proses.edit(
                f"{em.sukses}**PMPermit text has been reset to default.**"
            )
        if message.reply_to_message:
            pice = client.new_arg(message)
        else:
            pice = value
        await dB.set_var(client.me.id, "PMTEXT", pice)
        return await proses.edit(f"{em.sukses}**PMPermit text set to: {pice}.**")
    elif variable.lower() == "warn":
        if value.lower() == "reset":
            await dB.remove_var(client.me.id, "PMLIMIT")
            return await proses.edit(
                f"{em.sukses}**PMPermit warn has been reset to default.**"
            )
        if not message.reply_to_message:
            pice = value
        else:
            pice = rep.text
        if not pice.isnumeric():
            return await proses.edit(f"{em.gagal}**Please give warn type numeric.**")
        await dB.set_var(client.me.id, "PMLIMIT", pice)
        return await proses.edit(f"{em.sukses}**PMPermit warn set to: {pice}.**")
    elif variable.lower() == "get":
        if value.lower() == "teks":
            txt = await dB.get_var(client.me.id, "PMTEXT")
            pmtext = txt if txt else DEFAULT_TEXT
            await message.reply(
                f"**PMPermit text:**\n\n`{pmtext}`",
                disable_web_page_preview=True,
                parse_mode=ParseMode.DISABLED,
            )
            return await proses.delete()
        elif value.lower() == "warn":
            lmt = await dB.get_var(client.me.id, "PMLIMIT")
            lmt if lmt else LIMIT
            return await proses.edit(f"{em.sukses}**PMPermit warn: `{lmt}`.**")
        elif value.lower() == "media":
            pick = await dB.get_var(client.me.id, "PMMEDIA")
            if pick:
                return await proses.edit(f"{em.sukses}**PMPermit media: `{pick}`**")
            else:
                return await proses.edit(
                    f"{em.gagal}**PMPermit media already disable.**"
                )
        elif value.lower() == "status":
            sts = await dB.get_var(client.me.id, "PMPERMIT")
            if sts:
                return await proses.edit(f"{em.sukses}**PMPermit status:** `{sts}`")
            else:
                return await proses.edit(f"{em.gagal}**PMPermit already disable.**")
        else:
            return await proses.edit(
                f"{em.gagal}**Query not found, please read help!**"
            )
    else:
        return await proses.edit(f"{em.gagal}**Query not found, please read help!**")


@CMD.UBOT("ok")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pm_ok = await dB.get_list_from_var(client.me.id, "PM_OKE")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if message.reply_to_message:
            dia = message.reply_to_message.from_user.id
        else:
            return await message.delete()
    elif chat_type == ChatType.PRIVATE:
        dia = message.chat.id
    else:
        return await message.delete()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_}**")
    getc_pm_warns = await dB.get_var(client.me.id, "PMLIMIT")
    custom_pm_warns = getc_pm_warns if getc_pm_warns else LIMIT
    if dia in pm_ok:
        return await proses.edit(f"{em.sukses}**User already approved.**")
    try:
        async for uh in client.get_chat_history(dia, limit=int(custom_pm_warns)):
            if uh.reply_markup:
                await uh.delete()
            else:
                try:
                    await client.delete_messages(dia, message_ids=flood[dia])
                except KeyError:
                    pass
    except Exception as er:
        logger.error(f"ERROR: {str(er)}")
    await dB.add_to_var(client.me.id, "PM_OKE", dia)
    return await proses.edit(f"{em.sukses}**User approved to send message.**")


@CMD.UBOT("no")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()
    pm_ok = await dB.get_list_from_var(client.me.id, "PM_OKE")
    proses = await message.reply(f"{em.proses}**{proses_}**")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            return await message.delete()
    elif chat_type == ChatType.PRIVATE:
        user_id = message.chat.id
    else:
        return await message.delete()

    if user_id not in pm_ok:
        return await proses.edit(
            f"{em.gagal}**User already disapproved to send message**"
        )
    await dB.remove_from_var(client.me.id, "PM_OKE", user_id)
    return await proses.edit(f"{em.sukses}**User disapproved to send message**")


@CMD.NO_CMD("PMPERMIT", navy)
@CMD.capture_err
async def _(client, message):
    em = Emoji(client)
    await em.get()
    gw = client.me.id
    dia = message.from_user

    pm_oke = await dB.get_list_from_var(client.me.id, "PM_OKE")
    ong = await dB.get_var(gw, "PMPERMIT")
    if not ong or dia.id in pm_oke:
        return
    if dia.is_fake or dia.is_scam:
        return await client.block_user(dia.id)
    if dia.is_support or dia.is_verified or dia.is_self:
        return
    if dia.id in SUDO_OWNERS:
        try:
            await client.send_message(
                dia.id,
                f"<b>Approved {dia.mention} has Owner {BOT_NAME}!!</b>",
                parse_mode=ParseMode.HTML,
            )
            await dB.add_to_var(client.me.id, "PM_OKE", dia.id)
        except BaseException:
            pass
        return
    pmtok = await dB.get_var(gw, "PMTEXT")
    pm_text = pmtok if pmtok else DEFAULT_TEXT
    pm_warns = await dB.get_var(gw, "PMLIMIT") or LIMIT
    async for aks in client.get_chat_history(dia.id, limit=int(pm_warns)):
        if aks.reply_markup:
            await aks.delete()
    if str(dia.id) in flood:
        flood[str(dia.id)] += 1
    else:
        flood[str(dia.id)] = 1
    if flood[str(dia.id)] > int(pm_warns):
        del flood[str(dia.id)]
        await message.reply_text(
            f"{em.sukses}**SPAM DETECTED, {em.block}BLOCKED USER AUTOMATICALLY!**"
        )
        return await client.block_user(dia.id)
    state.set(gw, dia.id, flood[str(dia.id)])
    full = f"<a href=tg://user?id={dia.id}>{dia.first_name} {dia.last_name or ''}</a>"
    await dB.add_userdata(
        dia.id, dia.first_name, dia.last_name, dia.username, dia.mention, full, dia.id
    )
    try:
        query = f"pmpermit_inline {str(dia.id)}"
        await ButtonUtils.send_inline_bot_result(
            message, dia.id, bot.me.username, query
        )
        xx = state.get(client.me.id, query)
        flood2[str(dia.id)] = int(xx["_id"])
        return
    except Exception:
        media = await dB.get_var(gw, "PMMEDIA")
        teks, button = ButtonUtils.parse_msg_buttons(pm_text)
        tekss = await Tools.escape_tag(client, dia.id, teks, Tools.parse_words)
        if media:
            type = media["type"]
            file_id = media["file_id"]
            if type == "video":
                await bot.send_video(client.me.id, file_id)
            elif type == "photo":
                await bot.send_photo(client.me.id, file_id)
            async for copy_msg in client.search_messages(bot.id, limit=1):
                rplied_msg = await copy_msg.copy(
                    dia.id,
                    caption=INLINE_WARN.format(tekss, flood[str(dia.id)], pm_warns),
                )
                break
        else:
            rplied_msg = await message.reply(
                INLINE_WARN.format(tekss, flood[str(dia.id)], pm_warns)
            )
        flood2[str(dia.id)] = rplied_msg.id
        return
