# manobe - manga & ranobe

from aiogram.types import Message

from source.core.aiogram_wrapper import command
from source.core.parsers import Parser
from source.core.tasks import create_task
from source.utils.text_processing import prepare_markdown_text

from .base import ExtensionRouter


class Manobe(ExtensionRouter):
    def __init__(self, *args):
        self.manga = Parser("mangalib.me")
        self.ranobe = Parser("ranobelib.me")

        self._task.start(self)

    @create_task(6 * 60 * 60)  # One time per 6 hours
    async def _task(self):
        print("ping")

    @command(aliases=["sm"])
    async def search_manga(self, message: Message, name: str):
        title = await self.manga.get_title_async(name)
        if title:
            await message.answer(prepare_markdown_text(f"{title.name}\n{title.image_url}"))

    @command(aliases=["sr"])
    async def search_ranobe(self, message: Message, name: str):
        title = await self.ranobe.get_title_async(name)
        if title:
            await message.answer(prepare_markdown_text(f"{title.name}\n{title.image_url}"))
