import asyncio
import random

from Navy import navy
from Navy.helpers import CMD, Emoji, task

__MODULES__ = "ʀᴇᴀᴄᴛɪᴏɴ"
__HELP__ = """<blockquote>Command Help **Reaction** </blockquote>

<blockquote>**Reaction 1**</blockquote>
    **Give reactions to chat with costum emoji or random**
        `{0}react` (chatid) (emoji/random)

<blockquote>**Reaction 2**</blockquote>
    **Give many reactions to 1 message with active userbot**
        `{0}react2` (reply message) (emoji/random)

<blockquote>**Stop Reaction**</blockquote>
    **Stop task reaction with taskid**
        `{0}cancel` (taskid)

<b>   {1}</b>
"""

RANDOM_EMOJIS = [
    "😀",
    "😂",
    "😍",
    "😎",
    "😢",
    "😡",
    "👍",
    "👎",
    "🙏",
    "👏",
    "❤️",
    "🗿",
    "😭",
    "🔥",
]


@CMD.UBOT("react")
@CMD.FAKEDEV("react")
@CMD.DEV_CMD("react")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    sukses = 0
    failed = 0

    if len(message.command) not in [2, 3]:
        return await proses.edit(
            f"{em.gagal}**Please use format `{message.text.split()[0]}` [@username/chat_id] [emoji/random]**"
        )

    task_id = task.start_task()
    try:
        if len(message.command) == 3:
            chat_id = message.text.split()[1]
            emoji = message.text.split()[2]
        else:
            chat_id = message.chat.id
            emoji = message.text.split()[1]

        if emoji.lower() == "random":
            emoji = random.choice(RANDOM_EMOJIS)

        prefix = client.get_prefix(client.me.id)

        await proses.edit(
            f"{em.proses}<i>Task reaction running #<code>{task_id}</code>. Type <code>{prefix[0]}cancel {task_id}</code> to stop reaction!</i>"
        )
        async for m in client.get_chat_history(chat_id):
            if not task.is_active(task_id):
                return await proses.edit(
                    f"{em.gagal}**Task #{task_id} has been cancelled!**"
                )
            await asyncio.sleep(0.5)
            message_id = m.id
            try:
                for c in navy._ubot:
                    await asyncio.sleep(0.5)
                    await c.send_reaction(
                        chat_id=chat_id, message_id=message_id, emoji=emoji
                    )
                    sukses += 1
            except Exception:
                failed += 1
    except Exception as er:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}")
    finally:
        task.end_task(task_id)
    return await proses.edit(
        f"<b>{em.sukses}Succesfully send reaction to chat: {chat_id}, emoji: {emoji}.\n\nSucces: {sukses}, Failed: {failed}.</b>"
    )


@CMD.UBOT("react2")
@CMD.FAKEDEV("react2")
@CMD.DEV_CMD("react2")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    reply = message.reply_to_message or message
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    sukses = 0
    failed = 0

    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please use format `{message.text.split()[0]}` [emoji/random]**"
        )

    task_id = task.start_task()
    try:
        chat_id = message.chat.id
        emoji = message.text.split()[1]

        if emoji.lower() == "random":
            emoji = random.choice(RANDOM_EMOJIS)

        prefix = client.get_prefix(client.me.id)

        await proses.edit(
            f"{em.proses}<i>Task reaction running #<code>{task_id}</code>. Type <code>{prefix[0]}cancel {task_id}</code> to stop reaction!</i>"
        )
        try:
            for c in navy._ubot:
                message_id = reply.id
                await asyncio.sleep(0.5)
                await c.send_reaction(
                    chat_id=chat_id, message_id=message_id, emoji=emoji
                )
                sukses += 1
        except Exception:
            failed += 1
    except Exception as er:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}")
    finally:
        task.end_task(task_id)
    return await proses.edit(
        f"<b>{em.sukses}Succesfully send reaction to chat: {chat_id}\nEmoji: {emoji}\nSucces: {sukses}, Failed: {failed}.</b>"
    )
