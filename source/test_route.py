from aiogram.types import Message

from core.aiogram_wrapper.extensions import ExtensionRouter, command


class TestExtensionRoute(ExtensionRouter):
    @command()
    async def ext(self, message: Message):
        return message.text

