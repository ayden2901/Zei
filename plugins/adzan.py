__MODULES__ = "ᴀᴅᴢᴀɴ"
__HELP__ = """<blockquote expandable>Command Help **Adzan**</blockquote>

<blockquote>**Get today's adzan schedule**</blockquote>
    **Get schedule adzan from country command**
        `{0}adzan` (country)
    
<b>   {1}</b>
"""


from config import API_MAELYN
from Navy.helpers import CMD, Emoji, Tools, animate_proses
from httpx import ConnectError, TimeoutException

@CMD.UBOT("adzan")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()

    proses = await animate_proses(message, em.proses)

    # Validasi command
    if len(message.command) < 3:
        return await prs.edit(
            f"{em.gagal}**Format salah!**\n"
            f"Contoh:\n`{message.command[0]} jakarta indonesia`"
        )

    city = message.command[1].lower()
    country = message.command[2].lower()

    url = (
        "https://api.aladhan.com/v1/timingsByCity"
        f"?city={city}&country={country}&method=11"
    )

    # Request API dengan handling error
    try:
        respon = await Tools.fetch.get(
            url,
            timeout=10,
            follow_redirects=True
        )
    except ConnectError:
        return await prs.edit(
            f"{em.gagal}**Gagal terhubung ke server adzan**"
        )
    except TimeoutException:
        return await prs.edit(
            f"{em.gagal}**Request timeout**"
        )
    except Exception as e:
        return await prs.edit(
            f"{em.gagal}**Error:** `{e}`"
        )

    if respon.status_code != 200:
        return await prs.edit(
            f"{em.gagal}**API Error:** `{respon.status_code}`"
        )

    # Parsing data API
    data = respon.json()["data"]
    timings = data["timings"]
    date = data["date"]
    meta = data["meta"]

    # Format pesan
    msg = (
        f"<blockquote expandable>"
        f"**📅 Date**\n"
        f"• Gregorian: {date['gregorian']['date']}\n"
        f"• Hijri: {date['hijri']['date']}\n\n"
        f"**🕰️ Waktu Sholat**\n"
        f"• Imsak: {timings['Imsak']}\n"
        f"• Subuh: {timings['Fajr']}\n"
        f"• Syuruq: {timings['Sunrise']}\n"
        f"• Dzuhur: {timings['Dhuhr']}\n"
        f"• Ashar: {timings['Asr']}\n"
        f"• Maghrib: {timings['Maghrib']}\n"
        f"• Isya: {timings['Isha']}\n\n"
        f"**🌍 Lokasi**\n"
        f"• Kota: {city.title()}, {country.title()}\n"
        f"• Timezone: {meta['timezone']}\n"
        f"• Metode: {meta['method']['name']}"
        f"</blockquote>"
    )

    await proses.edit(f"<blockquote>{msg}</blockquote>")