from pyrogram.errors import PeerIdInvalid

from Navy.database import dB
from Navy.helpers import CMD, Emoji

__MODULES__ = "sᴜᴅᴏ ᴜsᴇʀ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>sᴜᴅᴏ ᴜsᴇʀ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>sᴜᴅᴏ ᴜsᴇʀ</b>
    ➢ `{0}addsudo` [ᴜsɴ/ʀᴇᴘʟʏ ᴜsᴇʀ]</blockquote>
<blockquote>❖ ʟɪʜᴀᴛ ᴅᴀғᴛᴀʀ <b>sᴜᴅᴏ ᴜsᴇʀ</b>
    ➢ `{0}sudolist`</blockquote>
<blockquote>❖ ʜᴀᴘᴜs ᴅᴀғᴛᴀʀ <b>sᴜᴅᴏ ᴜsᴇʀ</b>
    ➢ `{0}delsudo` [ᴜsɴ/ʀᴇᴘʟʏ ᴜsᴇʀ]
    ➢ `{0}delsudo all`</blockquote>

<b>~    {1}</b>
"""


@CMD.UBOT("addsudo")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_}</b>")
    user_id = await client.extract_user(message)
    if not user_id:
        return await pros.edit(
            f"{emo.gagal}<b>Please reply to message from user or give username</b>"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:\n\n<code>{error}</code></b>")

    sudo_users = await dB.get_list_from_var(client.me.id, "SUDOERS")

    if user.id in sudo_users:
        return await pros.edit(
            f"{emo.gagal}<b>[{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) Already in sudoers.</b>"
        )

    try:
        added = client.add_sudoers(client.me.id, user.id)
        if not added:
            return await pros.edit(f"{emo.gagal}<b>Failed to add sudo user.</b>")
        await dB.add_to_var(client.me.id, "SUDOERS", user.id)
        return await pros.edit(
            f"{emo.sukses}<b>[{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) Succesfully add to sudo users.</b>"
        )
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:\n\n<code>{error}</code></b>")


@CMD.UBOT("delsudo")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_}</b>")
    sudo_users = await dB.get_list_from_var(client.me.id, "SUDOERS")

    if len(message.command) > 1 and message.command[1] == "all":
        for user in sudo_users:
            await dB.remove_from_var(client.me.id, "SUDOERS", user)
        return await pros.edit(f"{emo.sukses}<b>Successfully deleted all sudoers.</b>")

    user_id = await client.extract_user(message)
    if not user_id:
        return await pros.edit(
            f"{emo.gagal}<b>Please reply to a message from the user or provide a username.</b>"
        )
    if user_id not in sudo_users:
        return await pros.edit(f"{emo.gagal}<b>User {user_id} is not in sudoers.</b>")

    try:
        deleted = client.remove_sudoers(client.me.id, user_id)
        if not deleted:
            return await pros.edit(
                f"{emo.gagal}<b>Failed to delete user {user_id} from sudoers.</b>"
            )
        await dB.remove_from_var(client.me.id, "SUDOERS", user_id)
        return await pros.edit(
            f"{emo.sukses}<b>Successfully deleted user {user_id} from sudoers.</b>"
        )
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:\n\n<code>{error}</code></b>")


@CMD.UBOT("sudolist|listsudo")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_}</b>")

    sudo_users = await dB.get_list_from_var(client.me.id, "SUDOERS")

    if not sudo_users:
        return await pros.edit(f"{emo.gagal}<b>You dont have sudoers.</b>")

    sudo_list = []
    teks = "<b>❒ List of Sudoers:</b>\n"

    for index, user_id in enumerate(sudo_users, 1):
        try:
            user = await client.get_users(int(user_id))
            user_name = f"{user.first_name} {user.last_name or ''}".strip()

            prefix = "┖" if index == len(sudo_users) else "┣"
            sudo_list.append(
                f"{prefix} [{user_name}](tg://user?id={user_id}) | <code>{user_id}</code>"
            )
        except PeerIdInvalid:
            await dB.remove_from_var(client.me.id, "SUDOERS", user_id)
        except Exception as e:
            return await pros.edit(
                f"{emo.gagal}<b>Error when get sudoers:</b>\n<code>{str(e)}</code>"
            )

    if not sudo_list:
        return await pros.edit(
            f"{emo.gagal}<b>All user has been deleted because error when get sudoers.</b>"
        )
    response = teks + "\n".join(sudo_list)
    return await pros.edit(f"<b>{response}</b>")
