from Navy import *
from pyrogram.raw.functions.contacts import AddContact
from Navy.helpers import CMD, Emoji, Tools


__MODULES__ = "sᴀᴠᴇ ᴋᴏɴᴛᴀᴋ"
__HELP__ = """<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ **sᴀᴠᴇ ᴋᴏɴᴛᴀᴋ**</u>

<blockquote><b>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ **sᴀᴠᴇ ᴋᴏɴᴛᴀᴋ**</b>
     ➢ `{0}addkon` [ʀᴇᴘʟʏ]</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("addkon")
async def save_contact(client, message):
    em = Emoji(client)
    await em.get()
    user_id = None
    first_name = None
    last_name = ""

    # Check if the message is a reply to another message
    reply_message = message.reply_to_message
    if reply_message and reply_message.from_user:
        user = reply_message.from_user
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name or ""
    else:
        # Check if the message contains a user ID argument
        args = message.command
        if len(args) < 2:
            return await message.reply_text(f"<b>{em.gagal} Please reply to the user or enter the user ID to save the contact.</b>")
        
        user_id = int(args[1])
        
        # Fetch user details using user ID
        try:
            user = await client.get_users(user_id)
            first_name = user.first_name
            last_name = user.last_name or ""
        except Exception as e:
            return await message.reply_text(f"<b>{em.gagal} There is an error: {e}</b>")

    # Resolve the peer ID of the user
    chat_id = await client.resolve_peer(user_id)

    # Attempt to add the contact
    try:
        response = await client.invoke(
            AddContact(
                id=chat_id,
                first_name=first_name,
                last_name=last_name,
                phone=""
            )
        )
        # Check if the contact was added successfully
        if response.users and response.users[0].contact:
            await message.reply_text(f"<b>{em.sukses} Successfully saved contact with name {first_name}</b>")
        else:
            await message.reply_text(f"<b>{em.gagal} An error occurred while saving the contact.</b>")
    except Exception as e:
        await message.reply_text(f"<b>{em.gagal} There is an error: {e}</b>")
