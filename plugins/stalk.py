from config import API_BOTCHAX
from Navy.helpers import CMD, Emoji, Tools

__MODULES__ = "sᴛᴀʟᴋɪɴɢ"
__HELP__ = """<u>ᴄᴏᴍᴍᴀɴᴅ ʜᴇʟᴘ <b>sᴛᴀʟᴋɪɴɢ</b></u>

<blockquote>❖ᴘᴇʀɪɴᴛᴀʜ ғɪᴛᴜʀ <b>sᴛᴀʟᴋɪɴɢ</b>
    ➢ `{0}stalkig` [ɴᴀᴍᴇ]
    ➢ `{0}stalktt` [ɴᴀᴍᴇ]
    ➢ `{0}stalktw` [ɴᴀᴍᴇ]
    ➢ `{0}stalkyt` [ɴᴀᴍᴇ]</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("stalkig|stalktt|stalktw|stalkyt")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give username without @!.\nExample: `{message.text.split()[0]} ranandam_`**"
        )

    username = message.text.split()[1]
    command = message.command[0].lower()

    args = {
        "stalkig": f"https://api.botcahx.eu.org/api/stalk/ig?username={username}&apikey={API_BOTCHAX}",
        "stalktt": f"https://api.botcahx.eu.org/api/stalk/tt?username={username}&apikey={API_BOTCHAX}",
        "stalktw": f"https://api.botcahx.eu.org/api/stalk/twitter?username={username}&apikey={API_BOTCHAX}",
        "stalkyt": f"https://api.botcahx.eu.org/api/stalk/yt?username={username}&apikey={API_BOTCHAX}",
    }

    try:
        response = await Tools.fetch.get(args[command])
        data = response.json()
        result = data["result"]
        if command == "stalkig":
            photo = result["photoUrl"]
            text = f"""
**Instagram Stalking Results**

**Full Name:** {result['fullName']}
**Username:** {result['username']}
**Bio:** {result['bio']}
**Followers:** {result['followers']}
**Following:** {result['following']}
**Posts:** {result['postsCount']}
"""

        elif command == "stalktt":

            photo = result["profile"]
            text = f"""
**TikTok Stalking Results**

**Username:** {result['username']}
**Bio:** {result['description']}
**Likes:** {result['likes']}
**Followers:** {result['followers']}
**Following:** {result['following']}
**Total post:** {result['totalPosts']}
"""

        elif command == "stalktw":
            photo = result["profileImage"]
            text = f"""
**Twitter Stalking Results**

**Full Name:** {result['fullName']}
**Username:** @{result['username']}
**Bio:** {result['bio']}
**Followers:** {result['follower']}
**Following:** {result['following']}
**Total post:** {result['totalPosts']}
**Created at:** {result['createdAt']}
"""

        elif command == "stalkyt":
            channel = result["data"][0]
            photo = channel["avatar"]

            text = f"""
**YouTube Stalking Results**
**Channel Name:** {channel['channelName']}
**Verified:** {channel['isVerified']}
**Subscribers:** {channel['subscriberH']}
**Channel URL:** {channel['url']}
**Description:** {channel.get('description', 'Not available')}
"""
        await message.reply_photo(photo, caption=text)

    except Exception as e:
        await message.reply(f"{em.gagal}**Error: {str(e)}**")
    return await proses.delete()
