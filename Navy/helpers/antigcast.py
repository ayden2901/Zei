import asyncio
from Navy.database import dB

_last_status = {}

async def AntiGcast():
    global _last_status

    print("[ANTIGCAST] Task AntiGcast berjalan")

    while True:
        try:
            status_dict = await dB.get_antigcast_status()

            if not status_dict:
                await asyncio.sleep(10)
                continue

            for chat_id, status in status_dict.items():

                prev_status = _last_status.get(chat_id)

                # hanya print jika status berubah
                if prev_status != status:
                    if status:
                        print(f"[ANTIGCAST] AKTIF di chat {chat_id}")
                    else:
                        print(f"[ANTIGCAST] NONAKTIF di chat {chat_id}")

                    _last_status[chat_id] = status

        except Exception as e:
            print(f"[ANTIGCAST ERROR] {e}")

        await asyncio.sleep(10)