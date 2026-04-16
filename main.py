import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineQueryResultAudio
from aiogram.enums import ParseMode

from deezer import Client as DeezerClient

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Initialize Deezer client
deezer_client = DeezerClient()

async def search_deezer(query):
    try:
        tracks = deezer_client.search(query)
        return [{\'title\': track.title, \'artist\': track.artist.name, \'preview\': track.preview, \'duration\': track.duration} for track in tracks[:5]]
    except Exception as e:
        logging.error(f"Error searching Deezer: {e}")
        return []

async def register_user(user_id):
    with open("users.txt", "a+") as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def command_start_handler(message: types.Message) -> None:
        await register_user(message.from_user.id)
        await message.answer(f"Hello, {message.from_user.full_name}!\nI am a music bot. Send me the name of a song or artist to search for music.")

    @dp.message()
    async def search_music_handler(message: types.Message) -> None:
        query = message.text
        await message.answer(f"Searching for \'{query}\'...")

        deezer_results = await search_deezer(query)

        if not deezer_results:
            await message.answer("No music found for your query.")
            return

        response_text = "<b>Deezer Results:</b>\n"
        for track in deezer_results:
            response_text += f"- {track[\'artist\']} - {track[\'title\']} (<a href=\\'{track[\'preview\']}\\'>Preview</a>)\n"
        
        await message.answer(response_text)

    @dp.inline_query()
    async def inline_query_handler(inline_query: types.InlineQuery) -> None:
        query = inline_query.query or ""
        if not query:
            await bot.answer_inline_query(inline_query.id, [], cache_time=1)
            return

        deezer_results = await search_deezer(query)

        results = []
        for i, track in enumerate(deezer_results):
            if track[\'preview\']:
                results.append(
                    InlineQueryResultAudio(
                        id=f"deezer_{i}",
                        audio_url=track[\'preview\'],
                        title=f"{track[\'artist\']} - {track[\'title\']}",
                        performer=track[\'artist\'],
                        audio_duration=track[\'duration\']
                    )
                )

        await bot.answer_inline_query(inline_query.id, results, cache_time=1)

    @dp.message(lambda message: message.from_user.id == int(ADMIN_ID), commands=["admin"])
    async def admin_panel(message: types.Message) -> None:
        await message.answer("Welcome to the Admin Panel!\n\nAvailable commands:\n/broadcast <message> - Send a message to all users.")

    @dp.message(lambda message: message.from_user.id == int(ADMIN_ID), commands=["broadcast"])
    async def broadcast_message(message: types.Message) -> None:
        if not message.text or len(message.text.split()) < 2:
            await message.answer("Usage: /broadcast <message>")
            return
        
        broadcast_text = message.text.split(None, 1)[1]
        
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
        
        sent_count = 0
        for user_id in users:
            try:
                await bot.send_message(user_id, broadcast_text)
                sent_count += 1
            except Exception as e:
                logging.error(f"Could not send message to user {user_id}: {e}")
        
        await message.answer(f"Broadcast sent to {sent_count} users.")

    # Start the bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
