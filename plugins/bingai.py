import os
import shutil
import traceback

import aiofiles
import aiohttp
from pyrogram.types import InputMediaPhoto

from config import API_MAELYN, COOKIE_BING
from Navy.helpers import CMD, Emoji, Tools
from Navy.logger import logger

__MODULES__ = "ʙɪɴɢᴀɪ"
__HELP__ = """<blockquote>Command Help **Bingai**</blockquote>

<blockquote>**Generate image with bingai**</blockquote>
    **You can generate image ai with Bingai from prompt command**
        `{0}bingai` (prompt)
    
<b>   {1}</b>
"""


async def generate_images(prompt):
    url = f"https://api.maelyn.tech/api/bing/createimage?cookie={COOKIE_BING}&prompt={prompt}&apikey={API_MAELYN}"
    result = await Tools.fetch.get(url)
    if result.status_code == 200:
        data = result.json()["result"]
        return data
    else:
        return f"{result.status_code}"


async def gen_bing_ai2(folder_name, prompt):
    try:
        os.makedirs(folder_name, exist_ok=True)

        results = await generate_images(prompt)

        image_paths = []
        unique_urls = set()

        async with aiohttp.ClientSession() as session:
            for url in results:

                if url not in unique_urls:
                    unique_urls.add(url)

                    logger.info(f"Url: {url}")
                    file_path = os.path.join(
                        folder_name, f"genai2_{len(image_paths) + 1}.jpg"
                    )

                    async with session.get(url) as response:
                        if response.status == 200:
                            async with aiofiles.open(file_path, "wb") as f:
                                await f.write(await response.read())
                            image_paths.append(file_path)

                    if len(image_paths) == 4:
                        break

        return folder_name, image_paths

    except Exception as e:
        logger.error(f"Error in gen_bing_ai: {traceback.format_exc()}")
        return folder_name, []


@CMD.UBOT("bingai")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    prompt = client.get_text(message)

    if not prompt:
        return await message.reply(
            f"{emo.gagal}<b>Give the query you want to make!\n\nExample: \n<code>{message.text.split()[0]} Gambarkan lelaki Jepang tampan sedang duduk di bangku, mengenakan hoodie hitam dengan tulisan 'Kynan only Me' di bagian depan dan kacamata, sambil menghisap rokok dengan sikap santai. Latar belakang menampilkan hutan hujan yang rimbun, dengan cahaya lembut yang menerobos di antara dedaunan, menciptakan suasana tenang dan memikat. Tambahkan efek asap rokok yang melayang di udara, memberikan nuansa misterius pada gambar. Kualitas gambar harus tinggi (4k) dengan detail yang tajam dan warna alami yang kaya || Hindari elemen yang terlalu cerah, ekspresi wajah yang berlebihan, dan latar belakang yang terlalu ramai yang dapat mengalihkan perhatian dari sosok utama.</code></b>"
        )
    pros = await message.reply(
        f"{emo.proses}<b>Proses generate <code>{prompt}</code> ..</b>"
    )
    folder_name = f"downloads/{client.me.id}/"
    try:
        folder_name, imgs = await gen_bing_ai2(folder_name, prompt)
        if imgs:
            media_group = []
            for img in imgs:
                if os.path.exists(img):
                    caption = f"{emo.sukses}<b>Successfully generate image:</b>"
                    media_group.append(InputMediaPhoto(media=img, caption=caption))

            if media_group:
                await client.send_media_group(
                    chat_id=message.chat.id,
                    media=media_group,
                    reply_to_message_id=message.id,
                )

            await pros.delete()

            if folder_name:
                shutil.rmtree(folder_name)
            for img in imgs:
                if os.path.exists(img):
                    os.remove(img)
        else:
            return await pros.edit(
                f"{emo.gagal}<b>Images are not found or failed generate images.</b>"
            )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Bing error: {traceback.format_exc()}")
        if "Failed to decode" in error_message:
            return await pros.edit(
                f"{emo.gagal}<b>Failed generate image.Please repeat again...</b>"
            )
        else:
            return await pros.edit(
                f"{emo.gagal}<b>Error:</b>\n <code>{error_message}</code>"
            )
    return
