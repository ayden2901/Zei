import asyncio
from Navy import bot
from Navy.database import dB


async def SangMataTask():
    """Task global untuk cek status ON/OFF tiap grup"""
    print("[SANGMATA] Task berjalan")
    last_status = {}  # cache status grup

    while True:
        try:
            groups = await dB.get_list_from_var("BOT_ID", "GROUPS")
            if not groups:
                await asyncio.sleep(10)
                continue

            for chat_id in groups:
                status = await dB.get_var(chat_id, "STATUS_SG") or "OFF"
                prev = last_status.get(chat_id)

                # Update cache & print status cuma kalau berubah
                if prev != status:
                    print(f"[SANGMATA] Grup {chat_id} => {'ON' if status=='ON' else 'OFF'}")
                    last_status[chat_id] = status

                if status == "ON":
                    await run_sangmata(chat_id)
                else:
                   
                    continue

        except Exception as e:
            print(f"[SANGMATA TASK ERROR] {e}")

        await asyncio.sleep(1800)