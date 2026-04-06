__MODULES__ = "ᴍᴀɪʟ"
__HELP__ = """<blockquote>Command Help **Temp Mail**</blockquote>

<blockquote>**Generate mail**</blockquote>
    **You can generate fake email from this command**
        `{0}mail gen`

<blockquote>**Get otp from mail**</blockquote>
    **After you generate fake mail, get otp from this command**
        `{0}mail otp` (id)

<blockquote>**View list mail**</blockquote>
    **You can view list email after you generated**
        `{0}mail list`
 
<b>   {1}</b>
"""


from config import API_MAELYN
from Navy.database import dB
from Navy.helpers import CMD, Emoji, Tools


@CMD.UBOT("mail")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    command = client.get_text(message)
    if not command:
        return await prs.edit(
            f"{em.gagal}**Please give query. Example: `{message.text.split()[0]} gen` (for generate mail) or `{message.text.split()[0]} otp` (for get otp)"
        )
    try:
        if message.command[1] == "gen":
            url = f"https://api.maelyn.tech/api/tempmail/generate?apikey={API_MAELYN}"
            response = await Tools.fetch.get(url)
            if response.status_code == 200:
                data = response.json()["result"]
                await dB.set_var(client.me.id, "ID_MAIL", data.get("id_inbox"))
                return await prs.edit(
                    f"{em.sukses}**Here your temp mail**\n\n**Email**: {data.get('email')}\n**ID**: `{data.get('id_inbox')}`"
                )
            else:
                return await prs.edit(f"{em.gagal}**ERROR**: {response.status_code}")
        elif message.command[1] == "otp":
            if len(message.command) > 2:
                ids = message.command[2]
                url = f"https://api.maelyn.tech/api/tempmail/inbox?id={ids}&apikey={API_MAELYN}"
                response = await Tools.fetch.get(url)
                if response.status_code == 200:
                    data = response.json()["result"]
                    inbox_data = data["inbox"]

                    inbox_text = ""
                    if inbox_data:
                        for idx, mail in enumerate(inbox_data, 1):
                            inbox_text += f"\n - **Mail {idx}**:\n"
                            inbox_text += (
                                f"**Sender**: {mail.get('senderName', 'N/A')}\n"
                            )
                            inbox_text += f"**From**: {mail.get('from', 'N/A')}\n"
                            inbox_text += f"**Subject**: {mail.get('subject', 'N/A')}\n"
                            inbox_text += (
                                f"**Message**: {mail.get('textBody', 'N/A')}\n"
                            )
                            inbox_text += f"**Received**: <t:{int(mail.get('receivedAt', 0)/1000)}:F>\n"
                    else:
                        inbox_text = "[]"

                    return await prs.edit(
                        f"{em.sukses}**Email**: {data.get('email')}\n"
                        f"**ID**: `{data.get('id_inbox')}`\n"
                        f"**Inbox**: {inbox_text}"
                    )
                else:
                    return await prs.edit(
                        f"{em.gagal}**ERROR**: {response.status_code}"
                    )
            else:
                ids = await dB.get_var(client.me.id, "ID_MAIL")
                if not ids:
                    return await prs.edit(f"{em.gagal}**Please give id temp mail!!**")

                url = f"https://api.maelyn.tech/api/tempmail/inbox?id={str(ids)}&apikey={API_MAELYN}"
                response = await Tools.fetch.get(url)
                if response.status_code == 200:
                    data = response.json()["result"]
                    inbox_data = data["inbox"]

                    inbox_text = ""
                    if inbox_data:
                        for idx, mail in enumerate(inbox_data, 1):
                            inbox_text += f" - **Mail {idx}**:\n"
                            inbox_text += (
                                f"**Sender**: {mail.get('senderName', 'N/A')}\n"
                            )
                            inbox_text += f"**From**: {mail.get('from', 'N/A')}\n"
                            inbox_text += f"**Subject**: {mail.get('subject', 'N/A')}\n"
                            inbox_text += (
                                f"**Message**: {mail.get('textBody', 'N/A')}\n"
                            )
                            inbox_text += f"**Received**: <t:{int(mail.get('receivedAt', 0)/1000)}:F>\n"
                    else:
                        inbox_text = "[]"

                    return await prs.edit(
                        f"{em.sukses}**Email**: {data.get('email')}\n"
                        f"**ID**: `{data.get('id_inbox')}`\n"
                        f"**Inbox**: {inbox_text}"
                    )
                else:
                    return await prs.edit(
                        f"{em.gagal}**ERROR**: {response.status_code}"
                    )
        else:
            return await prs.edit(
                f"{em.gagal}**Please give query. Example: `{message.text.split()[0]} gen` (for generate mail) or `{message.text.split()[0]} otp` (for get otp)"
            )
    except Exception as er:
        return await prs.edit(f"{em.gagal}**ERROR**: {str(er)}")
