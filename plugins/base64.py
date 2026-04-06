import requests
import base64
from Navy.helpers import CMD, Emoji
from Navy import bot, navy



def _(text):
    return text

async def process_message(client, message, text: str, decode: bool = False):
    """
    Proses encode/decode base64.
    """
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    if not text:
        return await message.reply("❌ Silakan reply pesan atau masukkan teks untuk di encode/decode.")

    try:
        if decode:
            # Base64 decode
            decoded = base64.b64decode(text.encode()).decode("utf-8")
            return await message.reply(f"{sukses_} Decode berhasil:\n<code>{decoded}</code>")
        else:
            # Base64 encode
            encoded = base64.b64encode(text.encode()).decode("utf-8")
            return await message.reply(f"{sukses_} Encode berhasil:\n<code>{encoded}</code>")
    except Exception as e:
        return await message.reply(f"❌ Terjadi error: {e}")

# ==================== PERINTAH UBOT ====================
@CMD.UBOT("encode")
async def base64_encode(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    pros = await message.reply(f"{em.proses}{proses_}")

    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif hasattr(message, "command") and len(message.command) > 1:
        text = " ".join(message.command[1:])
    else:
        await pros.delete()
        return await message.reply("❌ Silakan reply pesan atau masukkan teks untuk di encode.")

    await process_message(client, message, text, decode=False)
    await pros.delete()

@CMD.UBOT("decode")
async def base64_decode(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_, keterangan_ = await em.get_costum_text()

    pros = await message.reply(f"{em.proses}{proses_}")

    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif hasattr(message, "command") and len(message.command) > 1:
        text = " ".join(message.command[1:])
    else:
        await pros.delete()
        return await message.reply("❌ Silakan reply pesan atau masukkan teks untuk di decode.")

    await process_message(client, message, text, decode=True)
    await pros.delete()