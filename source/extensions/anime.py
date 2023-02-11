import re

import anilibria
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from .base import ExtensionRouter
from source.utils.responses import title_episode_text
from source.utils.text_processing import prepare_markdown_text
from source.core.aiogram_wrapper import command, callback_query

callback_pattern = re.compile(r"(un)?subscribe\|(anime|manga|ranobe)")
single_title_pattern = re.compile(r"Код: [0-9a-z-_]+")
select_anime_callback_pattern = re.compile(r"select\|anime\|[0-9]+")
select_anime_text_pattern = re.compile(r"\*[0-9]+\* [0-9a-z-_]+")


class AnimeRouter(ExtensionRouter):
    def __init__(
        self,
        client,
        postgres,
        anilibria_client
    ):
        self.client = client
        self.postgres = postgres
        self.anilibria_client: anilibria.AniLibriaClient = anilibria_client

        self.anilibria_client.listen(self.on_title_episode)

    async def on_title_episode(self, event: anilibria.TitleEpisode):
        users = await self.postgres.get_users_from_code("anime", event.title.code)

        for user in users:
            await self.client.bot.send_message(user[0], title_episode_text(event))

    @command(aliases=["поиск_аниме", "sa", "па"])
    async def search_anime(self, message: Message, name: str):
        response = await self.anilibria_client.search_titles(
            name,
            remove=["player.list", "torrents"],
            items_per_page=8
        )
        if not response.list:
            return "Ничего не найдено"

        if len(response.list) == 1:
            return await self.process_single_anime_title(message, message.from_user.id, response.list[0])

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

    async def process_single_anime_title(self, message: Message, user_id: int, title: anilibria.Title):
        code = prepare_markdown_text(title.code)

        total_episodes = f"/ {episodes}" if (episodes := title.type.episodes) else ""

        text = (
            f"*{prepare_markdown_text(title.names.ru)}* \n"
            f"Количество серий: {title.player.episodes.last} {total_episodes} \n"
            f"[Постер]({title.posters.small.full_url}) \n"
            f"Код: {code}"
        )

        entry = await self.postgres.get_subscription_entry("anime", user_id, title.code)
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

    @callback_query()
    async def callback_handler(self, query: CallbackQuery):
        if select_anime_callback_pattern.match(query.data):
            return await self.select_anime_title(query)
        elif callback_pattern.match(query.data):
            return await self.subscribe_title(query)

    async def select_anime_title(self, query: CallbackQuery):
        _, _, title_id = query.data.split("|")

        title = await self.anilibria_client.get_title(id=int(title_id))
        await self.process_single_anime_title(query.message, query.from_user.id, title)

    async def subscribe_title(self, query: CallbackQuery):
        action: str
        title_type: str
        action, title_type = query.data.split("|")

        matches = single_title_pattern.findall(query.message.text)
        if not matches:
            return await query.answer("Ошибка в коде")
        code: str = matches[0][5:]

        is_subscribed = await self.postgres.get_subscription_entry(title_type, query.from_user.id, code)

        if action == "subscribe":
            if is_subscribed:
                return await query.answer("Вы уже подписаны на данный тайтл")

            await self.postgres.subscribe(title_type, query.from_user.id, code)
            await query.answer("Вы успешно подписались")
        else:
            if not is_subscribed:
                return await query.answer("Вы уже отписаны от данного тайтла")

            await self.postgres.unsubscribe(title_type, query.from_user.id, code)
            await query.answer("Вы успешно отписались")

