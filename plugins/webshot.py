from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ᴡᴇʙsʜᴏᴛ"
__HELP__ = """<blockquote>Command Help **Webshot** </blockquote>

<blockquote>**View webpage capture**</blockquote>
    **Get screenshot web from url**
        `{0}webss` (url)
    
<b>   {1}</b>
"""


@CMD.UBOT("webss")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()

    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please provide a valid link!**\n"
            f"Example: `{message.command[0]} https://youtube.com`"
        )

    url = message.text.split(None, 1)[1]

    if not url.startswith("http"):
        url = "https://" + url

    # mode full jika ada kata "full"
    full = "full" in message.text.lower()
    # mode mobile jika ada kata "mobile"
    mobile = "mobile" in message.text.lower()

    try:
        photo = await Tools.screen_web(url, full)
        if not photo:
            return await proses.edit(f"{em.gagal}**Failed to take screenshot!**")

        await proses.delete()
        upload = await message.reply(f"{em.proses}**Uploading screenshot...**")

        if full:
            await message.reply_document(photo)
        else:
            await message.reply_photo(photo)

        return await upload.delete()

    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** `{e}`")