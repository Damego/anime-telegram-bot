from os import environ
import re

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import anilibria
from dotenv import load_dotenv

from core.aiogram_wrapper import AiogramClient
from core.parsers.parser import Parser
from utils.responses import title_episode_text
from utils.webdriver_utils import build_chrome_driver
from utils.text_processing import prepare_markdown_text
from core.tasks import create_task
from database.client import PostgreClient

load_dotenv()

callback_pattern = re.compile(r"(un)?subscribe\|(anime|manga|ranobe)")
single_title_pattern = re.compile(r"Код: [0-9a-z-_]+")
select_anime_callback_pattern = re.compile(r"select\|anime\|[0-9]+")
select_anime_text_pattern = re.compile(r"\*[0-9]+\* [0-9a-z-_]+")

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
    await postgres.create_tables()


@anilibria_client.listen
async def on_title_episode(event: anilibria.TitleEpisode):
    users = await postgres.get_users_from_code("anime", event.title.code)

    for user in users:
        await client.bot.send_message(user[0], title_episode_text(event))


@client.command("search_anime", aliases=["поиск_аниме", "sa", "па"])
async def search_anime(message: Message, name: str):
    response = await anilibria_client.search_titles(
        name,
        remove=["player.list", "torrents"],
        items_per_page=8
    )
    if not response.list:
        return "Ничего не найдено"

    if len(response.list) == 1:
        return await process_single_anime_title(message, message.from_user.id, response.list[0])

    text = f"Поиск: {name} \n\n"
    buttons = []

    for counter, title in enumerate(response.list, start=1):
        text += f"*{counter}* {prepare_markdown_text(title.names.ru)} \n"
        buttons.append(
            [InlineKeyboardButton(text=title.names.ru, callback_data=f"select|anime|{title.id}")]
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    await message.reply(text, reply_markup=keyboard)


async def process_single_anime_title(message: Message, user_id: int, title: anilibria.Title):
    code = prepare_markdown_text(title.code)

    total_episodes = f"/ {episodes}" if (episodes := title.type.episodes) else ""

    text = (
        f"*{prepare_markdown_text(title.names.ru)}* \n"
        f"Количество серий: {title.player.episodes.last} {total_episodes} \n"
        f"[Постер]({title.posters.small.full_url}) \n"
        f"Код: {code}"
    )

    entry = await postgres.get_subscription_entry("anime", user_id, title.code)
    if entry:
        button_text = "Отписаться"
        callback_data = f"unsubscribe|anime"
    else:
        button_text = "Подписаться"
        callback_data = f"subscribe|anime"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button_text, callback_data=callback_data)]
        ]
    )

    await message.answer(text, reply_markup=keyboard)


@client.dispatcher.callback_query()
async def callback_handler(query: CallbackQuery):
    if select_anime_callback_pattern.match(query.data):
        return await select_anime_title(query)
    elif callback_pattern.match(query.data):
        return await subscribe_title(query)


async def select_anime_title(query: CallbackQuery):
    _, _, title_id = query.data.split("|")

    title = await anilibria_client.get_title(id=int(title_id))
    await process_single_anime_title(query.message, query.from_user.id, title)


@client.dispatcher.callback_query()
async def subscribe_title(query: CallbackQuery):
    action: str
    title_type: str
    action, title_type = query.data.split("|")

    matches = single_title_pattern.findall(query.message.text)
    if not matches:
        return await query.answer("Ошибка в коде")
    code: str = matches[0][5:]

    if action == "subscribe":
        if await postgres.get_subscription_entry(title_type, query.from_user.id, code):
            return await query.answer("Вы уже подписаны на данный тайтл")

        await postgres.subscribe(title_type, query.from_user.id, code)
        await query.answer("Вы успешно подписались")
    else:
        if not await postgres.get_subscription_entry(title_type, query.from_user.id, code):
            return await query.answer("Вы уже отписаны от данного тайтла")

        await postgres.unsubscribe(title_type, query.from_user.id, code)
        await query.answer("Вы успешно отписались")


@client.command()
async def search_manga(message: Message, name: str):
    ...


@client.command("search-ranobe")
async def search_ranobe(message: Message, name: str):
    ...


if __name__ == "__main__":
    # client.start(environ["TOKEN"])
    anilibria_client.startwith(
        client.astart(environ["TOKEN"])
    )