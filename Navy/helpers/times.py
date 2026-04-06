# @TomiX
import asyncio
from time import time as waktunya
from pyrogram.errors import FloodWait
from Navy import bot, navy


start_time = waktunya()


async def get_time(seconds):
    count = 0
    up_time = ""
    time_list = []

    time_suffix_list = [
        "s",
        "m",
        "h",
        "d",
        "w",
        "m",
        "y",
    ]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        up_time += time_list.pop() + ":"

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time


async def put_cleanmode(chat_id, message_id):
    if chat_id not in cleanmode:
        cleanmode[chat_id] = []
    time_now = datetime.now()
    put = {
        "msg_id": message_id,
        "timer_after": time_now + timedelta(minutes=1),
    }
    cleanmode[chat_id].append(put)


async def auto_clean(client):
    while not await asyncio.sleep(5):
        try:
            for chat_id in cleanmode:
                if not dB.is_cleanmode_on(chat_id):
                    continue
                for x in cleanmode[chat_id]:
                    if datetime.now() <= x["timer_after"]:
                        continue
                    try:
                        await client.delete_messages(chat_id, x["msg_id"])
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        await client.delete_messages(chat_id, x["msg_id"])
                    except:
                        continue
        except:
            continue