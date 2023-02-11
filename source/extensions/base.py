from source.core.aiogram_wrapper.extensions import ExtensionRouter as ER
from source.database.client import PostgreClient


class ExtensionRouter(ER):
    postgres: PostgreClient

    def __new__(cls, client, postgres: PostgreClient, *args, **kwargs):
        self = super().__new__(cls, client, *args, **kwargs)
        self.postgres = postgres

        return self
