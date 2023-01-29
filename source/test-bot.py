from os import environ

import aiogram.types
import anilibria
from dotenv import load_dotenv

from core import AiogramClient
from core.parsers.parser import Parser
from utils.responses import on_title_episode
from utils.utils import build_chrome_driver

load_dotenv()


client = AiogramClient()
anilibria_client = anilibria.AniLibriaClient()

webdriver = build_chrome_driver()
manga = Parser(webdriver, "mangalib.me")
ranobe = Parser(webdriver, "ranobelib.me")


@anilibria_client.event()
async def on_title_episode(event: anilibria.TitleEpisode):
    await client.bot.send_message(724170445, on_title_episode(event))


@anilibria_client.event()
async def on_connect():
    print("Connected to anilibria api")


@client.command()
async def manga(message: aiogram.types.Message):
    raw = message.text.split(maxsplit=1)
    if len(raw) == 1:
        return await message.reply("Вы не указали название манги")

    _, name = raw

    data = manga.get_title(name)
    await message.reply(data.name)


if __name__ == "__main__":
    anilibria_client.startwith(
        client.astart(environ["TOKEN"])
    )