import os

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import functions, types

import localsettings


akks = localsettings.akks
choosen_akk = localsettings.current_akk


# Your API ID and API Hash obtained from my.telegram.org
api_id = akks[choosen_akk][0]  # Example: 123456
api_hash = akks[choosen_akk][1]  # Example: 'abcdef1234567890abcdef1234567890'


# Optional: You can store the session as a string or a file (for reusing sessions).
# Use StringSession or just the filename for a file session.
session_file = choosen_akk  # Session file will be created (anon.session)
client = TelegramClient(session_file, api_id, api_hash)


async def __get_bot_webapp_url(bot_username, app_url):
    # Check if the session file exists, otherwise prompt for phone number
    if not os.path.exists(f"{session_file}.session"):
        print("Session not found, starting new session...")

        # Initiating login flow
        await client.start()

        # Save the session string to reuse it next time
        session_string = StringSession.save(client.session)
        print(f"Your session string: {session_string}")
    else:
        print("Session found, logging in...")

    # After logging in, print your information
    me = await client.get_me()
    print(f"Logged in as {me.first_name} ({me.id})")

    # start bot here

    # dialog = None
    # async for dialog in client.iter_dialogs():
    #     try:
    #         dialog_user = dialog.entity.username
    #         if dialog_user == bot_username:
    #             break
    #     except:
    #         continue

    # if dialog.entity.username == bot_username:
    #     print(f"Found bot: {dialog.entity.username} - {dialog.name}")

    bot = await client.get_entity(bot_username)
    result = await client(
        functions.messages.RequestWebViewRequest(
            bot=types.InputUser(user_id=bot.id, access_hash=bot.access_hash),
            peer=types.InputPeerUser(user_id=bot.id, access_hash=bot.access_hash),
            platform="android",
            from_bot_menu="YES",
            url=app_url,
        )
    )
    return result.url


def get_bot_webapp_url(bot_username, app_url):
    with client:
        url = client.loop.run_until_complete(
            __get_bot_webapp_url(bot_username, app_url)
        )
    print(f"Got app url: {url}")
    return url
