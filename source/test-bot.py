from os import environ

import aiogram.types
import anilibria
from dotenv import load_dotenv

from core import AiogramBot

load_dotenv()


bot = AiogramBot()
anilibria_client = anilibria.AniLibriaClient()


@bot.command()
async def random_title(message: aiogram.types.Message):
    title = await anilibria_client.get_random_title()
    await message.reply(title.names.ru)


if __name__ == "__main__":
    bot.start(environ["TOKEN"])