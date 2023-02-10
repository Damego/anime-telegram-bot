from os import environ
import re

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import anilibria
from dotenv import load_dotenv

from core.aiogram_wrapper import AiogramClient
from core.parsers.parser import Parser
from utils.responses import title_episode_text
from utils.utils import build_chrome_driver
from core.tasks import create_task
from database.client import PostgreClient

load_dotenv()

callback_pattern = re.compile(r"(un)?subscribe\|(anime|manga|ranobe)\|[0-9a-z]+")

client = AiogramClient()
anilibria_client = anilibria.AniLibriaClient()

# webdriver = build_chrome_driver()
# manga = Parser(webdriver, "mangalib.me")
# ranobe = Parser(webdriver, "ranobelib.me")

postgres = PostgreClient(
    host=environ["HOST"],
    user=environ["LOGIN"],
    password=environ["PASSWORD"]
)


@anilibria_client.event()
async def on_connect(connect: anilibria.Connect):
    print(f"Connected to anilibria api {connect.api_version}")


@client.dispatcher.startup()
async def on_startup():
    print("telegram bot started")
    await postgres.connect()
    # await postgres.create_tables()


@anilibria_client.listen
async def on_title_episode(event: anilibria.TitleEpisode):
    await client.bot.send_message(724170445, title_episode_text(event))


@client.command("search_anime", aliases=["поиск_аниме", "sa", "па"])
async def search_anime(message: Message, name: str):
    response = await anilibria_client.search_titles(
        name,
        remove=["player.list", "torrents"]
    )
    if not response.list:
        return "Ничего не найдено"

    anime = response.list[0]

    text = (
        f"*{anime.names.ru}* \n"
        f"Количество серий: {anime.player.episodes.last} / {anime.type.episodes} \n"
        f"[Постер]({anime.posters.small.full_url})"
    )

    # TODO:
    #   1. Добавить проверку, что чел уже подписан, и он не может подписаться ещё раз
    #   2. Если подписан, вывести кнопку для отписки

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться", callback_data=f"subscribe|anime|{anime.code}")]
        ]
    )

    await message.reply(text, reply_markup=keyboard)


@client.dispatcher.callback_query()
async def on_callback(query: CallbackQuery):
    if not callback_pattern.match(query.data):
        return

    action: str
    type: str
    code: str
    action, type, code = query.data.split("|")

    if action == "subscribe":
        await postgres.subscribe(type, query.from_user.id, code)
        await query.answer("Вы успешно подписались")
    else:
        await postgres.unsubscribe(type, query.from_user.id, code)
        await query.answer("Вы успешно отписались")


@client.command()
async def test(message: Message):
    print(await postgres.get_all_codes("anime"))
    



@client.command()
async def search_manga(message: Message, name: str):
    ...


@client.command("search-ranobe")
async def search_ranobe(message: Message, name: str):
    ...


if __name__ == "__main__":
    client.start(environ["TOKEN"])
    # anilibria_client.startwith(
    #     client.astart(environ["TOKEN"])
    # )