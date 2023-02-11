from os import environ

import anilibria
from aiogram.types import Message
from core.aiogram_wrapper import AiogramClient
from database.client import PostgreClient
from dotenv import load_dotenv
from extensions.anime import AnimeRouter

load_dotenv()

postgres = PostgreClient(host=environ["HOST"], user=environ["LOGIN"], password=environ["PASSWORD"])


client = AiogramClient()
anilibria_client = anilibria.AniLibriaClient()

AnimeRouter(client, postgres, anilibria_client)

# webdriver = build_chrome_driver()
# manga = Parser(webdriver, "mangalib.me")
# ranobe = Parser(webdriver, "ranobelib.me")


@client.dispatcher.startup()
async def on_startup():
    print("telegram bot started")
    await postgres.connect()
    # await postgres.create_tables()


@client.command()
async def search_manga(message: Message, name: str):
    ...


@client.command("search-ranobe")
async def search_ranobe(message: Message, name: str):
    ...


if __name__ == "__main__":
    # client.start(environ["TOKEN"])
    anilibria_client.startwith(client.astart(environ["TOKEN"]))
