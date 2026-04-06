import os
from io import BytesIO

import aiofiles
import aiohttp

from config import BOT_NAME

from .tools import Tools


class QuotlyException(Exception):
    pass


class Quotly:
    GAMBAR_KONTOL = """
⣠⡶⠚⠛⠲⢄⡀
⣼⠁ ⠀⠀⠀ ⠳⢤⣄
⢿⠀⢧⡀⠀⠀⠀⠀⠀⢈⡇
⠈⠳⣼⡙⠒⠶⠶⠖⠚⠉⠳⣄
⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄
⠀⠀⠀⠘⣆ ⠀⠀⠀⠀ ⠀⠈⠓⢦⣀
⠀⠀⠀⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠲⢤
⠀⠀⠀⠀⠀⠀⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧
⠀⠀⠀⠀⠀⠀⠀⡴⠋⠓⠦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠈⣇
⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄
⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⢹⡄⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃
⠀⠀⠀⠀⠀⠀⠀⠙⢦⣀⣳⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⢦⣀⣀⣀⣀⣠⡴⠚⠉
"""

    GAMBAR_TITIT = """
😋😋
😋😋😋
  😋😋😋
    😋😋😋
     😋😋😋
       😋😋😋
        😋😋😋
         😋😋😋
          😋😋😋
          😋😋😋
      😋😋😋😋
 😋😋😋😋😋😋
 😋😋😋  😋😋😋
    😋😋       😋😋
"""
    loanjing = [
        "White",
        "Navy",
        "DarkBlue",
        "MediumBlue",
        "Blue",
        "DarkGreen",
        "Green",
        "Teal",
        "DarkCyan",
        "DeepSkyBlue",
        "DarkTurquoise",
        "MediumSpringGreen",
        "Lime",
        "SpringGreen",
        "Aqua",
        "Cyan",
        "MidnightBlue",
        "DodgerBlue",
        "LightSeaGreen",
        "ForestGreen",
        "SeaGreen",
        "DarkSlateGray",
        "DarkSlateGrey",
        "LimeGreen",
        "MediumSeaGreen",
        "Turquoise",
        "RoyalBlue",
        "SteelBlue",
        "DarkSlateBlue",
        "MediumTurquoise",
        "Indigo  ",
        "DarkOliveGreen",
        "CadetBlue",
        "CornflowerBlue",
        "RebeccaPurple",
        "MediumAquaMarine",
        "DimGray",
        "DimGrey",
        "SlateBlue",
        "OliveDrab",
        "SlateGray",
        "SlateGrey",
        "LightSlateGray",
        "LightSlateGrey",
        "MediumSlateBlue",
        "LawnGreen",
        "Chartreuse",
        "Aquamarine",
        "Maroon",
        "Purple",
        "Olive",
        "Gray",
        "Grey",
        "SkyBlue",
        "LightSkyBlue",
        "BlueViolet",
        "DarkRed",
        "DarkMagenta",
        "SaddleBrown",
        "DarkSeaGreen",
        "LightGreen",
        "MediumPurple",
        "DarkViolet",
        "PaleGreen",
        "DarkOrchid",
        "YellowGreen",
        "Sienna",
        "Brown",
        "DarkGray",
        "DarkGrey",
        "LightBlue",
        "GreenYellow",
        "PaleTurquoise",
        "LightSteelBlue",
        "PowderBlue",
        "FireBrick",
        "DarkGoldenRod",
        "MediumOrchid",
        "RosyBrown",
        "DarkKhaki",
        "Silver",
        "MediumVioletRed",
        "IndianRed ",
        "Peru",
        "Chocolate",
        "Tan",
        "LightGray",
        "LightGrey",
        "Thistle",
        "Orchid",
        "GoldenRod",
        "PaleVioletRed",
        "Crimson",
        "Gainsboro",
        "Plum",
        "BurlyWood",
        "LightCyan",
        "Lavender",
        "DarkSalmon",
        "Violet",
        "PaleGoldenRod",
        "LightCoral",
        "Khaki",
        "AliceBlue",
        "HoneyDew",
        "Azure",
        "SandyBrown",
        "Wheat",
        "Beige",
        "WhiteSmoke",
        "MintCream",
        "GhostWhite",
        "Salmon",
        "AntiqueWhite",
        "Linen",
        "LightGoldenRodYellow",
        "OldLace",
        "Red",
        "Fuchsia",
        "Magenta",
        "DeepPink",
        "OrangeRed",
        "Tomato",
        "HotPink",
        "Coral",
        "DarkOrange",
        "LightSalmon",
        "Orange",
        "LightPink",
        "Pink",
        "Gold",
        "PeachPuff",
        "NavajoWhite",
        "Moccasin",
        "Bisque",
        "MistyRose",
        "BlanchedAlmond",
        "PapayaWhip",
        "LavenderBlush",
        "SeaShell",
        "Cornsilk",
        "LemonChiffon",
        "FloralWhite",
        "Snow",
        "Yellow",
        "LightYellow",
        "Ivory",
        "Black",
    ]

    async def get_sender(message):
        if message.forward_date:
            if message.forward_sender_name:
                return 1
            elif message.forward_from:
                return message.forward_from.id
            elif message.forward_from_chat:
                return message.forward_from_chat.id
            else:
                return 1
        elif message.from_user:
            return message.from_user.id
        elif message.sender_chat:
            return message.sender_chat.id
        else:
            return 1

    async def sender_name(message):
        if message.forward_date:
            if message.forward_sender_name:
                return message.forward_sender_name
            elif message.forward_from:
                return (
                    f"{message.forward_from.first_name} {message.forward_from.last_name or ''}"
                    if message.forward_from.last_name
                    else message.forward_from.first_name
                )

            elif message.forward_from_chat:
                return message.forward_from_chat.title
            else:
                return ""
        elif message.from_user:
            if message.from_user.last_name:
                return f"{message.from_user.first_name} {message.from_user.last_name or ''}"
            else:
                return message.from_user.first_name
        elif message.sender_chat:
            return message.sender_chat.title
        else:
            return ""

    async def sender_emoji(message):
        if message.forward_date:
            return (
                ""
                if message.forward_sender_name
                or not message.forward_from
                and message.forward_from_chat
                or not message.forward_from
                else message.forward_from.emoji_status.custom_emoji_id
            )

        return (
            message.from_user.emoji_status.custom_emoji_id if message.from_user else ""
        )

    async def sender_username(message):
        if message.forward_date:
            if (
                not message.forward_sender_name
                and not message.forward_from
                and message.forward_from_chat
                and message.forward_from_chat.username
            ):
                return message.forward_from_chat.username
            elif (
                not message.forward_sender_name
                and not message.forward_from
                and message.forward_from_chat
                or message.forward_sender_name
                or not message.forward_from
            ):
                return ""
            else:
                return message.forward_from.username or ""
        elif message.from_user and message.from_user.username:
            return message.from_user.username
        elif (
            message.from_user
            or message.sender_chat
            and not message.sender_chat.username
            or not message.sender_chat
        ):
            return ""
        else:
            return message.sender_chat.username

    async def sender_photo(message):
        if message.forward_date:
            if (
                not message.forward_sender_name
                and not message.forward_from
                and message.forward_from_chat
                and message.forward_from_chat.photo
            ):
                return {
                    "small_file_id": message.forward_from_chat.photo.small_file_id,
                    "small_photo_unique_id": message.forward_from_chat.photo.small_photo_unique_id,
                    "big_file_id": message.forward_from_chat.photo.big_file_id,
                    "big_photo_unique_id": message.forward_from_chat.photo.big_photo_unique_id,
                }
            elif (
                not message.forward_sender_name
                and not message.forward_from
                and message.forward_from_chat
                or message.forward_sender_name
                or not message.forward_from
            ):
                return ""
            else:
                return (
                    {
                        "small_file_id": message.forward_from.photo.small_file_id,
                        "small_photo_unique_id": message.forward_from.photo.small_photo_unique_id,
                        "big_file_id": message.forward_from.photo.big_file_id,
                        "big_photo_unique_id": message.forward_from.photo.big_photo_unique_id,
                    }
                    if message.forward_from.photo
                    else ""
                )

        elif message.from_user and message.from_user.photo:
            return {
                "small_file_id": message.from_user.photo.small_file_id,
                "small_photo_unique_id": message.from_user.photo.small_photo_unique_id,
                "big_file_id": message.from_user.photo.big_file_id,
                "big_photo_unique_id": message.from_user.photo.big_photo_unique_id,
            }
        elif (
            message.from_user
            or message.sender_chat
            and not message.sender_chat.photo
            or not message.sender_chat
        ):
            return ""
        else:
            return {
                "small_file_id": message.sender_chat.photo.small_file_id,
                "small_photo_unique_id": message.sender_chat.photo.small_photo_unique_id,
                "big_file_id": message.sender_chat.photo.big_file_id,
                "big_photo_unique_id": message.sender_chat.photo.big_photo_unique_id,
            }

    async def t_or_c(message):
        if message.text:
            return message.text
        elif message.caption:
            return message.caption
        else:
            return ""

    async def quotly(messages, kolor, is_reply):
        if not isinstance(messages, list):
            messages = [messages]
        payload = {
            "type": "quote",
            "format": "png",
            "backgroundColor": kolor,
            "messages": [],
        }
        # payload = {
        #    "type": "quote",
        #    "format": "webp",
        #    "backgroundColor": kolor,
        #    "messages": [],
        # }

        for message in messages:
            m_dict = {}
            if message.entities:
                m_dict["entities"] = [
                    {
                        "type": entity.type.name.lower(),
                        "offset": entity.offset,
                        "length": entity.length,
                    }
                    for entity in message.entities
                ]
            elif message.caption_entities:
                m_dict["entities"] = [
                    {
                        "type": entity.type.name.lower(),
                        "offset": entity.offset,
                        "length": entity.length,
                    }
                    for entity in message.caption_entities
                ]
            else:
                m_dict["entities"] = []
            m_dict["chatId"] = await Quotly.get_sender(message)
            m_dict["text"] = await Quotly.t_or_c(message)
            m_dict["avatar"] = True
            m_dict["from"] = {}
            m_dict["from"]["id"] = await Quotly.get_sender(message)
            m_dict["from"]["name"] = await Quotly.sender_name(message)
            m_dict["from"]["username"] = await Quotly.sender_username(message)
            m_dict["from"]["type"] = message.chat.type.name.lower()
            m_dict["from"]["photo"] = await Quotly.sender_photo(message)
            if message.reply_to_message and is_reply:
                m_dict["replyMessage"] = {
                    "name": await Quotly.sender_name(message.reply_to_message),
                    "text": await Quotly.t_or_c(message.reply_to_message),
                    "chatId": await Quotly.get_sender(message.reply_to_message),
                }
            else:
                m_dict["replyMessage"] = {}
            payload["messages"].append(m_dict)
        APIS = [
            "https://bot.lyo.su/quote/generate.png",
            "https://quotly.netorare.codes/generate",
            "https://btzqc.betabotz.eu.org/generate",
            "https://api.ryzumi.vip/api/image/quotly",
        ]

        last_error = None

        for api in APIS:
            try:
                r = await Tools.fetch.post(api, json=payload)

                if r.status_code == 200 and r.content:
                    print(f"[QUOTLY] SUCCESS via {api}")
                    return r.read()

                try:
                    last_error = r.json()
                except Exception:
                    last_error = {
                        "status": r.status_code,
                        "message": "Quotly API returned non-JSON response",
                        "raw": r.text[:300]
                    }

            except Exception as e:
                last_error = {
                    "error": str(e),
                    "api": api
                }
                continue

        raise QuotlyException(last_error)

    @staticmethod
    def isArgInt(txt) -> list:
        count = txt
        try:
            count = int(count)
            return [True, count]
        except ValueError:
            return [False, 0]

    @staticmethod
    async def make_carbonara(
        code: str, bg_color: str, theme: str, language: str
    ) -> BytesIO:
        url = "https://carbonara.solopov.dev/api/cook"
        json_data = {
            "code": code,
            "paddingVertical": "56px",
            "paddingHorizontal": "56px",
            "backgroundMode": "color",
            "backgroundColor": bg_color,
            "theme": theme,
            "language": language,
            "fontFamily": "Cascadia Code",
            "fontSize": "14px",
            "windowControls": True,
            "widthAdjustment": True,
            "lineNumbers": True,
            "firstLineNumber": 1,
            "name": f"{BOT_NAME}-Carbon",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as resp:
                return BytesIO(await resp.read())

    @staticmethod
    async def get_message_content(message):
        if message.text:
            return message.text, "text"
        elif message.document:
            doc = await message.download()
            async with aiofiles.open(doc, mode="r") as f:
                content = await f.read()
            os.remove(doc)
            return content, "document"
        return None, None
