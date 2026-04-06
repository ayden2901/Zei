from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Message, Tools

__MODULES__ = "ᴘᴀʏs ᴀɪ"
__HELP__ = """<blockquote>Command Help **Pays-Ai**</blockquote>

<blockquote>**Chat with pays-id**</blockquote>
    **You can chat to pays-ai**
        `{0}pays` (prompt)

<blockquote>**Stop converstation**</blockquote>
    **Stop the converstation pays-ai**
        `{0}stop pays`

<b>   {1}</b>
"""


CONVERSATIONS = {}


@CMD.UBOT("pays|ai")
async def ai_chat(client, message):
    em = Emoji(client)
    await em.get()

    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(
            f"{em.gagal} **Please reply to message text or give message!**"
        )

    chat_id = message.chat.id
    user_id = (
        message.from_user.id
       if message.from_user
       else (message.sender_chat.id if message.sender_chat else message.chat.id)
    )

    if user_id not in CONVERSATIONS:
        CONVERSATIONS[user_id] = [
            {
                "role": "system",
                "content": "Kamu adalah asisten paling canggih yang berbahasa Indonesia gaul, dan jangan gunakan bahasa inggris sebelum saya memulai duluan.",
            },
            {
                "role": "assistant",
                "content": "Kamu adalah asisten paling canggih yang berbahasa Indonesia gaul",
            },
        ]

    question = client.get_text(message)

    while True:
        proses_ = await em.get_costum_text()
        pros = await message.reply(f"{em.proses}**{proses_[4]}**")

        try:
            CONVERSATIONS[user_id].append({"role": "user", "content": question})

            url = "https://api.botcahx.eu.org/api/search/openai-custom"
            payload = {"message": CONVERSATIONS[user_id], "apikey": API_BOTCHAX}

            response = await Tools.fetch.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                output = data["result"]

                CONVERSATIONS[user_id].append({"role": "assistant", "content": output})

                if len(CONVERSATIONS[user_id]) > 20:
                    CONVERSATIONS[user_id] = (
                        CONVERSATIONS[user_id][:2] + CONVERSATIONS[user_id][-18:]
                    )

                await pros.delete()

                if len(output) > 4096:
                    result = await Tools.paste(output)
                    next_message = await client.ask(
                        chat_id=chat_id,
                        text=f"{em.sukses}<b>Message too long, upload to pastebin</b>\n<b>Question:\n<blockquote>{question}</blockquote>\n\nAnswer:\n</b><blockquote>{result}</blockquote>\n\n<b>Type <code>stop mili</code> to end the conversation.</b>",
                        disable_web_page_preview=True,
                        timeout=300,
                        reply_to_message_id=Message.ReplyCheck(message),
                    )
                else:
                    result = output
                    next_message = await client.ask(
                        chat_id=chat_id,
                        text=f"{em.sukses}<b>Question:\n<blockquote>{question}</blockquote>\n\nAnswer:\n</b><blockquote>{result}</blockquote>\n\n<b>Type <code>stop pays</code> to end the conversation.</b>",
                        timeout=300,
                        reply_to_message_id=Message.ReplyCheck(message),
                    )
                try:
                    if next_message.text.lower() == "stop pays":
                        del CONVERSATIONS[user_id]
                        await next_message.reply(
                            f"{em.sukses}**Conversation ended.**",
                            reply_to_message_id=Message.ReplyCheck(message),
                        )
                        break

                    question = next_message.text

                except TimeoutError:
                    del CONVERSATIONS[user_id]
                    await next_message.reply(
                        f"{em.gagal}**Conversation timed out after 5 minutes of inactivity.**",
                        reply_to_message_id=Message.ReplyCheck(message),
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


@CMD.UBOT("clearpays")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    user_id = message.from_user.id
    if user_id in CONVERSATIONS:
        del CONVERSATIONS[user_id]
        await message.reply(f"{em.sukses}**AI conversation history cleared.**")
    else:
        await message.reply(f"{em.gagal}**No active AI conversation found.**")
