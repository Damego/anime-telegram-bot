from os import environ

from aiogram.types import Message
import anilibria
from dotenv import load_dotenv

from core.database.client import PostgreClient
from core import AiogramClient
from core.parsers.parser import Parser
from utils.responses import title_episode_text
from utils.utils import build_chrome_driver

load_dotenv()


client = AiogramClient()
anilibria_client = anilibria.AniLibriaClient()

# webdriver = build_chrome_driver()
# manga = Parser(webdriver, "mangalib.me")
# ranobe = Parser(webdriver, "ranobelib.me")

postgres = PostgreClient(
    host=environ["HOST"],
    user=environ["USER"],
    password=environ["PASSWORD"]
)

@anilibria_client.event()
async def on_title_episode(event: anilibria.TitleEpisode):
    await client.bot.send_message(724170445, title_episode_text(event))


@anilibria_client.event()
async def on_playlist_update(event: anilibria.PlaylistUpdate):
    title = await anilibria_client.get_title(event.id)
    print(title.names.ru)


@anilibria_client.event()
async def on_connect():
    print("Connected to anilibria api")


@client.command()
async def manga(message: Message):
    raw = message.text.split(maxsplit=1)
    if len(raw) == 1:
        return await message.reply("Вы не указали название манги")

    _, name = raw

    data = manga.get_title(name)
    await message.reply(data.name)


@client.command()
async def db(message: Message):
    await postgres.connect()
    await postgres.create_tables()


if __name__ == "__main__":
    anilibria_client.startwith(
        client.astart(environ["TOKEN"])
    )