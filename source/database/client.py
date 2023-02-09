import asyncpg


class PostgreClient:
    def __init__(self, *, host: str, port: int = 5432, user: str, password: str):
        self._host = host
        self._user = user
        self._port = port
        self._password = password

        self.connection: asyncpg.Connection = None  # type: ignore

    async def connect(self):
        self.connection = await asyncpg.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database="anime-telegram-bot-db"
        )

    async def create_tables(self):
        await self.connection.execute(
            """
            CREATE TABLE anime(
                user_id INT NOT NULL,
                anime_code varchar(255) NOT NULL
            )
            """
        )
        await self.connection.execute(
            """
            CREATE TABLE manga(
                user_id INT NOT NULL,
                manga_code varchar(255) NOT NULL,
                chapter varchar(50) NOT NULL
            )
            """
        )
        await self.connection.execute(
            """
            CREATE TABLE ranobe(
                user_id INT NOT NULL,
                ranobe_code varchar(255) NOT NULL,
                chapter varchar(50) NOT NULL
            )
            """
        )