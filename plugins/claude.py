from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ᴄʟᴀᴜᴅᴇ"
__HELP__ = """<blockquote>Command Help **Claude**</blockquote>

<blockquote>**Chat with claude** </blockquote>
    **You can chat with claude ai**
        `{0}claude` (prompt)
    
<blockquote>**Stop converstation**</blockquote>
    **Stop converstation chat**
        `{0}stop claude`

<b>   {1}</b>
"""


CONVERSATIONS = {}


@CMD.UBOT("claude")
async def ai_chat(client, message):
    em = Emoji(client)
    await em.get()

    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(
            f"{em.gagal} **Please reply to message text or give message!**"
        )

    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in CONVERSATIONS:
        CONVERSATIONS[user_id] = []

    question = client.get_text(message)

    while True:
        proses_ = await em.get_costum_text()
        pros = await message.reply(f"{em.proses}**{proses_[4]}**")

        try:
            CONVERSATIONS[user_id].append(question)

            url = f"https://api.maelyn.tech/api/claude?q={question}&apikey={API_MAELYN}"
            response = await Tools.fetch.get(url)
            if response.status_code == 200:
                data = response.json()
                output = data["result"]
                CONVERSATIONS[user_id].append(output)

                if len(CONVERSATIONS[user_id]) > 20:
                    CONVERSATIONS[user_id] = (
                        CONVERSATIONS[user_id][:2] + CONVERSATIONS[user_id][-18:]
                    )
                await pros.delete()
                if len(output) > 4096:
                    result = await Tools.paste(output)
                    next_message = await client.ask(
                        chat_id=chat_id,
                        text=f"{em.sukses}**Message too long, upload to pastebin. Question:\n{question}\n\nAnswer:\n**{result}\n\nType** `stop claude` **to end the conversation.**",
                        disable_web_page_preview=True,
                        timeout=300,
                    )
                else:
                    result = output
                    next_message = await client.ask(
                        chat_id=chat_id,
                        text=f"{em.sukses}**Question:\n{question}\n\nAnswer:\n**{output}\n\nType** `stop claude` **to end the conversation.**",
                        timeout=300,
                    )
                try:
                    if next_message.text.lower() == "stop claude":
                        del CONVERSATIONS[user_id]
                        await next_message.reply(f"{em.sukses}**Conversation ended.**")
                        break

                    question = next_message.text

                except TimeoutError:
                    del CONVERSATIONS[user_id]
                    await next_message.reply(
                        f"{em.gagal}**Conversation timed out after 5 minutes of inactivity.**"
                    )
                    break
            else:
                await pros.edit(
                    f"{em.gagal}**API Error:** Status code {response.status_code}"
                )
                break

        except Exception as er:
            if user_id in CONVERSATIONS:
                del CONVERSATIONS[user_id]
            await pros.edit(f"{em.gagal}**ERROR:** {str(er)}")
            break
