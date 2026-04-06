import asyncio
import os
import aiohttp
import requests
from google import genai
from pyrogram.enums import ChatAction, ParseMode
import html

from pyrogram.errors import ChatWriteForbidden
from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "ɢᴇᴍɪɴɪ"
__HELP__ = """<u>📋 ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>ɢᴇᴍɪɴɪ</b></u>

<blockquote>❖ ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>ɢᴇᴍɪɴɪ</b>
    ➢ `{0}gemini` [ᴘʀᴏᴍᴘᴛ]</blockquote>

<b>   {1}</b>
"""


async def gemini_botcahx(client, text, username="client star"):
    em = Emoji(client)
    await em.get()
    try:
        url = "https://api.botcahx.eu.org/api/search/openai-custom"

        messages = [
            {
                "role": "system",
                "content": f"Kamu adalah asisten AI yang ramah. Kamu sedang berbicara dengan {username}. Panggil dia dengan namanya."
            },
            {
                "role": "user",
                "content": text
            }
        ]

        payload = {
            "message": messages,
            "apikey": API_BOTCHAX
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=60) as resp:
                if resp.status != 200:
                    return f"API Error: {resp.status}"

                try:
                    data = await resp.json()
                except:
                    return await resp.text()

        return str(
            data.get("result")
            or data.get("message")
            or data.get("response")
            or data
        )

    except Exception as e:
        return f"{em.gagal}Error generating text:\n{str(e)}"

async def image_to_prompt(image_url):
    try:
        endpoint = "https://api.botcahx.eu.org/api/tools/img2prompt"
        params = {
            "url": image_url,
            "apikey": API_BOTCHAX
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params, timeout=60) as resp:

                text = await resp.text()

                if resp.status != 200:
                    print("IMG2PROMPT ERROR:", text)
                    return None
                try:
                    data = await resp.json()
                    return (
                        data.get("result")
                        or data.get("prompt")
                        or data.get("message")
                        or str(data)
                    )
                except:
                    return text.strip()

    except Exception as e:
        print("IMG2PROMPT EXCEPTION:", e)
        return None


# ==============================
# 🔥 SEND RESPONSE
# ==============================

async def mari_kirim(client, message, query):
    em = Emoji(client)
    await em.get()

    try:
        chat_id = message.chat.id

        if message.from_user:
            username = (
                message.from_user.first_name
                or message.from_user.username
                or "client star"
            )
        else:
            username = "client star"

        await client.send_chat_action(chat_id, ChatAction.TYPING)

        respon = await gemini_botcahx(client, query, username)

        if len(respon) > 4096:
            with open("gemini.txt", "w", encoding="utf-8") as file:
                file.write(respon)

            await client.send_document(
                chat_id,
                "gemini.txt",
                reply_to_message_id=message.id
            )
            os.remove("gemini.txt")

        else:
            ids = f"<blockquote>{em.pin}ᴄʀᴇᴀᴛᴇᴅ ʙʏ : @StarBotDevs</blockquote>"
            safe_respon = html.escape(respon)
            await message.reply_text(
                f"<blockquote>{em.sukses}Berikut Adalah Hasil Prompt:</blockquote>\n"
                f"<blockquote expandable><code>{safe_respon}</code></blockquote>\n"
                f"{ids}",
                reply_to_message_id=message.id,
                parse_mode=ParseMode.HTML
            )

    except ChatWriteForbidden:
        return


# ==============================
# 🔥 COMMAND GEMINI
# ==============================

@CMD.UBOT("gemini")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(
            f"{em.gagal} **Reply teks atau foto!**"
        )

    proses_ = await em.get_costum_text()
    pros = await message.reply(f"{em.proses} **{proses_[4]}**")

    # ==========================
    # 📸 REPLY FOTO FLOW
    # ==========================
    if message.reply_to_message and message.reply_to_message.photo:

        image_url = await Tools.upload_media(message)
        if not image_url:
            return await pros.edit("❌ Gagal upload gambar.")

        img_prompt = await image_to_prompt(image_url)
        if not img_prompt:
            return await pros.edit(f"❌ Gagal generate prompt.\nURL: {image_url}")

        final_prompt = final_prompt = f"""
You are an expert AI prompt engineer specializing in high-end image generation.

Transform the description below into a single, highly refined, production-quality AI image generation prompt.

Strict Requirements:
- Output must be ONE single paragraph.
- English language only.
- No explanations.
- Optimized for Stable Diffusion, Midjourney, and SDXL.
- Include subject details, environment, composition, camera angle, lens type, lighting setup, depth of field, texture detail, color grading, atmosphere, and render quality.
- Add professional photography or cinematic terminology when appropriate.
- Make it visually rich, precise, and descriptive.
- Enhance details creatively while staying true to the original concept.
- Do NOT repeat the instructions.

Description:
{img_prompt}
"""

        await mari_kirim(client, message, final_prompt)
        return await pros.delete()

    # ==========================
    # 💬 TEXT FLOW
    # ==========================
    reply_text = client.get_text(message)

    await mari_kirim(client, message, reply_text)
    return await pros.delete()


"""
genai.configure(api_key=API_GEMINI)


def gemini(text):
    try:
        generation_config = {
            "temperature": 0.6,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

        # ✅ MODEL TERBARU
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        response = model.generate_content(text)

        if response and hasattr(response, "text"):
            return response.text.strip()

        return "Tidak ada respon dari Gemini."

    except Exception as e:
        return f"❌ Error generating text:\n{str(e)}"


async def mari_kirim(client, message, query):
    em = Emoji(client)
    await em.get()
    try:
        chat_id = message.chat.id
        respon = await asyncio.to_thread(gemini, query)
        await message._client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(2)
        if len(respon) > 4096:
            with open("gemini.txt", "wb") as file:
                file.write(respon.encode("utf-8"))
            await message._client.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            await asyncio.sleep(2)
            await message._client.send_document(
                chat_id, "gemini.txt", reply_to_message_id=message.id
            )
            os.remove("gemini.txt")
            return await message._client.send_chat_action(chat_id, ChatAction.CANCEL)
        else:
            await message.reply_text(
                f"{em.sukses}**{respon}**", reply_to_message_id=message.id
            )
        return await message._client.send_chat_action(chat_id, ChatAction.CANCEL)
    except ChatWriteForbidden:
        return
"""
